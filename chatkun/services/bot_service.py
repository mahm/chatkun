from typing import List

from chatkun.bots.conversation_bot import ConversationBot
from chatkun.bots.tweet_bot import TweetBot
from chatkun.services.slack_message_service import SlackMessageService


class BotService:
    def __init__(self, session_maker, slack_app, slack_bot_id: str):
        self.slack_app = slack_app
        self.slack_bot_id = slack_bot_id
        self.slack_message_service = SlackMessageService(session_maker=session_maker)

    async def prepare_history(self, thread_ts, channel, user_id) -> (List[str], List[str]):
        user_messages = []
        assistant_messages = []
        if thread_ts is not None:
            thread_message = await self.slack_app.client.conversations_replies(
                channel=channel,
                ts=thread_ts
            )

            for message in thread_message["messages"]:
                if message["user"] == user_id and self.slack_bot_id in message["text"]:
                    user_messages.append(self.remove_slack_id_from_text(message["text"], self.slack_bot_id))
                elif message["user"] == self.slack_bot_id and user_id in message["text"]:
                    assistant_messages.append(self.remove_slack_id_from_text(message["text"], user_id))

        return user_messages, assistant_messages

    @staticmethod
    def remove_slack_id_from_text(text: str, slack_id: str) -> str:
        # メンション部を削除
        return text.replace(f"<@{slack_id}>", "").strip()

    async def do_reply(self, say, input_message: str, user_id: str, channel: str, ts: str,
                       thread_ts: str) -> None:

        user_messages, assistant_messages = await self.prepare_history(thread_ts, channel, user_id)

        bot = ConversationBot(
            user_messages=user_messages,
            assistant_messages=assistant_messages
        )

        try:
            reply_text = bot(
                self.remove_slack_id_from_text(input_message, self.slack_bot_id)
            )
            reply_text = f"<@{user_id}>\n{reply_text}"
        except Exception as e:
            reply_text = f"<@{user_id}>\nごめんなさい。現在サーバーの負荷が高いため処理できませんでした。時間をおいて再度質問してください。"

        # 返信先スレッドを求める
        if thread_ts is not None:
            thread_ts = thread_ts
        else:
            response = await self.slack_app.client.conversations_replies(
                channel=channel,
                ts=ts
            )
            thread_ts = response["messages"][0]["ts"]

        # メッセージをDBに保存
        self.slack_message_service.add_message(
            text=input_message,
            thread_ts=thread_ts,
            channel=channel,
            user_id=user_id
        )
        self.slack_message_service.add_message(
            text=self.remove_slack_id_from_text(reply_text, user_id),
            thread_ts=thread_ts,
            channel=channel,
            user_id=self.slack_bot_id
        )

        # Slackに送信
        await say(text=reply_text, thread_ts=thread_ts, channel=channel)

    async def tweet(self, channel_id: str) -> None:
        # 直近のメッセージを取得
        messages = self.slack_message_service.get_recent_messages(slack_bot_id=self.slack_bot_id)
        texts = [message.text for message in messages]
        bot = TweetBot(recent_messages=texts)
        bot_message = bot()
        await self.slack_app.client.chat_postMessage(channel=channel_id, text=bot_message)
