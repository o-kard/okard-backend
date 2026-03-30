from sqlalchemy.orm import Session
from uuid import UUID
from datetime import datetime, timezone
from . import model

def save_prediction_results(db: Session, campaign_id: UUID, results: dict):
    db_predict = db.query(model.Model).filter(model.Model.campaign_id == campaign_id).first()
    
    if not db_predict:
        db_predict = model.Model(campaign_id=campaign_id)
        db.add(db_predict)
    
    db_predict.success_label = results.get('success_cls', {}).get('label', 'Unknown')
    db_predict.risk_label = results.get('risk_level', {}).get('label', 'Unknown')
    db_predict.days_to_state_label = results.get('days_to_state_change', {}).get('label', 'Unknown')
    db_predict.goal_eval_label = results.get('goal_eval', {}).get('label', 'Unknown')
    db_predict.stretch_label = results.get('stretch_potential_cls', {}).get('label', 'Unknown')
    db_predict.created_at = datetime.now(timezone.utc)
    
    db.commit()
    db.refresh(db_predict)

    return db_predict