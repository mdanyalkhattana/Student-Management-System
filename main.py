from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
from fastapi.middleware.cors import CORSMiddleware
from config.config import settings
from routes import auth_routes
from database import Base, engine
 

# from routes import auth_routes, verify_routes


app = FastAPI(title="Authentication System")
app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)
# app.add_middleware(
#     SessionMiddleware,
#     secret_key=settings.SECRET_KEY,
#     same_site="lax",     # or "none" if using https
#     https_only=False
# )

# # ✅ STEP 2: Add Proper CORS Middleware
# origins = [
#     # "http://localhost:8000",
#     "http://127.0.0.1:8000"
# ]

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

Base.metadata.create_all(bind=engine)

app.include_router(auth_routes.router)
 
# app.include_router(google_auth_routes.router)

# app.include_router(auth_routes.router)
# app.include_router(auth_routes.router)

