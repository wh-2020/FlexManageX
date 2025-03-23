from app.core.config import settings

TORTOISE_ORM = {
    "connections": {
        "default": settings.DATABASE_URL
    },
    "apps": {
        "models": {
            "models": [
                "app.models.user",
                "app.models.role",
                "app.models.permission",
            ],
            "default_connection": "default",
        }
    }
} 