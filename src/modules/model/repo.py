from sqlalchemy.orm import Session
from uuid import UUID
from . import model

def save_prediction_results(db: Session, post_id: UUID, results: dict):
    db_predict = model.Model(
        post_id=post_id,
        success_label=results.get('success_cls', {}).get('label', 'Unknown'),
        risk_label=results.get('risk_level', {}).get('label', 'Unknown'),
        days_to_state_label=results.get('days_to_state_change', {}).get('label', 'Unknown'),
        goal_eval_label=results.get('goal_eval', {}).get('label', 'Unknown'),
        stretch_label=results.get('stretch_potential_cls', {}).get('label', 'Unknown')
    )
    db.add(db_predict)
    db.commit()
    db.refresh(db_predict)

    return db_predict