import re
import urllib.parse
from collections import defaultdict
from dataclasses import dataclass
import random
from typing import List

import numpy as np
import requests

from schema.summary import Country, Summary, WordCounter
# from utils.lemmatizer import lemmatizer
from utils.stopwords import STOP_WORDS


@dataclass
class Review:
    language: str
    review: str
    playtime_at_review: float  # minutes


class SummaryService:
    DAY_RANGE = 9223372036854775807
    BATCH_SIZE = 100
    REVIEW_URL_TEMPLATE = (
        "https://store.steampowered.com/appreviews/{gameid}"
        "?json=1&num_per_page={batch_size}&day_range={day_range}"
        "&language={language}&cursor={cursor}&filter={filter}"
        "&review_type={review_type}"
    )

    @staticmethod
    def clean_review_text(text: str) -> str:
        # remove [anything] including brackets
        text = re.sub(r"\[.*?\]", "", text)
        # remove \word (backslash followed by non-space characters)
        text = re.sub(r"\\\S+", "", text)
        text = text.replace("\n", "")
        # keep only english, numbers and some special characters
        text = re.sub(r"[^a-zA-Z0-9,\.\!\?\- ]", "", text)
        return text.strip()

    @staticmethod
    def get_top_words(text: str, top_n: int = 10) -> List[WordCounter]:
        text = text.lower()
        text = re.sub(r"[^\w\s]", "", text)

        words = text.split()
        words_cnt = defaultdict(int)
        for word in words:
            #lemma = lemmatizer.lemmatize(word)
            if word in STOP_WORDS:
                continue
            words_cnt[word] += 1

        words = [
            WordCounter(word=word, count=count) for word, count in words_cnt.items()
        ]

        words.sort(key=lambda c: c.count, reverse=True)
        return words[:top_n]

    @staticmethod
    def get_countries_dist_from_reviews(reviews: List[Review]) -> List[Country]:
        countries_cnt = defaultdict(int)
        for review in reviews:
            countries_cnt[review.language] += 1

        total = sum(countries_cnt.values())
        countries = [
            Country(title=lang, share=round(count / total, 2))
            for lang, count in countries_cnt.items()
        ]

        countries.sort(key=lambda c: c.share, reverse=True)
        return countries

    def parse_reviews(
        self,
        gameid: int,
        review_type: str,
        sort: str,
        language: str,
        max_reviews: int = 100,
    ) -> List[Review]:
        cursor = "*"
        current_reviews = 0
        reviews = []

        while True and current_reviews < max_reviews:
            url = self.REVIEW_URL_TEMPLATE.format(
                gameid=gameid,
                batch_size=self.BATCH_SIZE,
                day_range=self.DAY_RANGE,
                cursor=cursor,
                filter=sort,
                language=language,
                review_type=review_type,
            )
            response = requests.get(url)
            data = response.json()

            for r in data.get("reviews", []):
                reviews.append(
                    Review(
                        language=r.get("language", ""),
                        review=r.get("review", ""),
                        playtime_at_review=r.get("author", {}).get(
                            "playtime_at_review", 0.0
                        ),
                    )
                )

            next_cursor = urllib.parse.quote(data.get("cursor", ""))
            if not next_cursor or next_cursor == cursor:
                break

            cursor = next_cursor
            current_reviews += self.BATCH_SIZE

        return reviews

    def get_summary(self, gameid: int) -> Summary:
        def fetch_and_clean(review_type: str) -> list[str]:
            reviews = self.parse_reviews(
                gameid=gameid,
                review_type=review_type,
                sort="all",
                language="english",
                max_reviews=100,
            )
            cleaned_reviews = [self.clean_review_text(r.review) for r in reviews]
            return cleaned_reviews

        positive_reviews = fetch_and_clean("positive")
        positive_text = " ".join(positive_reviews)
        positive_summary = random.choice(positive_reviews)
        top_positive_words = self.get_top_words(positive_text, top_n=10)

        negative_reviews = fetch_and_clean("negative")
        negative_text = " ".join(negative_reviews)
        negative_summary = random.choice(negative_reviews)
        top_negative_words = self.get_top_words(negative_text, top_n=10)

        recent_reviews = self.parse_reviews(
            gameid=gameid,
            review_type="all",
            sort="recent",
            language="all",
            max_reviews=100,
        )
        countries = self.get_countries_dist_from_reviews(reviews=recent_reviews)
        median_playtime = round(
            np.median([r.playtime_at_review for r in recent_reviews])
        )

        summary = Summary(
            positive_summary=positive_summary,
            positive_words=top_positive_words,
            negative_summary=negative_summary,
            negative_words=top_negative_words,
            countries=countries,
            median_playtime=median_playtime,
        )

        return summary


summary_service = SummaryService()
