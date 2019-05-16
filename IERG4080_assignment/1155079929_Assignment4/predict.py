import threading
import base64
import json
import pickle
from telepot.loop import MessageLoop
from keras.applications.resnet50 import ResNet50
from keras.preprocessing import image
from keras.applications.resnet50 import preprocess_input, decode_predictions
import numpy as np
from sklearn.externals import joblib
from redis import StrictRedis


r = StrictRedis(host='localhost', port=6379)    

while True:
    data = json.loads(r.blpop('image'))
    image_data = base64.b64decode(data['image'])
    with open('image.png', 'wb') as outfile:
        outfile.write(image_data)
    model = ResNet50(weights='imagenet')
    img_path = 'image.png'
    img = image.load_img(img_path, target_size=(224, 224))
    x = image.img_to_array(img)
    x = np.expand_dims(x, axis=0)
    x = preprocess_input(x)
    preds = model.predict(x)
    pred_dict = []
    for a,b,c in decode_predictions(preds, top=5)[0]:
        pred_dict.append({"label":b, "prob":str(c)[0:6]})
    r.rpush('download', json.dumps({"chat_id":data['chat_id'],"prediction": json.dumps(pred_dict) }).encode("utf-8"))        