from pydantic import BaseModel, Field

class UserCreate(BaseModel):
    nome_completo: str
    email: str = Field(pattern=r"^\S+@\S+\.\S+$")
    password: str

class UserLogin(BaseModel):
    email: str = Field(pattern=r"^\S+@\S+\.\S+$")
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str = "USER"
