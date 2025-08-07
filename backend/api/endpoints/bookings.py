from fastapi import APIRouter, HTTPException, Request, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, Dict, Any
import httpx
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import os

router = APIRouter()

# Configuration
CALENDLY_WEBHOOK_SECRET = os.getenv("CALENDLY_WEBHOOK_SECRET", "your_webhook_secret")
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME", "your_email@gmail.com")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "your_app_password")
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "dennismutugi@gmail.com")

# Calendly Configuration
CALENDLY_USER_URI = os.getenv("CALENDLY_USER_URI", "https://api.calendly.com/users/BHHFOOHJUJ6X6Q4F")
CALENDLY_ORG_URI = os.getenv("CALENDLY_ORG_URI", "https://api.calendly.com/organizations/BCDBKJHIXYGVFYSX")
CALENDLY_SCHEDULING_URL = os.getenv("CALENDLY_SCHEDULING_URL", "https://calendly.com/boundinbox")

class BookingRequest(BaseModel):
    name: str
    email: str
    company: Optional[str] = None
    message: Optional[str] = None
    calendly_event_uri: Optional[str] = None

class CalendlyWebhook(BaseModel):
    event: str
    payload: Dict[str, Any]

@router.post("/bookings/request")
async def create_booking_request(booking: BookingRequest, background_tasks: BackgroundTasks):
    """Create a new booking request"""
    try:
        # Store booking request (in production, save to database)
        booking_data = {
            "id": f"booking_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "name": booking.name,
            "email": booking.email,
            "company": booking.company,
            "message": booking.message,
            "calendly_event_uri": booking.calendly_event_uri,
            "status": "pending",
            "created_at": datetime.now().isoformat()
        }

        # Send notification email in background
        background_tasks.add_task(send_booking_notification, booking_data)

        return {
            "success": True,
            "message": "Booking request created successfully",
            "booking_id": booking_data["id"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create booking request: {str(e)}")

@router.post("/bookings/calendly-webhook")
async def calendly_webhook(request: Request):
    """Handle Calendly webhook events"""
    try:
        # Verify webhook signature (in production, implement proper verification)
        body = await request.body()
        signature = request.headers.get("calendly-webhook-signature")

        # Parse webhook data
        webhook_data = json.loads(body)
        event_type = webhook_data.get("event")
        payload = webhook_data.get("payload", {})

        print(f"Received Calendly webhook: {event_type}")
        print(f"Payload: {json.dumps(payload, indent=2)}")

        if event_type == "invitee.created":
            await handle_invitee_created(payload)
        elif event_type == "invitee.canceled":
            await handle_invitee_canceled(payload)

        return {"success": True, "message": "Webhook processed successfully"}
    except Exception as e:
        print(f"Error processing Calendly webhook: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to process webhook: {str(e)}")

async def handle_invitee_created(payload: Dict[str, Any]):
    """Handle new invitee creation"""
    try:
        invitee = payload.get("invitee", {})
        event = payload.get("event", {})

        booking_data = {
            "id": f"calendly_{invitee.get('uuid', 'unknown')}",
            "name": invitee.get("name", "Unknown"),
            "email": invitee.get("email", ""),
            "calendly_event_uri": event.get("uri", ""),
            "event_name": event.get("name", "Wakili Demo"),
            "start_time": invitee.get("start_time"),
            "end_time": invitee.get("end_time"),
            "status": "confirmed",
            "created_at": datetime.now().isoformat()
        }

        # Send confirmation emails
        await send_booking_confirmation(booking_data)
        await send_admin_notification(booking_data)

        print(f"Processed new invitee: {booking_data['name']} ({booking_data['email']})")
    except Exception as e:
        print(f"Error handling invitee creation: {str(e)}")

async def handle_invitee_canceled(payload: Dict[str, Any]):
    """Handle invitee cancellation"""
    try:
        invitee = payload.get("invitee", {})
        print(f"Invitee canceled: {invitee.get('name')} ({invitee.get('email')})")

        # Send cancellation notification to admin
        await send_cancellation_notification(invitee)
    except Exception as e:
        print(f"Error handling invitee cancellation: {str(e)}")

async def send_booking_notification(booking_data: Dict[str, Any]):
    """Send booking notification email to admin"""
    try:
        subject = f"New Demo Booking Request - {booking_data['name']}"

        body = f"""
        New demo booking request received:

        Name: {booking_data['name']}
        Email: {booking_data['email']}
        Company: {booking_data.get('company', 'Not specified')}
        Message: {booking_data.get('message', 'No message')}
        Booking ID: {booking_data['id']}
        Created: {booking_data['created_at']}

        Please follow up with the client.
        """

        await send_email(ADMIN_EMAIL, subject, body)
        print(f"Booking notification sent to admin for: {booking_data['name']}")
    except Exception as e:
        print(f"Error sending booking notification: {str(e)}")

async def send_booking_confirmation(booking_data: Dict[str, Any]):
    """Send confirmation email to client"""
    try:
        subject = "Wakili Demo Confirmed - Next Steps"

        body = f"""
        Dear {booking_data['name']},

        Thank you for booking a demo with Wakili A Quick One!

        Your demo has been confirmed for:
        Event: {booking_data['event_name']}
        Date: {booking_data['start_time']}

        What to expect:
        - 30-minute personalized demonstration
        - Live product walkthrough
        - Q&A session with our AI experts
        - Customized solutions for your legal practice

        Please ensure you have:
        - A stable internet connection
        - Your questions ready
        - Any specific use cases you'd like to discuss

        If you need to reschedule, please contact us at {ADMIN_EMAIL}

        We look forward to showing you how Wakili can transform your legal practice!

        Best regards,
        The Wakili Team
        """

        await send_email(booking_data['email'], subject, body)
        print(f"Confirmation email sent to: {booking_data['email']}")
    except Exception as e:
        print(f"Error sending confirmation email: {str(e)}")

async def send_admin_notification(booking_data: Dict[str, Any]):
    """Send notification to admin about confirmed booking"""
    try:
        subject = f"Demo Confirmed - {booking_data['name']}"

        body = f"""
        Demo booking confirmed:

        Client: {booking_data['name']}
        Email: {booking_data['email']}
        Event: {booking_data['event_name']}
        Date: {booking_data['start_time']}
        Booking ID: {booking_data['id']}

        Please prepare for the demo session.
        """

        await send_email(ADMIN_EMAIL, subject, body)
        print(f"Admin notification sent for confirmed booking: {booking_data['name']}")
    except Exception as e:
        print(f"Error sending admin notification: {str(e)}")

async def send_cancellation_notification(invitee: Dict[str, Any]):
    """Send cancellation notification to admin"""
    try:
        subject = f"Demo Cancelled - {invitee.get('name', 'Unknown')}"

        body = f"""
        Demo booking cancelled:

        Client: {invitee.get('name', 'Unknown')}
        Email: {invitee.get('email', 'Unknown')}
        Cancelled at: {datetime.now().isoformat()}

        Please update your calendar accordingly.
        """

        await send_email(ADMIN_EMAIL, subject, body)
        print(f"Cancellation notification sent for: {invitee.get('name')}")
    except Exception as e:
        print(f"Error sending cancellation notification: {str(e)}")

async def send_email(to_email: str, subject: str, body: str):
    """Send email using SMTP"""
    try:
        msg = MIMEMultipart()
        msg['From'] = SMTP_USERNAME
        msg['To'] = to_email
        msg['Subject'] = subject

        msg.attach(MIMEText(body, 'plain'))

        # In production, use proper async SMTP or email service
        # For now, we'll just log the email
        print(f"EMAIL TO: {to_email}")
        print(f"SUBJECT: {subject}")
        print(f"BODY: {body}")
        print("---")

        # Uncomment below for actual email sending
        # with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        #     server.starttls()
        #     server.login(SMTP_USERNAME, SMTP_PASSWORD)
        #     server.send_message(msg)

    except Exception as e:
        print(f"Error sending email: {str(e)}")

@router.get("/bookings/status")
async def get_booking_status():
    """Get booking system status"""
    return {
        "status": "operational",
        "webhook_endpoint": "/bookings/calendly-webhook",
        "admin_email": ADMIN_EMAIL,
        "timestamp": datetime.now().isoformat()
    }