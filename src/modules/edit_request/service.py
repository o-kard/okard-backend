from sqlalchemy.orm import Session
from uuid import UUID
from datetime import datetime, timezone
from fastapi import HTTPException

from datetime import timezone
from . import repo, schema, model
from src.modules.notification import service as notification_service, schema as notification_schema
from src.modules.common.enums import NotificationType, EditRequestStatus, VoteDecision, PostState
from src.modules.post import service as post_service, schema as post_schema, repo as post_repo, model as post_model
from src.modules.reward import repo as reward_repo, schema as reward_schema
from src.modules.media import repo as media_repo

def _generate_display_changes(post: post_model.Post, proposed_changes: dict) -> str:
    lines = []
    
    # 1. Post Fields
    if "goal_amount" in proposed_changes:
        lines.append(f"Goal Amount: {post.goal_amount} -> {proposed_changes['goal_amount']}")
    if "status" in proposed_changes:
        lines.append(f"Status: {post.status} -> {proposed_changes['status']}")
    if "effective_end_date" in proposed_changes:
        lines.append(f"End Date: {post.effective_end_date} -> {proposed_changes['effective_end_date']}")
    
    # 2. Rewards
    if "rewards_payload" in proposed_changes:
        rewards_payload = proposed_changes["rewards_payload"]
        if isinstance(rewards_payload, list):
            # Map existing rewards
            current_rewards = {str(r.id): r for r in post.rewards}
            
            for item in rewards_payload:
                # Check if New or Existing
                rid = item.get("id")
                
                if not rid:
                    # New Reward
                    header = item.get("reward_header", "Unknown")
                    amount = item.get("reward_amount", "?")
                    lines.append(f"[New Reward] {header} (Amount: {amount})")
                    continue
                
                # Existing Reward
                if str(rid) in current_rewards:
                    curr = current_rewards[str(rid)]
                    
                    # Only check if isEdited is True
                    if item.get("isEdited"):
                        changes = []
                        # Check specific fields
                        if "reward_header" in item and item["reward_header"] != curr.reward_header:
                            changes.append(f"Header: '{curr.reward_header}' -> '{item['reward_header']}'")
                        if "reward_amount" in item and item["reward_amount"] != curr.reward_amount:
                            changes.append(f"Amount: {curr.reward_amount} -> {item['reward_amount']}")
                        if "reward_description" in item and item["reward_description"] != curr.reward_description:
                            # Description might be long, maybe just say it changed? Or substring.
                            changes.append(f"Description updated")
                            
                        if changes:
                            lines.append(f"[Update Reward] {curr.reward_header}: " + ", ".join(changes))
    
    if not lines:
        return "No significant changes detected"
        
    return "\n".join(lines)

def create_request(db: Session, requester_id: UUID, data: schema.EditRequestCreate):
    # Verify Post exists
    post = post_service.get_post(db, data.post_id)

    # Generate display_changes
    if data.proposed_changes:
        data.display_changes = _generate_display_changes(post, data.proposed_changes)

    # Default Expiration logic: 3 days if not provided
    if not data.expires_at:
        from datetime import timedelta
        # Use timezone aware datetime
        data.expires_at = datetime.now(timezone.utc) + timedelta(days=3)
    
    # Identify Top 11 Contributors
    contributors = repo.get_top_contributors(db, data.post_id, limit=11)
    
    # Create Request
    edit_req = repo.create_edit_request(db, requester_id, data)
    
    # Create Approvers
    repo.create_approvers(db, edit_req.id, contributors)
    
    # Notify Approvers
    for approver in contributors:
        notif_payload = notification_schema.NotificationCreate(
            user_id=approver.user_id,
            actor_id=requester_id,
            post_id=data.post_id,
            notification_title="New Edit Request",
            notification_message=f"A request to edit post '{post.post_header}' needs your vote.",
            type=NotificationType.system_alert 
        )
        notification_service.create_notification(db, notif_payload)
        
    return edit_req

    if approve_count > threshold:
        req.status = EditRequestStatus.approved
        req.resolved_at = datetime.now()
        
        if req.proposed_changes:
            try:
                changes = dict(req.proposed_changes)
                rewards_payload = changes.pop("rewards_payload", None)
                
                if rewards_payload and isinstance(rewards_payload, list):
                    from src.modules.reward import repo as reward_repo, schema as reward_schema
                    for item in rewards_payload:
                        data_dict = {k: v for k, v in item.items() if k not in ["isEdited", "id"]}
                        
                        if item.get("id"):
                            # Update Existing
                            rid = UUID(str(item["id"]))
                            update_schema = reward_schema.RewardUpdate(**data_dict)
                            curr_reward = reward_repo.get_reward(db, rid)
                            if curr_reward:
                                reward_repo.update_reward(db, curr_reward, update_schema)
                        else:
                            # Create New
                            data_dict["post_id"] = req.post_id
                            create_schema = reward_schema.RewardCreate(**data_dict)
                            reward_repo.create_reward(db, create_schema)
                
                # 2. Update Post Columns
                if changes:
                    valid_keys = post_schema.PostUpdate.model_fields.keys()
                    post_changes = {k: v for k, v in changes.items() if k in valid_keys}
                    
                    if post_changes:
                        update_data = post_schema.PostUpdate(**post_changes)
                        post = post_repo.get_post(db, req.post_id)
                        post_repo.update_post(db, post, update_data)
                    
            except Exception as e:
                import traceback
                traceback.print_exc()
                raise e
            
    elif reject_count >= (total_approvers - threshold):
        req.status = EditRequestStatus.rejected
        req.resolved_at = datetime.now()
    
    db.commit()
    db.refresh(req)
    
    return vote

async def cast_vote(db: Session, edit_request_id: UUID, user_id: UUID, data: schema.VoteCreate):
    # Get Request with locking to prevent race conditions
    req = db.query(model.EditRequest).filter(model.EditRequest.id == edit_request_id).with_for_update().first()
    if not req:
        raise HTTPException(status_code=404, detail="Edit Request not found")
        
    if req.status != EditRequestStatus.pending:
        raise HTTPException(status_code=400, detail="Edit Request is not pending")
        
    # Verify User is Approver
    approver = next((app for app in req.approvers if app.user_id == user_id), None)
    if not approver:
        raise HTTPException(status_code=403, detail="You are not authorized to vote on this request")
        
    # Check if already voted
    existing_vote = next((v for v in req.votes if v.user_id == user_id), None)
    if existing_vote:
        raise HTTPException(status_code=400, detail="You have already voted")
        
    # Cast Vote
    vote = repo.create_vote(db, edit_request_id, user_id, data)
    
    db.refresh(req)
    
    total_approvers = len(req.approvers)
    votes = req.votes
    
    approve_count = sum(1 for v in votes if v.decision == VoteDecision.approve)
    reject_count = sum(1 for v in votes if v.decision == VoteDecision.reject)
    
    # Majority rule: > 50%
    threshold = total_approvers / 2
    
    if approve_count > threshold:
        req.status = EditRequestStatus.approved
        req.resolved_at = datetime.now()
        
        # Apply changes if proposed_changes exists
        if req.proposed_changes:
            try:
                # 1. Handle Rewards First
                changes = dict(req.proposed_changes)
                rewards_payload = changes.pop("rewards_payload", None)
                
                if rewards_payload is not None and isinstance(rewards_payload, list):
                    # FULL SYNC LOGIC
                    # 1. Fetch current rewards
                    current_rewards = reward_repo.list_by_post(db, req.post_id)
                    current_reward_map = {str(r.id): r for r in current_rewards}
                    
                    # 2. Identify incoming IDs
                    incoming_ids = set()
                    for item in rewards_payload:
                        if item.get("id"):
                            incoming_ids.add(str(item["id"]))
                    
                    # 3. Delete rewards not in payload
                    for rid, r_obj in current_reward_map.items():
                        if rid not in incoming_ids:
                            reward_repo.delete_reward(db, r_obj)
                            
                            # 4. Create or Update
                    from src.modules.media import model as media_model
                    from src.modules.common.enums import ReferenceType
                    
                    for index, item in enumerate(rewards_payload):
                        # Clean item
                        media_id_str = item.get("image_id")
                        # Remove UI flags and handled fields
                        # Also remove 'backup_amount' as it is computed/readonly usually
                        data_dict = {
                            k: v for k, v in item.items() 
                            if k not in ["isEdited", "id", "file", "image_id", "backup_amount"]
                        }
                        
                        # Set display_order based on list position
                        data_dict["display_order"] = index
                        
                        target_reward_id = None
                        
                        if item.get("id"):
                            # Update Existing
                            rid = UUID(str(item["id"]))
                            target_reward_id = rid
                            curr_reward = current_reward_map.get(str(rid))
                            if curr_reward:
                                update_schema = reward_schema.RewardUpdate(**data_dict)
                                reward_repo.update_reward(db, curr_reward, update_schema)
                        else:
                            # Create New
                            data_dict["post_id"] = req.post_id
                            # Ensure backup_amount is set to 0 strictly for new items
                            data_dict["backup_amount"] = 0
                            create_schema = reward_schema.RewardCreate(**data_dict)
                            new_reward = reward_repo.create_reward(db, create_schema)
                            target_reward_id = new_reward.id

                        # Handle Media Linking if image_id is present
                        if media_id_str and target_reward_id:
                            try:
                                media_id = UUID(str(media_id_str))
                                media_obj = media_repo.get_media(db, media_id)
                                if media_obj:
                                    # Create MediaHandler link
                                    # Clean up old handlers for this media
                                    db.query(media_model.MediaHandler).filter(media_model.MediaHandler.media_id == media_id).delete()
                                    
                                    new_handler = media_model.MediaHandler(
                                        media_id=media_id,
                                        reference_id=target_reward_id,
                                        type=ReferenceType.reward
                                    )
                                    db.add(new_handler)
                                    
                            except Exception as e:
                                print(f"Failed to link media {media_id_str} to reward {target_reward_id}: {e}")

                # 2. Update Post Columns
                if changes:
                    valid_keys = post_schema.PostUpdate.model_fields.keys()
                    post_changes = {k: v for k, v in changes.items() if k in valid_keys}
                    
                    if post_changes:
                        update_data = post_schema.PostUpdate(**post_changes)
                        post = post_repo.get_post(db, req.post_id)
                        post_repo.update_post(db, post, update_data)
                    
            except Exception as e:
                import traceback
                traceback.print_exc()
                raise e
            
    elif reject_count >= (total_approvers - threshold):
        req.status = EditRequestStatus.rejected
        req.resolved_at = datetime.now()
    
    db.commit()
    db.refresh(req)
    
    return vote

def get_pending_requests(db: Session, post_id: UUID):
    return repo.get_pending_requests_by_post(db, post_id)
