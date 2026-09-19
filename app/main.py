from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.routers.auth import router as auth_router
from app.routers.businesses import router as business_router
from app.routers.categories import router as category_router
from app.routers.reviews import business_reviews_router, reviews_router
from app.routers.uploads import router as uploads_router
from app.routers.users import router as users_router

app = FastAPI(title=settings.APP_NAME, version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth_router)
app.include_router(category_router)
app.include_router(business_router)
app.include_router(business_reviews_router)
app.include_router(reviews_router)
app.include_router(uploads_router)
app.include_router(users_router)


@app.get("/health", tags=["Health"])
def healthcheck():
    return {"status": "ok"}
