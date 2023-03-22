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
ALLOWED_FILE_TYPES = ["mp3", "mp4", "mpeg", "m4a", "mpga", "webm", "wav"]
MAX_FILE_SIZE = 25 * 1024 * 1024

app = App(token=SLACK_BOT_TOKEN)
client = WebClient(token=SLACK_BOT_TOKEN)
openai.api_key = OPENAI_API_KEY

def transcribe_audio(audio_data, language):
    # whisper APIへのリクエスト
    transcript = openai.Audio.transcribe("whisper-1", audio_data, language=language)
    return transcript

def handle_event(event, say):
    # ファイル添付がない場合には添付するようにメッセージを返す。
    if not ("files" in event): 
        output = "ファイルが見つかりません。以下、いずれかの形式のファイルを添付してください。\nmp3, mp4, mpeg, mpga, m4a, wav, webm"
    else:
        file = event["files"][0]
        filetype = file["filetype"]
        url = file["url_private"]
        filename = "temp." + filetype
        # ファイル形式が適さない場合は処理をしない。
        # Whisper APIの制限により現状は25MBを超える場合には処理をしない。
        if filetype not in ALLOWED_FILE_TYPES:
            output = "適合するファイルではありません。以下、いずれかの形式のファイルを添付してください。\nmp3, mp4, mpeg, mpga, m4a, wav, webm"
        elif file["size"] > MAX_FILE_SIZE:
            output = "ファイルサイズオーバー。ファイルサイズは25MBにしてください。"
        else:
            try:
                file_id = file["id"]
                audio_data = client.files_info(file=file_id)["file"]
                language = "en" if "english" in event["text"].casefold() else "ja"
                audio_file_download = requests.get(url, headers={'Authorization': 'Bearer %s' % os.environ["SLACK_BOT_TOKEN"]})
                # 一時ファイルへの書き込み
                with open(filename, 'wb') as f:
                    f.write(audio_file_download.content)
                # 音声ファイルの文字起こしを実施
                with open(filename, "rb") as audio_file:
                    transcript = transcribe_audio(audio_file, language)
                    title = file["title"]
                    output = f"文字起こし致しました：{title}.{filetype}\n----\n{transcript['text']}"
                    # 一時ファイルの削除
                    os.remove(filename)
            except SlackApiError as e:
                output = f"エラーが発生しました: {e.response['error']}"
    thread_ts = event.get("thread_ts")
    channel = event["channel"]
    if thread_ts:
        say(text=output, thread_ts=thread_ts, channel=channel)
    else:
        say(text=output, channel=channel)

@app.event("app_mention")
def app_mention(event, say):
    handle_event(event, say)


if __name__ == "__main__":
    handler = SocketModeHandler(app, SLACK_APP_TOKEN)
    handler.start() 