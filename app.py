import os
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import pyshorteners

# 環境変数からトークンを取得
LINE_CHANNEL_ACCESS_TOKEN = os.environ["LINE_CHANNEL_ACCESS_TOKEN"]
LINE_CHANNEL_SECRET = os.environ["LINE_CHANNEL_SECRET"]


app = Flask(__name__)


line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

header = {
    "Content_Type": "application/json",
    "Authorization": "Bearer " + LINE_CHANNEL_ACCESS_TOKEN
}

@app.route("/")
def hello_world():
    return "Hello World!"


# アプリにPOSTがあったときの処理
@app.route("/callback", methods=["POST"])
def callback():
    # get X-Line-Signature header value
    signature = request.headers["X-Line-Signature"]
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return "OK"


# botにメッセージを送ったときの処理
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    # もしメッセージがURLであれば、そのURLを短縮する
    if event.message.text.startswith("http"):
        # URLを短縮する
        s = pyshorteners.Shortener()
        url = s.tinyurl.short(event.message.text)
        # 短縮したURLを返す
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=url))
    # もしメッセージが短縮されたURLであれば、そのURLを展開する
    elif event.message.text.startswith("https://tinyurl.com/"):
        # URLを展開する
        s = pyshorteners.Shortener()
        url = s.tinyurl.expand(event.message.text)
        # 展開したURLを返す
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=url)) 
    else:
        # 「不正なURLです」と返す
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="不正なURLです"))

# アプリの起動
if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
### End