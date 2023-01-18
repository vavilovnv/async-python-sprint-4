from fastapi import HTTPException, status

from models import Link


def validate_link(obj: Link) -> None:
    if not obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Url not found'
        )
    if not obj.is_active:
        raise HTTPException(
            status_code=status.HTTP_410_GONE, detail='Url deleted'
        )
