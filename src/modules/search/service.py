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

        if path.startswith("http://") or path.startswith("https://"):
            return path

        path = path.lstrip("/")  
        base_url = f"{request.url.scheme}://{request.client.host}:8000"
        return f"{base_url}/{path}"

    @staticmethod
    def search(db: Session, query: str, request: Request) -> SearchResponse:

        # users = SearchRepository.search_users(db, query)
        campaigns = SearchRepository.search_campaigns(db, query)

        results = []

        # -----------------------
        # USER SEARCH
        # -----------------------
        # for u in users:
        #     thumbnail = None
        #     if u.media:
        #         thumbnail = SearchService.build_image_url(request, u.media.path)
        #     if u:
        #         user_name = (
        #             f"{u.first_name} {u.surname}"
        #             if u.first_name else u.username
        #         )
        #     results.append(SearchResult(
        #         id=u.id,
        #         type="user",
        #         name=user_name,
        #         thumbnail=thumbnail,
        #         creator=None
        #     ))
        # -----------------------
        # CAMPAIGN SEARCH
        # -----------------------
        for p in campaigns:

            thumbnail = None
            if p.media and len(p.media) > 0:
                img_media = next((m for m in p.media if m.path and any(ext in m.path.lower() for ext in ['.jpg', '.jpeg', '.png', '.webp', '.gif'])), None)
                selected_media = img_media if img_media else p.media[0]
                thumbnail = SearchService.build_image_url(request, selected_media.path)

            user = db.query(User).filter(User.id == p.user_id).first()
            creator_name = None
            if user:
                creator_name = (
                    f"{user.first_name} {user.surname}"
                    if user.first_name else user.username
                )

            results.append(SearchResult(
                id=p.id,
                type="campaign",
                name=p.campaign_header,
                thumbnail=thumbnail,
                creator=creator_name
            ))

        return SearchResponse(results=results)
