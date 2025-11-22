import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get Supabase credentials from environment
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Connection pool configuration
DB_POOL_SIZE = int(os.getenv("DB_POOL_SIZE", "10"))
DB_MAX_OVERFLOW = int(os.getenv("DB_MAX_OVERFLOW", "5"))
DB_POOL_TIMEOUT = int(os.getenv("DB_POOL_TIMEOUT", "30"))

# Initialize Supabase client
supabase: Client = None

# Check if we're in a test environment
IS_TEST_ENV = os.getenv("PYTEST_CURRENT_TEST") is not None or os.getenv("CI") == "true"

if SUPABASE_URL and SUPABASE_KEY:
    # Create client with connection pooling configuration
    # Note: Connection pooling is handled internally by the Supabase client
    # The pool configuration variables are kept for future use if needed
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
elif not IS_TEST_ENV:
    # Only raise error in non-test environments
    raise ValueError(
        "SUPABASE_URL and SUPABASE_KEY must be set in environment variables"
    )


def get_supabase() -> Client:
    """
    Returns the initialized Supabase client.
    
    Returns:
        Client: Supabase client instance
    """
    if supabase is None:
        raise RuntimeError("Supabase client is not initialized")
    return supabase
