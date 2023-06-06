from datetime import datetime
import pytz
import guidance
from dotenv import load_dotenv

from chatkun.services.news_service import NewsArticle, NewsService


class TweetBot:
    def __init__(self, article: NewsArticle):
        self.article = article

    def __call__(self):
        # LLMを設定
        gpt = guidance.llms.OpenAI('gpt-3.5-turbo')

        # プロンプトを読み込み
        with open("./chatkun/bots/tweet_bot.handlebars", "r") as f:
            prompt = f.read()

        # 関数の生成
        bot = guidance(prompt, llm=gpt, caching=False)

        # 現在時刻を取得
        jst = pytz.timezone('Asia/Tokyo')
        now = datetime.now(jst)

        # 会話の生成
        out = bot(
            current_time=now.strftime('%Y-%m-%d %H:%M:%S'),
            article=self.article.dict()
        )
        return f"{out['message']}\n{self.article.url}"


if __name__ == "__main__":
    load_dotenv()
    article = NewsService.get_headline()
    bot = TweetBot(article)
    print(bot())
