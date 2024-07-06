from typing import List

import requests
from bs4 import BeautifulSoup

from schema.post import Post


class BlogService:
    @staticmethod
    def get_all_posts(url: str, category: str = "") -> List[Post]:
        if category:
            url = f"{url}/+{category}"
        response = requests.get(url)
        posts: List[Post] = []
        if response.status_code != 200:
            return posts

        soup = BeautifulSoup(response.content.decode("utf-8"), "html.parser")
        blog = soup.find("div", class_="blog__articles_list")
        posts_raw = blog.find_all("a", class_="blogArticleCut")

        for i, pr in enumerate(posts_raw):
            title = pr.find("h2", class_="blogArticleCut__title").get_text(strip=True)
            url = pr["href"]
            description = (
                pr.find("div", class_="blogArticleCut__text")
                .find("p")
                .get_text(strip=True)
            )
            image = pr.find("div", class_="blogArticleCut__text").find("img")["src"]

            post = Post(
                id=i, url=url, title=title, description=description, image=image
            )

            posts.append(post)

        return posts


blog_service = BlogService()
