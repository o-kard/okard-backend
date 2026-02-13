import os
from clerk_backend_api import Clerk

clerk_secret_key = os.getenv("CLERK_SECRET_KEY")

def get_clerk_client():
    if not clerk_secret_key:
        raise ValueError("CLERK_SECRET_KEY is not set")
    return Clerk(bearer_auth=clerk_secret_key)

def update_clerk_user_password(clerk_id: str, password: str):
    client = get_clerk_client()
    try:
        response = client.users.update(user_id=clerk_id, password=password)
        return response
    except Exception as e:
        print(f"Error updating Clerk user password: {e}")
        raise e
