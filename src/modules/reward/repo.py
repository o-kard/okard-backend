from sqlalchemy.orm import Session
from . import model, schema
from uuid import UUID

def list_rewards(db: Session):
    return db.query(model.Reward).all()

def get_reward(db: Session, reward_id: UUID):
    return db.query(model.Reward).filter(model.Reward.id == reward_id).first()

def create_reward(db: Session, reward: schema.RewardCreate):
    db_reward = model.Reward(**reward.model_dump())
    db.add(db_reward)
    db.commit()
    db.refresh(db_reward)
    return db_reward

def update_reward(db: Session, db_reward: model.Reward, data: schema.RewardUpdate):
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(db_reward, key, value)
    db.commit()
    db.refresh(db_reward)
    return db_reward

def delete_reward(db: Session, db_reward: model.Reward):
    db.delete(db_reward)
    db.commit()
    return db_reward
