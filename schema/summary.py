from typing import List

from pydantic import BaseModel


class WordCounter(BaseModel):
    word: str
    count: int


class Country(BaseModel):
    title: str
    share: float


class Summary(BaseModel):
    positive_summary: str = ""
    negative_summary: str = ""
    positive_words: List[WordCounter] = []
    negative_words: List[WordCounter] = []
    median_playtime: int = 0
    countries: List[Country] = []
