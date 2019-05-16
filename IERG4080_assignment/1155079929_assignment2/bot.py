import time
import telepot
import responses
from telepot.loop import MessageLoop
from sklearn.externals import joblib
from PIL import Image
import requests
from io import BytesIO
import socket
import base64
from io import BytesIO
from PIL import Image
import queue
import threading
import json
import socket
import sys

Queue1 = queue.Queue() 
Queue2 = queue.Queue()


def thread4():
    
    while True:
        
        if(Queue1.empty()):
            continue
            
        # create an INET TCP socket
        soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # connect to the server (change localhost to an IP address if necessary)
        soc.settimeout(500)
        soc.connect(("localhost", 50002))
        print("Connected to server")

        # Send a message to the server
        msg = "Hello Server!".encode("utf-8")
        
        image,chat_id = Queue1.get()
        
        data = {
        'image': image,
        'chat_id': chat_id
        }

        json_data=json.dumps(data)
        json_data+=('##END##')
        
        json_data=json_data.encode('utf-8')
        soc.sendall(json_data)

        
        data_1 = soc.recv(1024) 
        Queue2.put(data_1.decode())
        Queue2.put(chat_id)
    
    
def thread5():
    while True:
        
        if(Queue2.empty()):
            continue
        msg = Queue2.get()
        chatid = Queue2.get()
        bot.sendMessage(chatid,msg)

#model = joblib.load('model.pkl')
def handle(msg):
    """
    A function that will be invoked when a message is
    recevied by the bot
    """
    content_type, chat_type, chat_id = telepot.glance(msg)

    
    
    if content_type == 'photo':
        bot.download_file(msg['photo'][-1]['file_id'], './file.png')

       
    
        
    
    if content_type == "text":
        with open('./file.png', 'wb') as handle:
            for block in requests.get(msg["text"], stream=True).iter_content(1024):
                if not block:
                    break
                handle.write(block)

    image = Image.open('./file.png')
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    encoded_image = base64.b64encode(buffered.getvalue()).decode('ascii')

    #         data = {
    #     'image': encoded_image,
    #     'chat_id': chat_id
    # }

    Queue1.put((encoded_image,chat_id))

    
    
    
if __name__ == "__main__":
    bot = telepot.Bot("796097683:AAH5A4rKYanUq3ou2plYhGNjlrLb--EArDM")
    thread2 = threading.Thread(target=thread4,daemon=False)
    thread2.start()
    thread3 = threading.Thread(target=thread5,daemon=False)
    thread3.start()
    
    MessageLoop(bot, handle).run_as_thread()
    while True:
        time.sleep(10)