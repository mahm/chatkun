from typing import List
from datetime import datetime
import pytz
import guidance


class TweetBot:
    def __init__(self, recent_messages: List[str]):
        self.recent_messages = recent_messages

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
            recent_messages=self.recent_messages,
            empty=(not self.recent_messages)
        )
        return out['message']


if __name__ == "__main__":
    recent_messages = [
        '今日は暑いね',
        '昨日は遊園地に行ったよ',
        '富士山の雪が溶けていたよ'
    ]
    print('recent_message: 3')
    tweet_bot = TweetBot(recent_messages=recent_messages)
    print(tweet_bot())
    print('recent_message: 0')
    tweet_bot = TweetBot(recent_messages=[])
    print(tweet_bot())
