import time
import telepot
from telepot.loop import MessageLoop
from sklearn.externals import joblib

model = joblib.load('model.pkl')
def handle(msg):
    """
    A function that will be invoked when a message is
    recevied by the bot
    """
    content_type, chat_type, chat_id = telepot.glance(msg)

    if content_type == "text":
        content = msg["text"]
        score = round(float(model.predict_proba([content])[0][1]),2)
        if score >= 0.5:
            reply = "This is a positive review! ("+score+")"
        else:
            reply = "This is a negative review! ("+score+")"            
        bot.sendMessage(chat_id, reply)

if __name__ == "__main__":
    bot = telepot.Bot("796097683:AAH5A4rKYanUq3ou2plYhGNjlrLb--EArDM

")
    MessageLoop(bot, handle).run_as_thread()
    while True:
        time.sleep(10)