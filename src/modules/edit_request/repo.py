from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc
from uuid import UUID
from typing import List

from src.modules.common.enums import EditRequestStatus
from . import model
from . import schema
from src.modules.contributor.model import Contributor
from src.modules.campaign.model import Campaign
from src.modules.user.model import User

def create_edit_request(db: Session, requester_id: UUID, data: schema.EditRequestCreate) -> model.EditRequest:
    db_obj = model.EditRequest(
        campaign_id=data.campaign_id,
        requester_id=requester_id,
        description=data.description,
        display_changes=data.display_changes,
        proposed_changes=data.proposed_changes,
        expires_at=data.expires_at
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def get_edit_request(db: Session, request_id: UUID) -> model.EditRequest:
    return db.query(model.EditRequest).filter(model.EditRequest.id == request_id).options(joinedload(model.EditRequest.requester)).first()

def get_top_contributors(db: Session, campaign_id: UUID, limit: int = 11) -> List[Contributor]:
    return (
        db.query(Contributor)
        .filter(Contributor.campaign_id == campaign_id)
        .order_by(desc(Contributor.total_amount))
        .limit(limit)
        .all()
    )

def create_approvers(db: Session, edit_request_id: UUID, contributors: List[Contributor]):
    approvers = []
    
    sorted_contributors = sorted(contributors, key=lambda c: c.total_amount, reverse=True)
    
    for rank, contributor in enumerate(sorted_contributors, start=1):
        approver = model.EditRequestApprover(
            edit_request_id=edit_request_id,
            user_id=contributor.user_id,
            rank=rank,
            contribution_amount=contributor.total_amount
        )
        approvers.append(approver)
    
    if approvers:
        db.add_all(approvers)
        db.commit()

def create_vote(db: Session, edit_request_id: UUID, user_id: UUID, data: schema.VoteCreate) -> model.EditRequestVote:
    db_vote = model.EditRequestVote(
        edit_request_id=edit_request_id,
        user_id=user_id,
        decision=data.decision,
        comment=data.comment
    )
    db.add(db_vote)
    db.commit()
    db.refresh(db_vote)
    return db_vote

def get_votes(db: Session, edit_request_id: UUID):
    return db.query(model.EditRequestVote).filter(model.EditRequestVote.edit_request_id == edit_request_id).all()

def get_pending_requests_by_campaign(db: Session, campaign_id: UUID):
    return db.query(model.EditRequest).filter(
        model.EditRequest.campaign_id == campaign_id,
        model.EditRequest.status == EditRequestStatus.pending
    ).options(joinedload(model.EditRequest.approvers), joinedload(model.EditRequest.requester)).all()
