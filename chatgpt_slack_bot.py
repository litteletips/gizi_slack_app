import os
from io import BytesIO
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from dotenv import load_dotenv
import openai
import requests

load_dotenv()

SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]
SLACK_APP_TOKEN = os.environ["SLACK_APP_TOKEN"]
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]

app = App(token=SLACK_BOT_TOKEN)
client = WebClient(token=SLACK_BOT_TOKEN)
openai.api_key = OPENAI_API_KEY


def handle_event(event, say):
    input_message = event["text"]
    thread_ts = event.get("thread_ts")
    channel = event["channel"]
    input_message = input_message.replace("@chatGPTBOT", "")

    if "議事録" in input_message:
        system_message = """
            lang : jp
            You have over 20 years of experience as an IT consultant and have worked on a wide variety of industries and types of projects related to IT consulting.
            You will be in charge of writing the minutes of the meeting, using your knowledge of IT and consulting to ensure that the chapters are properly organized by topic, that the points of discussion are easy to understand, and that there are no typographical errors or omissions.
            """
        split_string = input_message.split("----", 1)
        if len(split_string) < 2:
            output = ""
            say(text=text, channel=channel)
        else:
            input_message = f"""以下は、ある会議の書き起こしです。
            {split_string[1]}
            この会議の議事録を作成してください。議事録は、以下のような形式で書いてください。
            - 決定事項
            - TODO
            - 会議のテーマごとの章立て
            - 章ごとの議事
            サマリー:
            """
    else:
        system_message = """
        """

        # system_message = """
        # #lang : jp
        # You have over 20 years of experience as an IT consultant and have worked on a wide variety of industries and types of projects related to IT consulting. 
        # Answer as concisely as possible.
        # """

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": input_message}
        ]
    )
    text = response["choices"][0]["message"]["content"]
    if thread_ts is not None:
        parent_thread_ts = event["thread_ts"]
        say(text=text, thread_ts=parent_thread_ts, channel=channel)
    else:
        say(text=text, channel=channel)


@app.event("app_mention")
def app_mention(event, say):
    handle_event(event, say)


if __name__ == "__main__":
    handler = SocketModeHandler(app, SLACK_APP_TOKEN)
    handler.start()