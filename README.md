# gizi_slack_app

## 以下のコマンドでDockerコンテナを起動
docker run -e SLACK_APP_TOKEN=<YOUR_APP_TOKEN> -e SLACK_BOT_TOKEN=<YOUR_BOT_TOKEN> -e OPENAI_API_KEY=<YOUR_OPENAI_API_KEY> -p 3000:3000 slack-bot
