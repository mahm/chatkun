import os
import logging

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from slack_bolt.async_app import AsyncApp
from slack_bolt.adapter.fastapi.async_handler import AsyncSlackRequestHandler

from chatkun.database import setup_database
from chatkun.services.bot_service import BotService

# Loggerの設定
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# 環境変数の読み込み
load_dotenv()
SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN")
SLACK_SIGNING_SECRET = os.environ.get("SLACK_SIGNING_SECRET")
SLACK_BOT_ID = os.environ.get("SLACK_BOT_ID")
DATABASE_URL = os.environ.get("DATABASE_URL")

# データベースの設定
logger.info(f"DATABASE_URL: {DATABASE_URL}")
session_maker = setup_database(DATABASE_URL)

# Slack APIのクライアントを作成
app = AsyncApp(token=os.environ["SLACK_BOT_TOKEN"], signing_secret=SLACK_SIGNING_SECRET)
handler = AsyncSlackRequestHandler(app)
api = FastAPI()


@app.event("message")
async def handle_message_event(message, say):
    # slackからの情報を取得する
    input_message = message["text"]
    ts = message["ts"]
    thread_ts = message.get("thread_ts") or None
    channel = message["channel"]
    user_id = message["user"]

    log_message = f"receive: channel={channel} user_id={user_id} input_message={input_message}"
    logger.info(log_message)

    bot_service = BotService(session_maker, app, say, SLACK_BOT_ID, user_id, channel, ts, thread_ts)
    await bot_service.do_reply(say, input_message)


@api.post("/slack/events")
async def handle_slack_events(req: Request):
    return await handler.handle(req)


@api.get("/healthcheck")
async def healthcheck():
    return {"status": "OK"}


if __name__ == "__main__":
    logger.info("====starting slack bot====")
    app.start(port=int(os.environ.get("PORT", 3000)))
