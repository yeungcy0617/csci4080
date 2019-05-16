import telepot
import threading
import base64
import json
import pickle
import requests
from telepot.loop import MessageLoop
from redis import StrictRedis

r = StrictRedis(host='localhost', port=6379)

def thread1(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    if content_type == 'photo':
        message = {'chat_id' : chat_id, 'file_id' : msg['photo'][-1]['file_id']}
    if content_type == "text":
        message = {'chat_id' : chat_id, 'url' : msg["text"]}
    r.rpush('download', json.dumps(message).encode("utf-8"))

def thread2():
    while True:
        msg = json.loads(r.blpop('prediction'))
        result = ""
        i=1
        for item in json.loads(msg['prediction']):
            result += "{0}. {1} ({2})\n".format(i,item['label'],item['prob'])
            i+=1
        bot.sendMessage(msg['chat_id'], result)


if __name__ == "__main__":
    bot = telepot.Bot("796097683:AAH5A4rKYanUq3ou2plYhGNjlrLb--EArDM")
    MessageLoop(bot, thread1).run_as_thread()
    thread2 = threading.Thread(target=thread2, daemon=False)
    thread2.start()
    while True:
        time.sleep(10)
