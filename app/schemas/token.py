from pydantic import BaseModel

class Token(BaseModel):
    """
    Response model for access token returned upon successful authentication.

    Attributes:
        access_token (str): The JWT access token generated for the authenticated user.
        token_type (str): The type of the token. Typically set to 'bearer'.
    """
    access_token: str
    token_type: str
