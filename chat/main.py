import openai
import os

from dotenv import load_dotenv

from taipy.gui import State, Gui

load_dotenv()

context = "The following is a conversation with an AI assistant. The assistant is helpful, creative, clever, and very friendly.\n\nHuman: Hello, who are you?\nAI: I am an AI created by OpenAI. How can I help you today? "
conversation = {
    "Conversation": ["Who are you?", "Hi! I am GPT-3. How can I help you today?"]
}
current_user_message = ""

client = openai.Client(api_key=os.environ.get("OPENAI_KEY"))


def request(state: State, prompt: str) -> str:
    response = state.client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": f"{prompt}",
            },
        ],
        model="gpt-3.5-turbo",
    )

    return response.choices[0].message.content


def send_message(state: State) -> None:
    state.context += f"Human: \n {state.current_user_message}\n\n AI:"
    answer = request(state, state.context).replace("\n", "")
    state.context += answer
    conv = state.conversation._dict.copy()
    conv["Conversation"] += [state.current_user_message, answer]
    state.conversation = conv
    state.current_user_message = ""


def style_conv(_: State, idx: int) -> str:
    if idx is None:
        return None
    elif idx % 2 == 0:
        return "user_msg"
    else:
        return "gpt_msg"


page = """
<|{conversation}|table|show_all|width=100%|style=style_conv|>
<|{current_user_message}|input|label=Write your message here...|on_action=send_message|class_name=fullwidth|>
"""

if __name__ == "__main__":
    Gui(page).run(title="TaipyGPT")
