from fastapi import APIRouter, Depends, HTTPException, status,requests ,Request,Form
from sqlalchemy.orm import Session
from models.user_model import User
from schemas.auth_schema import UserCreate, UserResponse
from utils.auth_utils import hash_password
from utils.auth_utils import send_verification_email
from database import get_db
import uuid
from models.email_verification_model import EmailVerificationToken
from models.session_model import Session as UserSession
from schemas.auth_schema import LoginRequest, TokenResponse
from utils.auth_utils import verify_password
from utils.auth_utils import create_access_token
from fastapi.responses import JSONResponse,HTMLResponse
from models.uow_models import UnitOfWorkModels
from database import get_db
from utils.auth_utils import create_access_token, verify_token
from schemas.auth_schema import TokenRefreshRequest
from datetime import timedelta
from models.password_reset_model import PasswordResetToken
from schemas.auth_schema import ForgotPasswordRequest
from utils.auth_utils import send_reset_password_email
from utils.auth_utils import hash_password
from fastapi.templating import Jinja2Templates
import uuid
from utils.auth_utils import get_current_user, TokenData
from config.config import settings
from models.role import Role
from models.menu_model import Menu
from models.menu_permission import MenuPermission
import json


router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/signup", response_model=UserResponse)
def signup(user: UserCreate, db: Session = Depends(get_db)):
    # Check if email exists
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
     
    # Hash password
    hashed_pw = hash_password(user.password)

    # Create user
    new_user = User(
        name=user.name,
        email=user.email,
        password=hashed_pw,
        role_id = user.role_id

         
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Create verification token      uuid create rendom numbers
    verify_token = str(uuid.uuid4())     
    token_entry = EmailVerificationToken(
        user_id=new_user.id,
        token=verify_token
    )
    
    db.add(token_entry)
    db.commit()

    # Send email
    send_verification_email(new_user.email, verify_token)

    # return new_user
    return JSONResponse(
        content={
            "status": status.HTTP_201_CREATED,
            "message": "User registered successfully. Please check your email for verification.", 
             
        },
        status_code=status.HTTP_201_CREATED
    )

@router.post("/login", response_model=dict)
def login_user(request: LoginRequest, db: Session = Depends(get_db)):
    """
    Login API:
    1. Validate user
    2. Validate password
    3. Create JWT token
    4. Save session
    5. Fetch role, menu, permissions
    6. Return structured response
    """

    # Step 1 — Check if user exists
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"status": "error", "message": "Invalid email or password"}
        )

    # Step 2 — Check if verified
    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"status": "error", "message": "User not verified yet"}
        )

    # Step 3 — Check active session
    existing_session = db.query(UserSession).filter(
        UserSession.user_id == user.id,
        UserSession.is_active == True
    ).first()

    if existing_session:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"status": "error", "message": "Session already exists"}
        )

    # Step 4 — Verify password
    if not verify_password(request.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"status": "error", "message": "Invalid email or password"}
        )

    # Step 5 — Create JWT token
    access_token = create_access_token(data={"sub": str(user.id)})

    # Step 6 — Create new session
    new_session = UserSession(
        user_id=user.id,
        token=access_token,
        is_active=True
    )
    db.add(new_session)
    db.commit()
    db.refresh(new_session)

    ########### FETCH ROLE + MENU + PERMISSIONS ###########

    # 🔵 Step 7.1 — Fetch Role
    role = db.query(Role).filter(Role.id == user.role_id).first()
    if not role:
        raise HTTPException(
            status_code=404,
            detail={"status": "error", "message": "Role not found"}
        )

    # 🔵 Step 7.2 — Fetch Menu assigned to Role
    menu = None
    if role.menu_id:
        menu = (
            db.query(Menu)
            .filter(Menu.id == role.menu_id, Menu.status == True)
            .first()
        )

    if not menu:
        raise HTTPException(
            status_code=404,
            detail={"status": "error", "message": "Menu not assigned to this role"}
        )

    # 🔵 Step 7.3 — Fetch menu permissions
    menu_permission = (
        db.query(MenuPermission)
        .filter(MenuPermission.menu_id == menu.id)
        .first()
    )

    if not menu_permission:
        raise HTTPException(
            status_code=404,
            detail={"status": "error", "message": "Menu permissions not found"}
        )

    # Parse JSON safely
    try:
        permissions = json.loads(menu_permission.permission_objects)
    except:
        permissions = []

    ########### FINAL RESPONSE ###########

    return {
        "status": "success",
        "message": "Login successful",
        "access_token": access_token,
        "user_id": user.id,
        "role": {
            "role_id": role.id,
            "role_name": role.name
        },
        "menu": {
            "menu_id": menu.id,
            "menu_name": menu.name,
            "slug": menu.slug,
            "parent_id": menu.parent_id
        },
        "permissions": permissions
    }

    
@router.post("/refresh")
def refresh_token(request: TokenRefreshRequest, db: Session = Depends(get_db)):
    payload = verify_token(request.refresh_token)
    if not payload:
        raise HTTPException(status_code=401, detail={"status": "error", "message": "Invalid refresh token"})

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail={"status": "error", "message": "Invalid token payload"})

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    new_access_token = create_access_token(data={"sub": user_id}, expires_delta=access_token_expires)

    return JSONResponse({
        "status": "success",
        "message": "Access token refreshed successfully",
        "access_token": new_access_token,
        "token_type": "bearer"
    })

@router.get("/logout")
def logout(db: Session = Depends(get_db), current_user: TokenData = Depends(get_current_user)):
    """
    In JWT-based auth, logout is handled client-side (token is deleted).
    You can later enhance by adding token blacklisting.
    """
    # Step 1: Find active session for the user
    session = db.query(UserSession).filter(
        UserSession.user_id == current_user.id,
        UserSession.is_active == True
    ).first()   
    # Step 2: If no active session found
    if not session:
        return JSONResponse({
            "status": "info",
            "message": "User already logged out or no active session"
        })
    # Step 3: Mark session as inactive
    session.is_active = False
    db.commit()
    # Step 4: Return success response
    return JSONResponse({
        "status": "success",
        "message": "User logged out successfully"
    })

@router.get("/verify-email")
def verify_email(token: str, db: Session = Depends(get_db)):
    # Find token
    db_token = db.query(EmailVerificationToken).filter(
        EmailVerificationToken.token == token,
        EmailVerificationToken.is_used == False
    ).first()
      
    if not db_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification token"
        )
    # Find user
    user = db.query(User).filter(User.id == db_token.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Mark user as verified
    user.is_verified = True
    db_token.is_used = True
    db.commit()

    return {"message": "Email verified successfully! You can now log in."}

@router.get("/url")
async def google_auth_url(request: Request):
    """
    Debug endpoint: returns the authorization URL as JSON and forwards the
    session Set-Cookie header from the internal redirect response so the
    browser can use the same session when opening the auth URL.
    """
    redirect_uri = settings.GOOGLE_REDIRECT_URI
    # This will create a RedirectResponse and set the session cookie on it.
    redirect_resp = await oauth.google.authorize_redirect(request, redirect_uri)
    # Extract the location (the external Google consent URL)
    auth_url = redirect_resp.headers.get("location") or redirect_resp.headers.get("Location")

    json_resp = JSONResponse({"authorization_url": auth_url})
    # Forward Set-Cookie so the client receives the session cookie.
    set_cookie = redirect_resp.headers.get("set-cookie") or redirect_resp.headers.get("Set-Cookie")
    if set_cookie:
        json_resp.headers["set-cookie"] = set_cookie

    return json_resp

@router.get("/link")
async def google_auth_link(request: Request):
        """
        Debug HTML page: navigable link that opens the Google consent screen.
        This endpoint should be opened directly in the browser (not via Swagger/XHR)
        so the Set-Cookie header is stored by the browser and state validation will
        succeed on callback.
        """
        redirect_uri = settings.GOOGLE_REDIRECT_URI
        redirect_resp = await oauth.google.authorize_redirect(request, redirect_uri)
        auth_url = redirect_resp.headers.get("location") or redirect_resp.headers.get("Location")

        html = f"""
        <html>
            <head>
                <meta charset='utf-8'>
                <title>Google OAuth Debug</title>
            </head>
            <body>
                <p>Click the link below to continue to Google (will open in a new tab):</p>
                <a id='auth' href='{auth_url}' target='_blank' rel='noopener'>Login with Google</a>
                <p>If nothing happens, copy/paste this URL into a new tab:</p>
                <p><code>{auth_url}</code></p>
                <script>
                    // Optionally auto-open in a new tab (commented out by default).
                    // window.open('{auth_url}', '_blank');
                </script>
            </body>
        </html>
        """

        html_resp = HTMLResponse(content=html)
        # Forward session cookie so browser stores it when navigating to this page.
        set_cookie = redirect_resp.headers.get("set-cookie") or redirect_resp.headers.get("Set-Cookie")
        if set_cookie:
                html_resp.headers["set-cookie"] = set_cookie

        return html_resp

@router.post("/forgot", response_model=dict)
def forgot_password(request: ForgotPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        raise HTTPException(status_code=404, detail={"status": "error", "message": "Email not found"})

    reset_token = str(uuid.uuid4())
    token_entry = PasswordResetToken(user_id=user.id, token=reset_token)
    db.add(token_entry)
    db.commit()

    send_reset_password_email(user.email, reset_token)

    return {"status": "success", "message": "Password reset link sent to your email"}

@router.get("/reset-form", response_class=HTMLResponse)
def reset_password_form(request: Request, token: str):
    """Display HTML reset form when user clicks the email link."""
    return templates.TemplateResponse("reset_password_form.html", {"request": request, "token": token})

@router.post("/reset/submit", response_class=HTMLResponse)
def reset_password_submit(request: Request, token: str = Form(...), new_password: str = Form(...), db: Session = Depends(get_db)):
    """Process form and update password."""
    token_entry = db.query(PasswordResetToken).filter(
        PasswordResetToken.token == token, PasswordResetToken.is_used == False
    ).first()

    if not token_entry:
        return HTMLResponse("<h3 style='color:red;'>Invalid or expired link</h3>", status_code=400)

    user = db.query(User).filter(User.id == token_entry.user_id).first()
    if not user:
        return HTMLResponse("<h3 style='color:red;'>User not found</h3>", status_code=404)

    user.password = hash_password(new_password)
    token_entry.is_used = True
    db.commit()

    return HTMLResponse("<h3 style='color:green;'>Your password has been successfully reset.</h3>")



    # Step 4: Return success response
    return {
        "status": "success",
        "message": "User logged out successfully"
    }






