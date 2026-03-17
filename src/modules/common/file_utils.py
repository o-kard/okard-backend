from fastapi import UploadFile, HTTPException

def validate_image_size(file: UploadFile, max_size_mb: int = 5, max_video_size_mb: int = 50):
    """
    Validates the size of an uploaded file.
    Default: 5MB for images, 50MB for videos.
    """
    if not file:
        return

    is_video = file.content_type and file.content_type.startswith("video/")
    limit_mb = max_video_size_mb if is_video else max_size_mb
    
    # Seek to end to get size, then back to start
    file.file.seek(0, 2)
    size_bytes = file.file.tell()
    file.file.seek(0)

    if size_bytes > limit_mb * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail=f"File {file.filename} exceeds the {limit_mb}MB limit."
        )
