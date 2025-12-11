from sqlalchemy.orm import Session
from src.modules.user.model import User
from src.modules.post.model import Post

class SearchRepository:

    @staticmethod
    def search_users(db: Session, query: str):
        return (
            db.query(User)
            .filter(
                (User.username.ilike(f"%{query}%")) |
                (User.first_name.ilike(f"%{query}%")) |
                (User.surname.ilike(f"%{query}%"))
            )
            .limit(10)
            .all()
        )

    @staticmethod
    def search_posts(db: Session, query: str):
        return (
            db.query(Post)
            .filter(
                (Post.post_header.ilike(f"%{query}%")) |
                (Post.post_description.ilike(f"%{query}%"))
            )
            .limit(10)
            .all()
        )
