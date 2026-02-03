from uuid import UUID
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session, joinedload, selectinload, with_expression
from sqlalchemy import select, exists, and_, literal
from . import model, schema
from src.modules.user import model as user_model

def create_comment(db: Session, comment_data: schema.CommentCreate, user_id: UUID):
    comment = model.Comment(
        post_id=comment_data.post_id,
        user_id=user_id,
        parent_id=comment_data.parent_id,
        content=comment_data.content,
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment

def lists_comments(db: Session, post_id: UUID, viewer_user_id: UUID | None):
    if viewer_user_id:
        like_expr = exists(
            select(1).where(
                and_(
                    model.CommentLike.comment_id == model.Comment.id,
                    model.CommentLike.user_id == viewer_user_id,
                )
            )
        ).correlate(model.Comment)
    else:
        like_expr = literal(False)

    return (
        db.query(model.Comment)
        .options(
            with_expression(model.Comment.is_liked, like_expr),  # ใส่ค่าบน parent
            selectinload(model.Comment.children)
                .options(with_expression(model.Comment.is_liked, like_expr)),  # ใส่ค่าบน children
            joinedload(model.Comment.author).joinedload(user_model.User.media),
        )
        .filter(
            model.Comment.post_id == post_id,
            model.Comment.parent_id.is_(None),
        )
        .order_by(model.Comment.created_at.asc())
        .all()
    )


def get_comment(db: Session, comment_id: UUID):
    return db.query(model.Comment).filter(model.Comment.id == comment_id).first()

def like_comment(db: Session, comment_id: UUID, user_id: UUID):
    c = get_comment(db, comment_id)
    if not c:
        raise ValueError("Comment not found")

    # upsert into comment_like
    stmt = (insert(model.CommentLike)
            .values(comment_id=comment_id, user_id=user_id)
            .on_conflict_do_nothing(index_elements=[model.CommentLike.comment_id,
                                                   model.CommentLike.user_id])
            .returning(model.CommentLike.comment_id))
    inserted = db.execute(stmt).fetchone()

    if inserted:
        db.query(model.Comment).filter(model.Comment.id == comment_id) \
          .update({model.Comment.likes: model.Comment.likes + 1}, synchronize_session=False)
        db.commit()

    likes = db.query(model.Comment.likes).filter(model.Comment.id == comment_id).scalar()
    return {"comment_id": str(comment_id), "likes": likes, "is_liked": True}

def unlike_comment(db: Session, comment_id: UUID, user_id: UUID):
    c = get_comment(db, comment_id)
    if not c:
        raise ValueError("Comment not found")

    rows = (db.query(model.CommentLike)
              .filter_by(comment_id=comment_id, user_id=user_id)
              .delete())
    if rows > 0:
        db.query(model.Comment).filter(model.Comment.id == comment_id) \
          .update({model.Comment.likes: model.Comment.likes - 1}, synchronize_session=False)
        db.commit()

    likes = db.query(model.Comment.likes).filter(model.Comment.id == comment_id).scalar()
    return {"comment_id": str(comment_id), "likes": likes, "is_liked": False}
