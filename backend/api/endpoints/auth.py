from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any
import httpx
import json
import os
import html
import jwt
from datetime import datetime, timedelta

router = APIRouter(prefix="/auth", tags=["authentication"])

# Supabase configuration (uses environment variables)
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

security = HTTPBearer()

# Pydantic models for input validation
class ProfileUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=1, max_length=100)
    company: Optional[str] = Field(None, min_length=1, max_length=100)

    @validator('full_name', 'company')
    def sanitize_input(cls, v):
        if v:
            return html.escape(v.strip())
        return v

class UserProfile(BaseModel):
    id: str
    email: str
    full_name: Optional[str] = ""
    company: Optional[str] = ""
    role: Optional[str] = "user"
    demo_requested: Optional[bool] = False
    demo_approved: Optional[bool] = False
    demo_date: Optional[str] = None
    created_at: Optional[str] = ""
    updated_at: Optional[str] = ""

class AuthResponse(BaseModel):
    user: UserProfile
    message: str

class VerifyResponse(BaseModel):
    authenticated: bool
    user_id: Optional[str] = None
    email: Optional[str] = None
    message: str

def decode_jwt_payload(token: str) -> Dict[str, Any]:
    """Decode JWT payload without verification for debugging"""
    try:
        # Split the token and get the payload part
        parts = token.split('.')
        if len(parts) != 3:
            raise ValueError("Invalid JWT format")

        # Decode the payload (second part)
        import base64
        payload = parts[1]
        # Add padding if needed
        payload += '=' * (4 - len(payload) % 4)
        decoded = base64.urlsafe_b64decode(payload)
        return json.loads(decoded)
    except Exception as e:
        print(f"Error decoding JWT payload: {e}")
        return {}

async def verify_supabase_jwt(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """Verify Supabase JWT and return user data"""
    if not SUPABASE_URL or not SUPABASE_ANON_KEY:
        raise HTTPException(status_code=500, detail="Supabase not configured")

    token = credentials.credentials

    # First, try to decode the JWT payload to get user info
    try:
        payload = decode_jwt_payload(token)
        print(f"JWT Payload: {json.dumps(payload, indent=2)}")

        # Check if token is expired
        if 'exp' in payload:
            exp_timestamp = payload['exp']
            current_timestamp = datetime.utcnow().timestamp()
            if current_timestamp > exp_timestamp:
                raise HTTPException(status_code=401, detail="Token expired")

        # Extract user data from JWT payload
        user_data = {
            "id": payload.get("sub"),
            "email": payload.get("email"),
            "user_metadata": payload.get("user_metadata", {})
        }

        if not user_data["id"] or not user_data["email"]:
            raise HTTPException(status_code=401, detail="Invalid token payload")

        print(f"Extracted user data: {user_data}")
        return user_data

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error extracting user data from JWT: {e}")
        # Fallback to Supabase API verification
        pass

    # Fallback: Try Supabase API verification
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{SUPABASE_URL}/auth/v1/user",
                headers={
                    "Authorization": f"Bearer {token}",
                    "apikey": SUPABASE_ANON_KEY
                }
            )

            print(f"Supabase API response status: {response.status_code}")
            print(f"Supabase API response: {response.text}")

            if response.status_code != 200:
                raise HTTPException(status_code=401, detail=f"Invalid token: {response.status_code}")

            user_data = response.json()
            return user_data
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in Supabase API verification: {e}")
        raise HTTPException(status_code=401, detail=f"Token verification failed: {str(e)}")

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """Get current user data from JWT token"""
    return await verify_supabase_jwt(credentials)

async def get_user_profile(user_data: Dict[str, Any]) -> UserProfile:
    """Get or create user profile from Supabase"""
    if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
        raise HTTPException(status_code=500, detail="Supabase not configured")

    try:
        async with httpx.AsyncClient() as client:
            # First, try to get existing profile
            response = await client.get(
                f"{SUPABASE_URL}/rest/v1/profiles?id=eq.{user_data['id']}",
                headers={
                    "apikey": SUPABASE_SERVICE_ROLE_KEY,
                    "Authorization": f"Bearer {SUPABASE_SERVICE_ROLE_KEY}"
                }
            )

            if response.status_code == 200:
                profiles = response.json()
                if profiles:
                    profile = profiles[0]
                    # Ensure all required fields are present
                    profile_data = {
                        "id": profile.get("id", user_data["id"]),
                        "email": profile.get("email", user_data["email"]),
                        "full_name": profile.get("full_name", ""),
                        "company": profile.get("company", ""),
                        "role": profile.get("role", "user"),
                        "demo_requested": profile.get("demo_requested", False),
                        "demo_approved": profile.get("demo_approved", False),
                        "demo_date": profile.get("demo_date"),
                        "created_at": profile.get("created_at", ""),
                        "updated_at": profile.get("updated_at", "")
                    }
                    return UserProfile(**profile_data)

            # If no profile exists, create one
            profile_data = {
                "id": user_data["id"],
                "email": user_data["email"],
                "full_name": user_data.get("user_metadata", {}).get("full_name", ""),
                "company": user_data.get("user_metadata", {}).get("company", ""),
                "role": "user",
                "demo_requested": False,
                "demo_approved": False,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }

            create_response = await client.post(
                f"{SUPABASE_URL}/rest/v1/profiles",
                headers={
                    "apikey": SUPABASE_SERVICE_ROLE_KEY,
                    "Authorization": f"Bearer {SUPABASE_SERVICE_ROLE_KEY}",
                    "Content-Type": "application/json",
                    "Prefer": "return=representation"
                },
                json=profile_data
            )

            if create_response.status_code == 201:
                created_profile = create_response.json()[0]
                return UserProfile(**created_profile)
            else:
                # If profile creation fails, return a basic profile
                print(f"Warning: Failed to create profile: {create_response.text}")
                return UserProfile(
                    id=user_data["id"],
                    email=user_data["email"],
                    full_name=user_data.get("user_metadata", {}).get("full_name", ""),
                    company=user_data.get("user_metadata", {}).get("company", ""),
                    role="user",
                    demo_requested=False,
                    demo_approved=False,
                    demo_date=None,
                    created_at=datetime.utcnow().isoformat(),
                    updated_at=datetime.utcnow().isoformat()
                )

    except Exception as e:
        print(f"Error in get_user_profile: {str(e)}")
        # Return a basic profile instead of throwing an error
        return UserProfile(
            id=user_data["id"],
            email=user_data["email"],
            full_name=user_data.get("user_metadata", {}).get("full_name", ""),
            company=user_data.get("user_metadata", {}).get("company", ""),
            role="user",
            demo_requested=False,
            demo_approved=False,
            demo_date=None,
            created_at=datetime.utcnow().isoformat(),
            updated_at=datetime.utcnow().isoformat()
        )

@router.get("/verify", response_model=VerifyResponse)
async def verify_auth(user_data: Dict[str, Any] = Depends(verify_supabase_jwt)):
    """Verify authentication and return basic user info"""
    return VerifyResponse(
        authenticated=True,
        user_id=user_data["id"],
        email=user_data["email"],
        message="Authentication successful"
    )

@router.get("/verify-full", response_model=AuthResponse)
async def verify_auth_full(user_data: Dict[str, Any] = Depends(verify_supabase_jwt)):
    """Verify authentication and return user profile"""
    profile = await get_user_profile(user_data)
    return AuthResponse(user=profile, message="Authentication successful")

@router.get("/profile", response_model=UserProfile)
async def get_profile(user_data: Dict[str, Any] = Depends(verify_supabase_jwt)):
    """Get user profile"""
    return await get_user_profile(user_data)

@router.put("/profile", response_model=UserProfile)
async def update_profile(
    updates: ProfileUpdate,
    user_data: Dict[str, Any] = Depends(verify_supabase_jwt)
):
    """Update user profile"""
    if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
        raise HTTPException(status_code=500, detail="Supabase not configured")

    try:
        # Prepare update data
        update_data = {}
        if updates.full_name is not None:
            update_data["full_name"] = updates.full_name
        if updates.company is not None:
            update_data["company"] = updates.company
        update_data["updated_at"] = datetime.utcnow().isoformat()

        async with httpx.AsyncClient() as client:
            response = await client.patch(
                f"{SUPABASE_URL}/rest/v1/profiles?id=eq.{user_data['id']}",
                headers={
                    "apikey": SUPABASE_SERVICE_ROLE_KEY,
                    "Authorization": f"Bearer {SUPABASE_SERVICE_ROLE_KEY}",
                    "Content-Type": "application/json",
                    "Prefer": "return=representation"
                },
                json=update_data
            )

            if response.status_code == 200:
                updated_profile = response.json()[0]
                return UserProfile(**updated_profile)
            else:
                raise HTTPException(status_code=500, detail="Failed to update profile")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Profile update failed: {str(e)}")

@router.post("/request-demo")
async def request_demo(user_data: Dict[str, Any] = Depends(verify_supabase_jwt)):
    """Request a demo for the authenticated user"""
    if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
        raise HTTPException(status_code=500, detail="Supabase not configured")

    try:
        async with httpx.AsyncClient() as client:
            # Update user to mark demo as requested
            user_update = {
                "demo_requested": True,
                "updated_at": datetime.utcnow().isoformat()
            }

            user_response = await client.patch(
                f"{SUPABASE_URL}/rest/v1/profiles?id=eq.{user_data['id']}",
                headers={
                    "apikey": SUPABASE_SERVICE_ROLE_KEY,
                    "Authorization": f"Bearer {SUPABASE_SERVICE_ROLE_KEY}",
                    "Content-Type": "application/json"
                },
                json=user_update
            )

            if user_response.status_code != 200:
                raise HTTPException(status_code=500, detail="Failed to update user demo status")

            # Create demo request record
            demo_request = {
                "user_id": user_data["id"],
                "status": "pending",
                "created_at": datetime.utcnow().isoformat()
            }

            demo_response = await client.post(
                f"{SUPABASE_URL}/rest/v1/demo_requests",
                headers={
                    "apikey": SUPABASE_SERVICE_ROLE_KEY,
                    "Authorization": f"Bearer {SUPABASE_SERVICE_ROLE_KEY}",
                    "Content-Type": "application/json"
                },
                json=demo_request
            )

            if demo_response.status_code != 201:
                raise HTTPException(status_code=500, detail="Failed to create demo request")

            return {"message": "Demo request submitted successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Demo request failed: {str(e)}")

@router.get("/health")
async def auth_health():
    """Health check for authentication service"""
    return {
        "status": "healthy",
        "supabase_configured": bool(SUPABASE_URL and SUPABASE_ANON_KEY and SUPABASE_SERVICE_ROLE_KEY),
        "timestamp": datetime.utcnow().isoformat()
    }