from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import schemas, models, auth
from database import get_db

router = APIRouter(tags=["auth"])

@router.post("/register", response_model=schemas.Token, status_code=status.HTTP_201_CREATED)
def register(user_in: schemas.UserCreate, db: Session = Depends(get_db)):
    user_exist = db.query(models.User).filter(models.User.email == user_in.email).first()
    if user_exist:
        raise HTTPException(status_code=400, detail="E-mail já está em uso.")
    
    hashed_pwd = auth.get_password_hash(user_in.password)
    user = models.User(
        nome_completo=user_in.nome_completo,
        email=user_in.email,
        password_hash=hashed_pwd
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    token = auth.create_access_token(subject=str(user.id))
    return schemas.Token(access_token=token, token_type="bearer")

@router.post("/login", response_model=schemas.Token)
def login(user_in: schemas.UserLogin, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == user_in.email).first()
    if not user:
        raise HTTPException(status_code=401, detail="Credenciais inválidas")
    
    if not auth.verify_password(user_in.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Credenciais inválidas")
    
    token = auth.create_access_token(subject=str(user.id))
    return schemas.Token(access_token=token, token_type="bearer")
