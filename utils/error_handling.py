"""
Comprehensive Error Handling and Validation Utilities
"""
import logging
import traceback
from typing import Dict, Any, Optional, Callable
from functools import wraps
import requests
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class SystemError(Exception):
    """Base exception for system errors"""
    pass

class APIError(SystemError):
    """Exception for API-related errors"""
    def __init__(self, message: str, status_code: Optional[int] = None, response: Optional[str] = None):
        super().__init__(message)
        self.status_code = status_code
        self.response = response

class ValidationError(SystemError):
    """Exception for validation errors"""
    pass

class ConfigurationError(SystemError):
    """Exception for configuration errors"""
    pass

def handle_api_errors(func: Callable) -> Callable:
    """Decorator to handle API errors gracefully"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed in {func.__name__}: {str(e)}")
            raise APIError(f"API request failed: {str(e)}")
        except requests.exceptions.Timeout as e:
            logger.error(f"API timeout in {func.__name__}: {str(e)}")
            raise APIError(f"API request timed out: {str(e)}")
        except requests.exceptions.ConnectionError as e:
            logger.error(f"API connection error in {func.__name__}: {str(e)}")
            raise APIError(f"API connection failed: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error in {func.__name__}: {str(e)}")
            logger.error(traceback.format_exc())
            raise SystemError(f"Unexpected error in {func.__name__}: {str(e)}")
    
    return wrapper

def validate_company_input(company: str) -> bool:
    """Validate company name input"""
    if not company or not isinstance(company, str):
        raise ValidationError("Company name must be a non-empty string")
    
    if len(company.strip()) < 2:
        raise ValidationError("Company name must be at least 2 characters long")
    
    if len(company.strip()) > 100:
        raise ValidationError("Company name must be less than 100 characters")
    
    # Check for potentially harmful characters
    dangerous_chars = ['<', '>', '"', "'", '&', ';', '(', ')', '|', '`', '$']
    if any(char in company for char in dangerous_chars):
        raise ValidationError("Company name contains invalid characters")
    
    return True

def validate_industry_input(industry: str) -> bool:
    """Validate industry input"""
    if not industry or not isinstance(industry, str):
        raise ValidationError("Industry must be a non-empty string")
    
    valid_industries = [
        "Manufacturing", "Automotive", "Finance", "Retail", "Healthcare",
        "Technology", "Energy", "Agriculture", "Transportation", "Education",
        "Real Estate", "Entertainment", "Telecommunications", "Aerospace",
        "Pharmaceuticals", "Food & Beverage", "Construction", "Other"
    ]
    
    if industry not in valid_industries:
        raise ValidationError(f"Industry must be one of: {', '.join(valid_industries)}")
    
    return True

def validate_api_response(response: requests.Response, expected_status: int = 200) -> bool:
    """Validate API response"""
    if response.status_code != expected_status:
        error_msg = f"API returned status {response.status_code}"
        if response.text:
            error_msg += f": {response.text[:500]}"
        raise APIError(error_msg, response.status_code, response.text)
    
    return True

def safe_json_parse(data: str, default: Any = None) -> Any:
    """Safely parse JSON data with fallback"""
    try:
        return json.loads(data)
    except json.JSONDecodeError as e:
        logger.warning(f"Failed to parse JSON: {str(e)}")
        return default

def log_system_event(event_type: str, message: str, details: Optional[Dict[str, Any]] = None):
    """Log system events with structured format"""
    event_data = {
        "timestamp": datetime.now().isoformat(),
        "event_type": event_type,
        "message": message,
        "details": details or {}
    }
    
    logger.info(f"SYSTEM_EVENT: {json.dumps(event_data)}")

def create_error_report(error: Exception, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Create a structured error report"""
    return {
        "timestamp": datetime.now().isoformat(),
        "error_type": type(error).__name__,
        "error_message": str(error),
        "context": context or {},
        "traceback": traceback.format_exc()
    }

def retry_on_failure(max_retries: int = 3, delay: float = 1.0, backoff: float = 2.0):
    """Decorator to retry function on failure"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            current_delay = delay
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except (APIError, requests.exceptions.RequestException) as e:
                    last_exception = e
                    if attempt < max_retries:
                        logger.warning(f"Attempt {attempt + 1} failed for {func.__name__}: {str(e)}. Retrying in {current_delay}s...")
                        time.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        logger.error(f"All {max_retries + 1} attempts failed for {func.__name__}")
                except Exception as e:
                    # Don't retry on non-API errors
                    logger.error(f"Non-retryable error in {func.__name__}: {str(e)}")
                    raise e
            
            # If we get here, all retries failed
            raise last_exception
        
        return wrapper
    return decorator

def validate_file_path(file_path: str) -> bool:
    """Validate file path for security"""
    import os
    
    # Check for path traversal attempts
    if '..' in file_path or file_path.startswith('/'):
        raise ValidationError("Invalid file path: path traversal not allowed")
    
    # Check for dangerous characters
    dangerous_chars = ['<', '>', '"', "'", '&', ';', '|', '`', '$', '\\']
    if any(char in file_path for char in dangerous_chars):
        raise ValidationError("Invalid file path: contains dangerous characters")
    
    return True

def sanitize_output(output: str, max_length: int = 10000) -> str:
    """Sanitize output text for safety"""
    if not isinstance(output, str):
        return str(output)
    
    # Truncate if too long
    if len(output) > max_length:
        output = output[:max_length] + "... [truncated]"
    
    # Remove potentially harmful content
    dangerous_patterns = [
        '<script', '</script>',
        'javascript:',
        'data:text/html',
        'vbscript:',
        'onload=',
        'onerror='
    ]
    
    for pattern in dangerous_patterns:
        output = output.replace(pattern, '[removed]')
    
    return output

def check_system_health() -> Dict[str, Any]:
    """Check system health and return status"""
    health_status = {
        "timestamp": datetime.now().isoformat(),
        "status": "healthy",
        "checks": {}
    }
    
    try:
        # Check if output directories exist
        import os
        from config.settings import settings
        
        output_dir = settings.REPORTS_DIR
        if not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
            health_status["checks"]["output_directory"] = "created"
        else:
            health_status["checks"]["output_directory"] = "exists"
        
        # Check API key configuration
        api_validation = settings.validate_api_keys()
        health_status["checks"]["api_keys"] = "valid" if api_validation["valid"] else "invalid"
        
        if not api_validation["valid"]:
            health_status["status"] = "degraded"
            health_status["issues"] = api_validation["missing_keys"]
        
        # Check disk space
        import shutil
        total, used, free = shutil.disk_usage(output_dir)
        free_gb = free // (1024**3)
        health_status["checks"]["disk_space_gb"] = free_gb
        
        if free_gb < 1:
            health_status["status"] = "degraded"
            health_status["issues"] = health_status.get("issues", []) + ["low_disk_space"]
        
    except Exception as e:
        health_status["status"] = "unhealthy"
        health_status["error"] = str(e)
        logger.error(f"Health check failed: {str(e)}")
    
    return health_status

def create_fallback_response(error: Exception, context: str) -> str:
    """Create a fallback response when the system fails"""
    return f"""
    # System Error - Fallback Response
    
    We apologize, but the system encountered an error while processing your request.
    
    **Error Details:**
    - Error Type: {type(error).__name__}
    - Error Message: {str(error)}
    - Context: {context}
    - Timestamp: {datetime.now().isoformat()}
    
    **Recommended Actions:**
    1. Please try again in a few minutes
    2. Check your internet connection
    3. Verify that all API keys are properly configured
    4. Contact support if the issue persists
    
    **System Status:**
    The Multi-Agent AI system is temporarily unavailable. Please try again later.
    """

# Import time for retry decorator
import time
