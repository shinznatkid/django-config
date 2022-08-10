INSTALLED_APPS += ['corsheaders']

MIDDLEWARE.insert(
    0,
    "corsheaders.middleware.CorsMiddleware",
)

CORS_ALLOWED_ORIGINS = [
    "http://localhost:8000",
    "http://localhost:3000",
]
