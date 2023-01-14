from fastapi import APIRouter

router = APIRouter()


@router.get('/')
def read_root():
    return 'Welcome to the URL shortener API'

