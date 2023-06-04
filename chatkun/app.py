import os
import sys
import logging
from typing import List

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from slack_bolt.async_app import AsyncApp
from slack_bolt.adapter.fastapi.async_handler import AsyncSlackRequestHandler

from chatkun.llm import ConversationBot

# Loggerの設定
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# ハンドラーの設定
handler = logging.StreamHandler(sys.stdout)  # stdoutに出力するためのハンドラー
handler.setLevel(logging.INFO)  # ハンドラーのログレベルも設定

# フォーマッターの設定
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

# Loggerにハンドラーとフォーマッターをセット
logger.addHandler(handler)

# 環境変数の読み込み
load_dotenv()
SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN")
SLACK_SIGNING_SECRET = os.environ.get("SLACK_SIGNING_SECRET")
SLACK_BOT_ID = os.environ.get("SLACK_BOT_ID")  # 発行したBotのIDを設定

# Slack APIのクライアントを作成
app = AsyncApp(token=os.environ["SLACK_BOT_TOKEN"], signing_secret=SLACK_SIGNING_SECRET)
handler = AsyncSlackRequestHandler(app)
api = FastAPI()


def remove_slack_id_from_text(text: str, slack_id: str) -> str:
    # メンション部を削除
    return text.replace(f"<@{slack_id}>", "")


async def prepare_history(user_id: str, channel: str, thread_ts: str) -> (List[str], List[str]):
    user_messages = []
    assistant_messages = []
    if thread_ts is not None:
        thread_message = await app.client.conversations_replies(channel=channel, ts=thread_ts)

        for message in thread_message["messages"]:
            if message["user"] == user_id and SLACK_BOT_ID in message["text"]:
                user_messages.append(remove_slack_id_from_text(message["text"], SLACK_BOT_ID))
            elif message["user"] == SLACK_BOT_ID and user_id in message["text"]:
                assistant_messages.append(remove_slack_id_from_text(message["text"], user_id))

    return user_messages, assistant_messages


@app.event("message")
async def handle_message_event(message, say):
    # slackからの情報を取得する
    input_message = message["text"]
    thread_ts = message.get("thread_ts") or None
    channel = message["channel"]
    user_id = message["user"]

    log_message = f"receive: channel={channel} user_id={user_id} input_message={input_message}"
    logger.info(log_message)

    # 自分自身の発言は無視する
    if user_id == os.environ.get("SLACK_BOT_USER_ID"):
        return

    # slack botのIDがメッセージに含まれるので、削除する
    input_message = remove_slack_id_from_text(input_message, SLACK_BOT_ID)

    user_messages, assistant_messages = await prepare_history(user_id, channel, thread_ts)

    bot = ConversationBot(user_messages=user_messages, assistant_messages=assistant_messages)
    try:
        reply_text = bot(input_message)
        reply_text = f"<@{user_id}>\n{reply_text}"
    except Exception as e:
        reply_text = f"<@{user_id}>\nごめんなさい。現在サーバーの負荷が高いため処理できませんでした。時間をおいて再度質問してください。"

    # slackのスレッドに返信する
    if thread_ts is not None:
        parent_thread_ts = message["thread_ts"]
        await say(text=reply_text, thread_ts=parent_thread_ts, channel=channel)
    else:
        response = await app.client.conversations_replies(channel=channel, ts=message["ts"])
        thread_ts = response["messages"][0]["ts"]
        await say(text=reply_text, thread_ts=thread_ts, channel=channel)


@api.post("/slack/events")
async def handle_slack_events(req: Request):
    return await handler.handle(req)


@api.get("/healthcheck")
async def healthcheck():
    return {"status": "OK"}


if __name__ == "__main__":
    logger.info("====starting slack bot====")
    app.start(port=int(os.environ.get("PORT", 3000)))
