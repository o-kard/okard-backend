import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from src.database.db import DATABASE_URL
from src.modules.post.model import Post, PostState, PostStatus, PostCategory
from src.modules.campaign.model import Campaign
from src.modules.reward.model import Reward
from src.modules.comment.model import Comment
from src.modules.model.model import Model
from src.modules.country.model import Country
from src.modules.image.model import Image, ImageHandler
from src.modules.common.enums import ReferenceType
from src.modules.user.model import User
import uuid
import uuid as uuid_lib

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

def test_create_post_with_image_handler(db_session):
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

        # 2. Create a post
        post_id = uuid_lib.uuid4()
        post = Post(
            id=post_id,
            user_id=user.id,
            post_header="Test Post Schema Verification",
            post_description="Content for schema verification",
            status=PostStatus.active,
            state=PostState.published,
            category=PostCategory.other
        )
        db_session.add(post)
        db_session.flush()

        # 3. Create images
        img1_id = uuid_lib.uuid4()
        img2_id = uuid_lib.uuid4()
        img1 = Image(id=img1_id, path="path/1.jpg", orig_name="1.jpg", display_order=1)
        img2 = Image(id=img2_id, path="path/2.jpg", orig_name="2.jpg", display_order=2)
        db_session.add(img1)
        db_session.add(img2)
        db_session.flush()

        # 4. Create ImageHandlers linking images to post
        h1 = ImageHandler(image_id=img1.id, reference_id=post.id, type=ReferenceType.post)
        h2 = ImageHandler(image_id=img2.id, reference_id=post.id, type=ReferenceType.post)
        db_session.add(h1)
        db_session.add(h2)
        db_session.flush()
        
        # 5. Refresh post to load relationships
        # We expire the session to force reload from DB
        db_session.expire(post)
        
        # 6. Verify relationships
        # Accessing post.images should trigger the secondary join via ImageHandler
        loaded_images = post.images
        
        print(f"Loaded {len(loaded_images)} images for post {post.id}")
        assert len(loaded_images) == 2, "Should have 2 images associated via ImageHandler"
        
        loaded_ids = {img.id for img in loaded_images}
        assert img1.id in loaded_ids
        assert img2.id in loaded_ids
        
        # Verify display_order
        # Sort by display_order
        sorted_images = sorted(loaded_images, key=lambda x: x.display_order)
        assert sorted_images[0].id == img1.id
        assert sorted_images[0].display_order == 1
        assert sorted_images[1].id == img2.id
        assert sorted_images[1].display_order == 2

        print("Verification Successful!")
        
    except Exception as e:
        pytest.fail(f"Verification failed: {e}")
