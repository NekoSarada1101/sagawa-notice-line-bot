from flask import Flask, request
from linebot import LineBotApi
from linebot.models import TextSendMessage
from linebot.exceptions import LineBotApiError
from settings import *

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/line', methods=['POST'])
def push_notice():
    post_data = request.get_data()  # type: str
    print(post_data.encode().decode('unicode-escape'))

    line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
    try:
        line_bot_api.push_message(USER_ID, TextSendMessage(text=post_data))
    except LineBotApiError as e:
        print(e)
    return "line"

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080)
