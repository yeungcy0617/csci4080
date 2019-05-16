import base64
import json
import requests
from telepot.loop import MessageLoop
from io import BytesIO
from PIL import Image
from redis import StrictRedis
r = StrictRedis(host='localhost', port=6379) 
while True:
    item = json.loads(r.blpop('download'))
    if 'file_id' in item:
        bot.download_file(item['file_id'], './file.png')
    elif 'url' in item:
        with open('./file.png', 'wb') as handle:
            response = requests.get(item["url"], stream=True)
            for block in response.iter_content(1024):
                if not block:
                    break
                handle.write(block)
    image = Image.open('./file.png')
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    encoded_image = base64.encodebytes(buffered.getvalue()).decode('ascii') 
    data = {
    'image': encoded_image,
    'chat_id': item['chat_id']
    }
    r.rpush('image', json.dumps(data).encode("utf-8"))    
    