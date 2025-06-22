
from supabase import create_client
import os

# Read values from environment
SUPABASE_URL = "https://qnzioartedlrithdxszx.supabase.co"
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
BUCKET_NAME = "uploads"

if not SUPABASE_KEY:
    print("❌ Environment variable 'SUPABASE_SERVICE_ROLE_KEY' not set.")
    exit(1)

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def test_connection():
    try:
        # Test DB query
        tables = supabase.table("sessions").select("*").limit(1).execute()
        print("✅ Database connection succeeded. 'sessions' table exists or is accessible.")
    except Exception as e:
        print("❌ Database connection failed:")
        print(e)

    try:
        # Upload a small test file
        file_content = b"Test file content"
        file_path = f"test_upload.txt"
        supabase.storage.from_(BUCKET_NAME).upload(file_path, file_content, {"content-type": "text/plain"})
        print(f"✅ Upload to bucket '{BUCKET_NAME}' succeeded.")

        # Clean up
        supabase.storage.from_(BUCKET_NAME).remove([file_path])
        print("🧹 Test file removed.")
    except Exception as e:
        print(f"❌ Upload to bucket '{BUCKET_NAME}' failed:")
        print(e)

if __name__ == "__main__":
    test_connection()
