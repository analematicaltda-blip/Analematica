from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "SGA-CD FastAPI Backend"
    API_V1_STR: str = "/api/v1"
    TESTING: bool = False
    ENVIRONMENT: str = "production"

    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Database
    DATABASE_URL: str

    # OpenAI
    OPENAI_API_KEY: str = "your_openai_api_key_here"

    # Stripe
    STRIPE_SECRET_KEY: str = "sk_test_placeholder"
    STRIPE_PUBLISHABLE_KEY: str = "pk_test_placeholder"
    STRIPE_WEBHOOK_SECRET: str = "whsec_placeholder"

    # MercadoPago
    MERCADOPAGO_ACCESS_TOKEN: str = "mp_test_placeholder"

    # Wompi
    WOMPI_PUBLIC_KEY: str = "wompi_pub_key_placeholder"
    WOMPI_SECRET_KEY: str = "wompi_sec_key_placeholder"

    # WhatsApp
    WHATSAPP_API_TOKEN: str = "YOUR_WHATSAPP_API_TOKEN"
    WHATSAPP_PHONE_NUMBER_ID: str = "YOUR_PHONE_NUMBER_ID"
    WHATSAPP_VERIFY_TOKEN: str = "sga-cd-whatsapp-secret"

    # Meta (Facebook/Instagram)
    META_CLIENT_ID: str = "YOUR_META_APP_ID"
    META_CLIENT_SECRET: str = "YOUR_META_APP_SECRET"

    # Google Workspace
    GOOGLE_CLIENT_ID: str = "YOUR_GOOGLE_CLIENT_ID"
    GOOGLE_CLIENT_SECRET: str = "YOUR_GOOGLE_CLIENT_SECRET"

    SERVER_HOST: str = "http://localhost:8000" # For constructing callback URLs

    class Config:
        case_sensitive = True
        env_file = ".env"
        env_file_encoding = 'utf-8'
        extra = "ignore"

settings = Settings()