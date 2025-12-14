from sqlalchemy.orm import Session
from fastapi import Request

from src.modules.search.schemas import SearchResult, SearchResponse
from src.modules.search.repo import SearchRepository
from src.modules.user.model import User


class SearchService:

    @staticmethod
    def build_image_url(request: Request, path: str | None):
        if not path:
            return None

        path = path.lstrip("/")  
        base_url = f"{request.url.scheme}://{request.client.host}:8000"
        return f"{base_url}/{path}"

    @staticmethod
    def search(db: Session, query: str, request: Request) -> SearchResponse:

        users = SearchRepository.search_users(db, query)
        posts = SearchRepository.search_posts(db, query)

        results = []

        # -----------------------
        # USER SEARCH
        # -----------------------
        for u in users:
            thumbnail = None
            if u.image:
                thumbnail = SearchService.build_image_url(request, u.image.path)
            if u:
                user_name = (
                    f"{u.first_name} {u.surname}"
                    if u.first_name else u.username
                )
            results.append(SearchResult(
                id=u.id,
                type="user",
                name=user_name,
                thumbnail=thumbnail,
                creator=None
            ))

        # -----------------------
        # POST SEARCH
        # -----------------------
        for p in posts:

            thumbnail = None
            if p.images and len(p.images) > 0:
                thumbnail = SearchService.build_image_url(request, p.images[0].path)

            user = db.query(User).filter(User.id == p.user_id).first()
            creator_name = None
            if user:
                creator_name = (
                    f"{user.first_name} {user.surname}"
                    if user.first_name else user.username
                )

            results.append(SearchResult(
                id=p.id,
                type="post",
                name=p.post_header,
                thumbnail=thumbnail,
                creator=creator_name
            ))

        return SearchResponse(results=results)
