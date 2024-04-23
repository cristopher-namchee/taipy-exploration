import openai
import os

from dotenv import load_dotenv

from taipy.gui import (
    State,
    Gui,
    invoke_callback,
    get_state_id,
    invoke_long_callback,
    notify,
)

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


def update_state(state: State, resp: str):
    conv = state.conversation._dict.copy()

    state.context += resp

    if conv["Conversation"][-1] == "Thinking...":
        conv["Conversation"][-1] = ""

    conv["Conversation"][-1] += resp
    state.conversation = conv


def stream_message(gui, state_id, client, context):
    response = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": f"{context}",
            },
        ],
        model="gpt-3.5-turbo",
        frequency_penalty=frequency_penalty,
        max_tokens=max_input_token,
        top_p=top_p,
        temperature=temperature,
        stream=True,
    )

    for chunk in response:
        resp = chunk.choices[0].delta.content
        if resp is None:
            break

        invoke_callback(
            gui,
            state_id,
            update_state,
            [resp],
        )


def send_message_stream(state: State) -> None:
    state.context += f"Human: \n {state.current_user_message}\n\n AI: &nbsp;"
    curr_msg = state.current_user_message

    conv = state.conversation._dict.copy()
    conv["Conversation"] += [curr_msg, "Thinking..."]
    state.conversation = conv

    state.current_user_message = ""
    invoke_long_callback(
        state=state,
        user_function=stream_message,
        user_function_args=[gui, get_state_id(state), state.client, state.context],
    )


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
<|{current_user_message}|input|label=Write your message here...|on_action=send_message_stream|class_name=fullwidth a|>
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
    gui.run(title="TaipyGPT")
