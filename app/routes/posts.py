from typing import List

from fastapi import APIRouter

from schema.post import Post
from services.blog_service import blog_service

router = APIRouter()


@router.get("/posts", response_model=List[Post])
async def get_posts(
    blog_url: str = "https://teletype.in/@sadari", category: str = ""
) -> List[Post]:
    """Get all posts from teletype"""
    posts = blog_service.get_all_posts(url=blog_url, category=category)
    return posts
