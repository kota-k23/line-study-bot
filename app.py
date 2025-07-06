from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, StickerMessage
import os
from datetime import datetime

app = Flask(__name__)

# 環境変数からLINEの認証情報を取得
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# 開始時刻を一時保存する辞書（永続保存はまだしない）
start_times = {}

@app.route("/")
def home():
    return "LINE Bot is running!"

@app.route("/webhook", methods=["POST"])
def webhook():
    signature = request.headers["X-Line-Signature"]
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return "OK"

@handler.add(MessageEvent, message=TextMessage)
def handle_text(event):
    user_id = event.source.user_id
    text = event.message.text.strip()

    if text == "始めます":
        start_times[user_id] = datetime.now()
        reply = "スタート時間を記録しました！集中してがんばってください💪"
    elif text == "終わります":
        if user_id in start_times:
            start = start_times.pop(user_id)
            end = datetime.now()
            duration = end - start
            minutes = duration.seconds // 60
            hours = minutes // 60
            minutes %= 60
            reply = f"お疲れさまでした！勉強時間は {hours}時間{minutes}分 でした📝"
        else:
            reply = "「始めます」の記録がないので、まずは「始めます」と送ってね！"
    else:
        reply = "「始めます」か「終わります」と送ってね！"

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply)
    )

@handler.add(MessageEvent, message=StickerMessage)
def handle_sticker(event):
    reply = "スタンプを受け取りました！（今はテキストのみ対応中）"
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply)
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
