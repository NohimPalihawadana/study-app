
import os
import re
import time
import secrets
import hashlib

from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import (
    FastAPI,
    Depends,
    HTTPException,
    Request,
    Response,
)

from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from pwdlib import PasswordHash
from sqlmodel import SQLModel, Session, select
from sqlalchemy.exc import IntegrityError

from database import engine, get_session
from models import User, AuthSession


# ==========================================
# 1. CONFIGURATION
# ==========================================

password_hasher = PasswordHash.recommended()

# Used when a username does not exist.
DUMMY_HASH = password_hasher.hash(
    "dummy-password-not-used"
)

COOKIE_NAME = "study_session"

# Session expires after 7 days.
SESSION_DURATION = 60 * 60 * 24 * 7

# False for local HTTP development.
# Must be True when using HTTPS in production.
COOKIE_SECURE = (
    os.getenv("COOKIE_SECURE", "false").lower() == "true"
)

SessionDep = Annotated[
    Session,
    Depends(get_session)
]


# ==========================================
# 2. APPLICATION INITIALIZATION
# ==========================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create missing tables at application startup.
    SQLModel.metadata.create_all(engine)
    yield


app = FastAPI(
    title="Study App API",
    description="Backend API for the Study App",
    version="0.1.0",
    lifespan=lifespan,
)


# Allow requests from the React frontend.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


# ==========================================
# 3. REQUEST AND RESPONSE SCHEMAS
# ==========================================

class RegisterRequest(BaseModel):
    username: str = Field(
        min_length=3,
        max_length=30,
    )

    password: str = Field(
        min_length=8,
        max_length=128,
    )

    confirm_password: str

    university: str = Field(
        min_length=1,
        max_length=120,
    )

    field_of_study: str = Field(
        min_length=1,
        max_length=120,
    )


class LoginRequest(BaseModel):
    username: str
    password: str


class UserPublic(BaseModel):
    id: int
    username: str
    university: str
    field_of_study: str


# ==========================================
# 4. AUTHENTICATION HELPER FUNCTIONS
# ==========================================

def hash_token(token: str) -> str:
    """Create a SHA-256 hash of a session token."""

    return hashlib.sha256(
        token.encode("utf-8")
    ).hexdigest()


def current_user(
    request: Request,
    session: SessionDep,
) -> User:
    """Get the authenticated user from the session cookie."""

    # Read the browser's session cookie.
    token = request.cookies.get(COOKIE_NAME)

    if not token:
        raise HTTPException(
            status_code=401,
            detail="Not logged in.",
        )

    # Hash the token before database lookup.
    token_hash = hash_token(token)

    auth_session = session.exec(
        select(AuthSession).where(
            AuthSession.token_hash == token_hash
        )
    ).first()

    if not auth_session:
        raise HTTPException(
            status_code=401,
            detail="Invalid session.",
        )

    # Check whether the session has expired.
    if auth_session.expires_at <= int(time.time()):
        session.delete(auth_session)
        session.commit()

        raise HTTPException(
            status_code=401,
            detail="Session expired. Please log in again.",
        )

    # Retrieve the associated user.
    user = session.get(
        User,
        auth_session.user_id,
    )

    if not user:
        raise HTTPException(
            status_code=401,
            detail="User not found.",
        )

    return user


# ==========================================
# 5. REGISTER A NEW USER
# ==========================================

@app.post(
    "/auth/register",
    response_model=UserPublic,
    status_code=201,
)
def register(
    data: RegisterRequest,
    session: SessionDep,
):
    # Normalize username.
    username = data.username.strip().lower()

    # Validate username characters.
    if not re.fullmatch(r"[a-z0-9_]{3,30}", username):
        raise HTTPException(
            status_code=400,
            detail=(
                "Username must contain 3-30 "
                "letters, numbers, or underscores."
            ),
        )

    # Confirm passwords match.
    if data.password != data.confirm_password:
        raise HTTPException(
            status_code=400,
            detail="Passwords do not match.",
        )

    # Clean up profile information.
    university = data.university.strip()
    field_of_study = data.field_of_study.strip()

    if not university or not field_of_study:
        raise HTTPException(
            status_code=400,
            detail=(
                "University and field of study "
                "cannot be empty."
            ),
        )

    # Check whether the username already exists.
    existing_user = session.exec(
        select(User).where(
            User.username == username
        )
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=409,
            detail="Username already exists.",
        )

    # Hash the password before storing.
    hashed_password = password_hasher.hash(
        data.password
    )

    # Create the user record.
    new_user = User(
        username=username,
        password_hash=hashed_password,
        university=university,
        field_of_study=field_of_study,
    )

    session.add(new_user)

    try:
        session.commit()

    except IntegrityError as exc:
        session.rollback()

        # PostgreSQL SQLSTATE for unique constraint violation.
        if getattr(exc.orig, "sqlstate", None) == "23505":
            raise HTTPException(
                status_code=409,
                detail="Username already exists.",
            ) from exc

        raise

    # Refresh to retrieve the generated user ID.
    session.refresh(new_user)

    return new_user


# ==========================================
# 6. LOGIN
# ==========================================

@app.post(
    "/auth/login",
    response_model=UserPublic,
)
def login(
    data: LoginRequest,
    response: Response,
    session: SessionDep,
):
    # Normalize the username.
    username = data.username.strip().lower()

    # Search for the user in PostgreSQL.
    user = session.exec(
        select(User).where(
            User.username == username
        )
    ).first()

    # Use a dummy hash if username does not exist.
    hash_to_check = (
        user.password_hash
        if user
        else DUMMY_HASH
    )

    # Verify the supplied password.
    valid_password = password_hasher.verify(
        data.password,
        hash_to_check,
    )

    if not user or not valid_password:
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password.",
        )

    # Generate a random login session token.
    token = secrets.token_urlsafe(32)

    # Store only the hashed token.
    auth_session = AuthSession(
        user_id=user.id,
        token_hash=hash_token(token),
        expires_at=(
            int(time.time()) + SESSION_DURATION
        ),
    )

    session.add(auth_session)
    session.commit()

    # Send session cookie to the browser.
    response.set_cookie(
        key=COOKIE_NAME,
        value=token,
        httponly=True,
        secure=COOKIE_SECURE,
        samesite="lax",
        max_age=SESSION_DURATION,
        path="/",
    )

    return user


# ==========================================
# 7. GET CURRENT USER
# ==========================================

@app.get(
    "/auth/me",
    response_model=UserPublic,
)
def get_me(
    request: Request,
    session: SessionDep,
):
    return current_user(
        request,
        session,
    )


# ==========================================
# 8. LOGOUT
# ==========================================

@app.post("/auth/logout")
def logout(
    request: Request,
    response: Response,
    session: SessionDep,
):
    token = request.cookies.get(COOKIE_NAME)

    if token:
        # Find the existing login session.
        auth_session = session.exec(
            select(AuthSession).where(
                AuthSession.token_hash == hash_token(token)
            )
        ).first()

        if auth_session:
            # Delete session from database.
            session.delete(auth_session)
            session.commit()

    # Remove the browser's session cookie.
    response.delete_cookie(
        key=COOKIE_NAME,
        path="/",
        secure=COOKIE_SECURE,
        samesite="lax",
    )

    return {
        "message": "Logged out successfully."
    }
