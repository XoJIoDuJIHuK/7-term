import random
import string

from fastapi import HTTPException, UploadFile


async def validate_file_size(file_: UploadFile, max_file_size_mb: int):
    """
    Asynchronously validate the size of an uploaded file.

    Args:
        file_ (UploadFile): The file to validate.
        max_file_size_mb (int): Maximum allowed file size in MB.

    Raises:
        HTTPException: If the file size exceeds the maximum allowed size.
    """
    file_size = 0
    chunk_size = 1024 * 1024

    while True:
        chunk = await file_.read(chunk_size)
        if not chunk:
            break
        file_size += len(chunk)
        if file_size > max_file_size_mb * chunk_size:
            raise HTTPException(
                status_code=413,
                detail=f'Uploaded file exceeds the maximum size of '
                       f'{max_file_size_mb} MB.'
            )

    await file_.seek(0)


def generate_random_string(length: int = 10):
    return ''.join(random.choices(string.ascii_uppercase, k=length))
