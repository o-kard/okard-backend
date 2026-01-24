# src/auth.py
import os
import requests
from jose import jwt, JWTError
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

CLERK_ISSUER = os.getenv("CLERK_ISSUER")  

JWKS_URL = f"{CLERK_ISSUER}/.well-known/jwks.json"

jwks = requests.get(JWKS_URL).json()

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        unverified_header = jwt.get_unverified_header(token)
        key = next(
            k for k in jwks["keys"] if k["kid"] == unverified_header["kid"]
        )

        payload = jwt.decode(
            token,
            key,
            algorithms=["RS256"],
            audience=None,
            issuer=CLERK_ISSUER,
        )
    except (JWTError, StopIteration):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    return payload
