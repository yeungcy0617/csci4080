import time
import logging
import telepot
from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardButton, InlineKeyboardMarkup
import json
import requests

logging.basicConfig(level=logging.INFO)


def handle(msg):
    """
    A function that will be invoked when a message is
    recevied by the bot
    """
    # Get text or data from the message
    text = msg.get("text", None)
    data = msg.get("data", None)
#     print(msg)
    if data is not None:
        # This is a message from a custom keyboard
        chat_id = msg["message"]["chat"]["id"]
        content_type = "data"
    elif text is not None:
        # This is a text message from the user
        chat_id = msg["chat"]["id"]
        content_type = "text"
    else:
        # This is a message we don't know how to handle
        content_type = "unknown"
    
    if content_type == "text":
        message = msg["text"]
        logging.info("Received from chat_id={}: {}".format(chat_id, message))

        if message == "/start":
            # Check against the server to see
            # if the user is new or not
            if(json.loads(requests.post("http://localhost:5000/register", data={'chat_id': chat_id}).text)['exists']):
                bot.sendMessage(chat_id, 'Welcome back!')
            else:
                bot.sendMessage(chat_id, 'Welcome!')
        
        elif message == "/rate":
            contents_dict = json.loads(requests.post("http://localhost:5000/get_unrated_movie", data={'chat_id': chat_id}).text)
            bot.sendMessage(chat_id, contents_dict['title']+' '+ contents_dict['url'])
            # Create a custom keyboard to let user enter rating
            my_inline_keyboard = [[
                InlineKeyboardButton(text='1', callback_data=str(contents_dict['id'])+'_1'),
                InlineKeyboardButton(text='2', callback_data=str(contents_dict['id'])+'_2'),
                InlineKeyboardButton(text='3', callback_data=str(contents_dict['id'])+'_3'),
                InlineKeyboardButton(text='4', callback_data=str(contents_dict['id'])+'_4'),
                InlineKeyboardButton(text='5', callback_data=str(contents_dict['id'])+'_5')
            ]]
            keyboard = InlineKeyboardMarkup(inline_keyboard=my_inline_keyboard )
            bot.sendMessage(chat_id, "How do you rate this movie?", reply_markup=keyboard)
        
        elif message == "/recommend":
            lists = json.loads((requests.post("http://localhost:5000/recommend", data={'chat_id': chat_id, "top_n": 3}).text))['movies']
            if len(lists) > 0:
                bot.sendMessage(chat_id, "My recommendations:{0}{1},{2}{3},{4}{5}".format(lists[0]['title'],lists[0]['url'],lists[1]['title'],lists[1]['url'],lists[2]['title'],lists[2]['url']))
            else:
                bot.sendMessage(chat_id, "not enough data")

        else:
            # Some command that we don't understand
            bot.sendMessage(chat_id, "I don't understand your command.")

    elif content_type == "data":
        # This is data returned by the custom keyboard
        # Extract the movie ID and the rating from the data
        # and then send this to the server
        # TODO
        movie_id = int(data.split('_')[0])
        rating = int(data.split('_')[1])
        requests.post("http://localhost:5000/rate_movie", data={"chat_id": chat_id, "movie_id": movie_id, "rating": rating})
        logging.info("Received rating: {}".format(data))
        bot.sendMessage(chat_id, "Your rating is received!")


if __name__ == "__main__":
    
    # Povide your bot's token 
    bot = telepot.Bot("796097683:AAH5A4rKYanUq3ou2plYhGNjlrLb--EArDM")
    MessageLoop(bot, handle).run_as_thread()

    while True:
        time.sleep(10)