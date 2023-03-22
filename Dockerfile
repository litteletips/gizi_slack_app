# ベースイメージの指定
FROM python:3.11

# 必要なライブラリをインストール
RUN pip install slack-sdk slack-bolt openai python-dotenv requests

# コードをコンテナ内にコピー
WORKDIR /app
COPY . /app

# ポートの指定
EXPOSE 3000

# 環境変数の設定
ENV SLACK_APP_TOKEN=<YOUR_SLACK_APP_TOKEN>
ENV SLACK_BOT_TOKEN=<YOUR_SLACK_BOT_TOKEN>
ENV OPENAI_API_KEY=<YOUR_OPENAI_API_KEY>

# コマンドの指定
CMD ["python", "whisper_slack_bot.py"]