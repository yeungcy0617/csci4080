import socket
import time
import threading
import queue
import tensorflow as tf
import json
import base64
from keras.applications.resnet50 import ResNet50
from keras.preprocessing import image
from keras.applications.resnet50 import preprocess_input, decode_predictions
import numpy as np

Queue1 = queue.Queue() 

def Listen():


    # A indefinite loop
    while True:
        # create an INET socket
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # bind the socket to the host and a port
        server_socket.bind(("localhost", 50002))

        # Listen for incoming connections from clients
        server_socket.listen(1)
        # accept connections from outside
        (client_socket, address) = server_socket.accept()
        print("accepted connection from %s" % str(address))

        # Read data from client and send it back
        
        
        data = client_socket.recv(1024) 
        
        while True:
            if(b"##END" in data):
                break
            data += client_socket.recv(1024) 
            
        data=data[:-7]
        data=data.decode("utf-8")
            
            
        Queue1.put(data)
        Queue1.put(client_socket)

       
        
#         print("Received %s from %s" % (data.decode("utf-8"), address))

        

def Image():
    while True:
        if Queue1.empty():
            continue
        model = ResNet50(weights='imagenet')

        ImageData = Queue1.get()
        ReceiveData = json.loads(ImageData)
        BinaryImage = ReceiveData['image']
        image_data = base64.b64decode(BinaryImage)


        with open('image.png', 'wb') as outfile:
            outfile.write(image_data)

        img_path = 'image.png'
        img = image.load_img(img_path, target_size=(224, 224))
        x = image.img_to_array(img)
        x = np.expand_dims(x, axis=0)
        x = preprocess_input(x)

        preds = model.predict(x)
        # decode the results into a list of tuples (class, description, probability)
        # (one such list for each sample in the batch)
        data = decode_predictions(preds, top=5)[0]
#         data = data.encode()
        client_socket = Queue1.get()
        data=json.dumps(client_socket).encode()
        client_socket.sendall(data)

        # Close the socket
        client_socket.close()    
    # Predicted: [(u'n02504013', u'Indian_elephant', 0.82658225), (u'n01871265', u'tusker', 0.1122357), (u'n02504458', u'African_elephant', 0.061040461)]
        
    
if __name__ == "__main__":
    thread1 = threading.Thread(target=Listen,daemon=False)
    thread1.start()
    thread2 = threading.Thread(target=Image,daemon=False)
    thread2.start()