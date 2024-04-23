import openai
import os

from dotenv import load_dotenv

from taipy.gui import State, Gui, invoke_callback, get_state_id

load_dotenv()

context = ""
conversation = {"Conversation": []}
current_user_message = ""

client = openai.Client(api_key=os.environ.get("OPENAI_KEY"))

max_input_token = 4096
system_message = "The following is a conversation with an AI assistant. The assistant is helpful, creative, clever, and very friendly."
temperature = 0
top_p = 0
frequency_penalty = 0


def request(state: State, prompt: str) -> str:
    response = state.client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": f"{state.system_message}\n\n{prompt}",
            },
        ],
        model="gpt-3.5-turbo",
        frequency_penalty=state.frequency_penalty,
        max_tokens=state.max_input_token,
        top_p=state.top_p,
        temperature=state.temperature,
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


def update_state(state: State, resp: str):
    conv = state.conversation._dict.copy()

    state.context += resp

    conv["Conversation"][-1] += resp
    state.conversation = conv


def send_message_stream(state: State) -> None:
    state.context += f"Human: \n {state.current_user_message}\n\n AI: &nbsp;"
    curr_msg = state.current_user_message

    conv = state.conversation._dict.copy()
    conv["Conversation"] += [curr_msg, "..."]
    state.conversation = conv

    state.current_user_message = ""

    response = state.client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": f"{state.context}",
            },
        ],
        model="gpt-3.5-turbo",
        stream=True,
    )

    for chunk in response:
        if chunk.choices[0].delta.content is not None:
            resp = chunk.choices[0].delta.content

            invoke_callback(gui, get_state_id(state), update_state, [resp])


def style_conv(_: State, idx: int) -> str:
    if idx is None:
        return None
    elif idx % 2 == 0:
        return "user_msg"
    else:
        return "gpt_msg"


page = """
<|layout|columns=1fr 320px|
<|layout|class_name=chat-box|
<|{conversation}|table|show_all|width=100%|style=style_conv|>
<|{current_user_message}|input|label=Write your message here...|on_action=send_message|class_name=fullwidth|>
|>
<|
System Message
<|{system_message}|input|class_name=fullwidth|class_name=form__control|>
Max Input Token
<|{max_input_token}|number|class_name=fullwidth|class_name=form__control|>
Temperature
<|{temperature}|slider|min=0.0|max=1.0|step=0.01|continuous=False|class_name=form__control|>
Top P
<|{top_p}|slider|min=0.0|max=1.0|step=0.01|continuous=False|class_name=form__control|>
Frequency Penalty
<|{frequency_penalty}|slider|min=-2.0|max=2.0|step=0.01|continuous=False|class_name=form__control|>
|>
|>
"""

gui = Gui(page)

if __name__ == "__main__":
    Gui(page).run(title="TaipyGPT", use_reloader=True)
