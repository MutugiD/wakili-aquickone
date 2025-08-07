from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import jwt
from datetime import datetime, timedelta
import os
from typing import Optional

router = APIRouter(prefix="/demo-auth", tags=["demo-authentication"])
security = HTTPBearer()

# Secret key for JWT (in production, use environment variable)
SECRET_KEY = "wakili-demo-secret-key-2024"
ALGORITHM = "HS256"

# Demo user credentials (in production, this would be in a database)
# These are users who have requested demos and been approved
DEMO_USERS = {
    "demo_user_1": {
        "email": "demo@example.com",
        "name": "Demo User",
        "company": "Demo Law Firm",
        "demo_requested": True,
        "approved": True,
        "demo_date": "2024-07-30"
    }
}

class DemoLoginRequest(BaseModel):
    email: str
    demo_code: str  # Special code given to demo users

class DemoLoginResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    user_info: dict

def create_demo_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=2)  # Demo tokens expire in 2 hours
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_demo_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid demo authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return email
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Demo token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid demo authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

@router.post("/login", response_model=DemoLoginResponse)
async def demo_login(request: DemoLoginRequest):
    # Check if user exists and has been approved for demo
    user_found = None
    for user_id, user_data in DEMO_USERS.items():
        if user_data["email"] == request.email:
            user_found = user_data
            break

    if not user_found:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Demo user not found. Please request a demo first."
        )

    if not user_found["demo_requested"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Demo not requested. Please request a demo first."
        )

    if not user_found["approved"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Demo request pending approval."
        )

    # In a real system, you'd verify the demo_code against what was sent to the user
    # For now, we'll use a simple check
    if request.demo_code != "WAKILI2024":  # Demo code sent to approved users
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid demo code"
        )

    # Create demo access token (shorter expiration for demo users)
    access_token_expires = timedelta(hours=2)
    access_token = create_demo_access_token(
        data={"sub": request.email, "type": "demo"},
        expires_delta=access_token_expires
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": 7200,  # 2 hours in seconds
        "user_info": {
            "email": user_found["email"],
            "name": user_found["name"],
            "company": user_found["company"],
            "demo_date": user_found["demo_date"]
        }
    }

@router.get("/verify")
async def verify_demo_auth(current_user: str = Depends(verify_demo_token)):
    return {"message": "Demo authentication successful", "user": current_user}

@router.get("/demo-status")
async def demo_status(current_user: str = Depends(verify_demo_token)):
    # Find user info
    user_found = None
    for user_id, user_data in DEMO_USERS.items():
        if user_data["email"] == current_user:
            user_found = user_data
            break

    return {
        "status": "authenticated",
        "user": current_user,
        "role": "demo_user",
        "demo_date": user_found["demo_date"] if user_found else None,
        "permissions": ["demo_access", "limited_features"]
    }

@router.post("/request-demo")
async def request_demo(demo_request: dict):
    """
    This endpoint would be used when someone fills out the demo request form.
    In a real system, this would:
    1. Save the request to a database
    2. Send notification to admin
    3. Send confirmation email to user
    4. Generate a unique demo code
    """
    # For now, just return success
    return {
        "message": "Demo request received",
        "status": "pending_approval",
        "next_steps": "We'll review your request and contact you within 24 hours"
    }