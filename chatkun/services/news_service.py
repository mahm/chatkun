import os
import random

from newsapi import NewsApiClient
from pydantic.main import BaseModel


class NewsArticle(BaseModel):
    title: str
    description: str
    url: str
    content: str


class NewsService:
    @staticmethod
    def get_headline() -> NewsArticle:
        """News APIからテクノロジ関連のヘッドラインを取得する"""
        # News APIのクライアントを作成
        newsapi = NewsApiClient(api_key=os.environ["NEWS_API_KEY"])

        # News APIからテクノロジ関連のヘッドラインを取得する
        top_headlines = newsapi.get_top_headlines(
            category="technology"
        )

        # ヘッドラインを取得できなかった場合はNoneを返す
        if top_headlines["status"] != "ok" or top_headlines["totalResults"] == 0:
            return None

        # ヘッドラインをランダムに選択する
        articles = top_headlines["articles"]
        article = random.sample(articles, k=1)[0]

        # ヘッドラインを返す
        return NewsArticle(**article)
