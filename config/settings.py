"""
Configuration settings for the Multi-Agent AI Use Case Generation System
Enhanced with better API key validation and debugging
"""
import os
from dotenv import load_dotenv
import streamlit as st  # Import streamlit for secrets management

# Load environment variables
load_dotenv()

class Settings:
    """Application settings with enhanced API key management"""
    
    # LLM Configuration
    LLM_MODEL: str = "openai/gpt-4o-mini"  # Model that supports tool use
    LLM_TEMPERATURE: float = 0.7
    LLM_MAX_TOKENS: int = 4000
    
    # API Keys - will be loaded from secrets or environment
    OPENROUTER_API_KEY: str = ""
    SERPER_API_KEY: str = ""
    KAGGLE_USERNAME: str = ""
    KAGGLE_KEY: str = ""
    GITHUB_TOKEN: str = ""
    
    # System Configuration
    LOG_LEVEL: str = "INFO"
    REPORTS_DIR: str = "outputs"
    MAX_RETRIES: int = 3
    TIMEOUT: int = 300
    
    def get_secret(self, key: str, default: str = "") -> str:
        """Retrieve secret from st.secrets or environment variables with debugging"""
        # Try Streamlit secrets first (for cloud deployment)
        if hasattr(st, 'secrets') and key in st.secrets:
            value = st.secrets[key]
            print(f"✅ Loaded {key} from Streamlit secrets")
            return value
        
        # Fallback to environment variables (for local development)
        value = os.getenv(key, default)
        if value:
            print(f"✅ Loaded {key} from environment variables")
        else:
            print(f"❌ {key} not found in secrets or environment")
        
        return value
    
    def __init__(self):
        """Initialize settings with API key loading"""
        print("🔧 Initializing settings...")
        
        # Load API keys with debugging
        self.OPENROUTER_API_KEY = self.get_secret("OPENROUTER_API_KEY")
        self.SERPER_API_KEY = self.get_secret("SERPER_API_KEY")
        self.KAGGLE_USERNAME = self.get_secret("KAGGLE_USERNAME")
        self.KAGGLE_KEY = self.get_secret("KAGGLE_KEY")
        self.GITHUB_TOKEN = self.get_secret("GITHUB_TOKEN")
        
        # Create reports directory if it doesn't exist
        os.makedirs(self.REPORTS_DIR, exist_ok=True)
        
        print("✅ Settings initialized successfully")
    
    def validate_api_keys(self) -> dict:
        """Validate that all required API keys are configured"""
        required_keys = {
            "OPENROUTER_API_KEY": self.OPENROUTER_API_KEY,
            "SERPER_API_KEY": self.SERPER_API_KEY,
            "KAGGLE_USERNAME": self.KAGGLE_USERNAME,
            "KAGGLE_KEY": self.KAGGLE_KEY,
        }
        
        missing_keys = []
        for key, value in required_keys.items():
            if not value or value.strip() == "":
                missing_keys.append(key)
        
        return {
            "valid": len(missing_keys) == 0,
            "missing_keys": missing_keys,
            "configured_keys": [key for key, value in required_keys.items() if value and value.strip() != ""]
        }
    
    def get_debug_info(self) -> dict:
        """Get debugging information about configuration"""
        return {
            "llm_model": self.LLM_MODEL,
            "api_keys_status": self.validate_api_keys(),
            "reports_dir": self.REPORTS_DIR,
            "log_level": self.LOG_LEVEL,
            "max_retries": self.MAX_RETRIES,
            "timeout": self.TIMEOUT
        }

# Create global settings instance
settings = Settings()