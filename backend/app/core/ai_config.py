"""
AI Configuration settings for OpenAI and other AI services.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class AISettings(BaseSettings):
    """
    AI-related configuration settings.
    Loads from environment variables with AI_ prefix.
    """

    # OpenAI Configuration
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4-turbo-preview"
    OPENAI_MAX_TOKENS: int = 500
    OPENAI_TEMPERATURE: float = 0.3  # Lower = more focused, higher = more creative

    # Alternative: Anthropic Claude (optional)
    ANTHROPIC_API_KEY: str = ""
    ANTHROPIC_MODEL: str = "claude-3-sonnet-20240229"

    # Summarization Settings
    SUMMARY_MAX_LENGTH: int = 150  # words
    SUMMARY_STYLE: str = "concise"  # Options: "concise", "detailed", "technical"
    QUICK_SCAN_MAX_LENGTH: int = 25  # words for tender card quick scan

    # Entity Extraction Settings
    SPACY_MODEL: str = "en_core_web_sm"  # spaCy model to use
    EXTRACT_ENTITIES: bool = True  # Enable/disable entity extraction

    # Processing Settings
    AI_ENABLED: bool = True  # Master switch for AI features
    AI_CACHE_TTL: int = 86400  # Cache AI results for 24 hours (in seconds)
    AI_TIMEOUT: int = 30  # Timeout for AI API calls (seconds)

    # Cost Management
    MAX_TOKENS_PER_REQUEST: int = 4000  # Maximum tokens to send to API
    ENABLE_TOKEN_COUNTING: bool = True  # Track token usage

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore",
        env_prefix="AI_"  # Environment variables should start with AI_
    )


# Global AI settings instance
ai_settings = AISettings()
