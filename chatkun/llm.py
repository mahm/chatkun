from typing import List

import guidance


class ConversationBot:
    def __init__(self, user_messages: List[str], assistant_messages: List[str]):
        self.user_messages = user_messages
        self.assistant_messages = assistant_messages

    def conversation_data(self) -> List[dict]:
        conversations = []
        for user, assistant in zip(self.user_messages, self.assistant_messages):
            conv = {"user": user, "assistant": assistant}
            conversations.append(conv)
        return conversations

    def __call__(self, user_input: str):
        # LLMを設定
        gpt = guidance.llms.OpenAI('gpt-3.5-turbo')

        # プロンプトを読み込み
        with open("./chatkun/chatbot.handlebars", "r") as f:
            prompt = f.read()

        # 関数の生成
        bot = guidance(prompt, llm=gpt)

        # 会話の生成
        out = bot(conversations=self.conversation_data(), user_input=user_input)
        return out['reply']


if __name__ == "__main__":
    print('===== start conversation =====')
    user_messages = []
    assistant_messages = []
    while True:
        user_input = input("Human: ")
        bot = ConversationBot(
            user_messages=user_messages,
            assistant_messages=assistant_messages
        )
        response = bot(user_input)
        print("AI: ", response)
        user_messages.append(user_input)
        assistant_messages.append(response)
