from sqlalchemy import select, or_
from sqlalchemy.orm import Session

import auth, models, schemas


def create_user(db: Session, user: schemas.UserIn):
    hashed_password = auth.get_password_hash(user.password)
    db_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        role=user.role.value,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_users(db: Session):
    stmt = select(models.User)
    return db.scalars(stmt).all()


def get_user_by_username(db: Session, username: str, email: str | None = None):
    stmt = (
        select(models.User)
        .where(or_(models.User.username == username, models.User.email == email))
    )
    return db.scalar(stmt)
