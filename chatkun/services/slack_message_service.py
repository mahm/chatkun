from datetime import datetime, timedelta

from chatkun.database import SlackMessage


class SlackMessageService:
    def __init__(self, session_maker):
        self.session_maker = session_maker

    def add_message(self, text, thread_ts, channel, user_id):
        session = self.session_maker()
        try:
            message = SlackMessage(
                text=text,
                thread_ts=thread_ts,
                channel=channel,
                user_id=user_id,
                created_at=datetime.now(),
            )
            session.add(message)
            session.commit()
        except Exception as e:
            print(f"An error occurred: {e}")
            session.rollback()
        finally:
            session.close()

    def get_recent_messages(self, slack_bot_id):
        session = self.session_maker()
        try:
            one_day_ago = datetime.now() - timedelta(days=1)
            messages = session.query(SlackMessage).filter(
                SlackMessage.created_at >= one_day_ago,
                SlackMessage.user_id != slack_bot_id,
            ).all()
            return messages
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            session.close()
