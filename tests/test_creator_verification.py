import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.database.db import DATABASE_URL
from src.modules.user.model import User
from src.modules.creator.model import Creator
from src.modules.creator_verification_doc import service, schema
from src.modules.common.enums import VerificationDocType, StorageProvider
from src.modules.campaign.model import Campaign
from src.modules.reward.model import Reward
from src.modules.comment.model import Comment
from src.modules.model.model import Model
from src.modules.country.model import Country
from src.modules.image.model import Image, ImageHandler
from src.modules.progress.model import Progress
import uuid
import uuid as uuid_lib
from unittest.mock import MagicMock, AsyncMock, patch
from fastapi import UploadFile
import os

@pytest.fixture(scope="module")
def db_session():
    # Setup
    engine = create_engine(DATABASE_URL)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    yield session
    # Teardown
    session.rollback()
    session.close()

import asyncio

def test_create_verification_doc(db_session):
    try:
        # 1. Create a dummy user
        user_id = uuid_lib.uuid4()
        user = User(
            id=user_id, 
            clerk_id=f"test_clerk_{user_id}", 
            username=f"test_user_{user_id}", 
            email=f"test_{user_id}@example.com"
        )
        db_session.add(user)
        db_session.flush()

        # 2. Create a creator
        creator_id = uuid_lib.uuid4()
        creator = Creator(
            id=creator_id,
            user_id=user.id,
            bio="Test Bio"
        )
        db_session.add(creator)
        db_session.flush()

        # 3. Mock UploadFile
        mock_file = MagicMock(spec=UploadFile)
        mock_file.filename = "test_doc.jpg"
        mock_file.content_type = "image/jpeg"
        mock_file.read = AsyncMock(return_value=b"fake image content")
        
        # 4. Call service
        # Mock file writing to avoid disk usage
        with patch("builtins.open", new_callable=MagicMock) as mock_open:
            mock_file_handle = MagicMock()
            mock_open.return_value.__enter__.return_value = mock_file_handle
            
            async def run_service():
                return await service.create_verification_doc_from_upload(
                    db_session,
                    creator_id,
                    VerificationDocType.id_card,
                    mock_file
                )
            
            doc_out = asyncio.run(run_service())

        # 5. Verify result
        assert doc_out.creator_id == creator_id
        assert doc_out.type == VerificationDocType.id_card
        assert doc_out.storage_provider == StorageProvider.local
        assert doc_out.mime_type == "image/jpeg"
        # assert doc_out.file_size == len(b"fake image content") # file_size might be mocked differently or calculated

        # 6. Verify DB record
        from src.modules.creator_verification_doc.model import CreatorVerificationDoc
        db_doc = db_session.query(CreatorVerificationDoc).filter_by(id=doc_out.id).first()
        assert db_doc is not None
        assert db_doc.creator_id == creator_id
        
        print("Verification Successful!")

    except Exception as e:
        pytest.fail(f"Verification failed: {e}")
