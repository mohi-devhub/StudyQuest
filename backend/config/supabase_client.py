import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get Supabase credentials from environment
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")  # Should be the ANON key (respects RLS)
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")  # Bypasses RLS

# Connection pool configuration
DB_POOL_SIZE = int(os.getenv("DB_POOL_SIZE", "10"))
DB_MAX_OVERFLOW = int(os.getenv("DB_MAX_OVERFLOW", "5"))
DB_POOL_TIMEOUT = int(os.getenv("DB_POOL_TIMEOUT", "30"))

# Initialize Supabase clients
supabase: Client = None
supabase_admin: Client = None

# Check if we're in a test environment
IS_TEST_ENV = os.getenv("PYTEST_CURRENT_TEST") is not None or os.getenv("CI") == "true"

if IS_TEST_ENV:
    # In test environment, don't initialize real Supabase client
    # Tests should mock the client as needed
    supabase = None
    supabase_admin = None
elif SUPABASE_URL and SUPABASE_KEY:
    # Create anon client (respects RLS)
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        print(f"Warning: Failed to initialize Supabase client: {e}")
        supabase = None

    # Create admin client (bypasses RLS) — only if service_role key is provided
    if SUPABASE_SERVICE_ROLE_KEY:
        try:
            supabase_admin = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
        except Exception as e:
            print(f"Warning: Failed to initialize Supabase admin client: {e}")
            supabase_admin = None
else:
    # Only raise error in non-test environments
    raise ValueError(
        "SUPABASE_URL and SUPABASE_KEY must be set in environment variables"
    )


def get_supabase() -> Client:
    """
    Returns the anon Supabase client (respects RLS).

    Returns:
        Client: Supabase client instance

    Raises:
        RuntimeError: If client is not initialized and not in test mode
    """
    if supabase is None and not IS_TEST_ENV:
        raise RuntimeError("Supabase client is not initialized")
    return supabase


def get_admin_supabase() -> Client:
    """
    Returns the admin Supabase client (bypasses RLS).
    Use only for privileged operations like token verification.

    Returns:
        Client: Supabase admin client instance

    Raises:
        RuntimeError: If admin client is not initialized and not in test mode
    """
    if supabase_admin is None and not IS_TEST_ENV:
        raise RuntimeError(
            "Supabase admin client is not initialized. "
            "Set SUPABASE_SERVICE_ROLE_KEY in environment variables."
        )
    return supabase_admin
