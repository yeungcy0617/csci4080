from flask import Flask, current_app, request
import pandas as pd
import json
import numpy as np
import heapq
import operator
from scipy.stats import pearsonr
app = Flask(__name__)

# Store something in the "data" attribute
# of the Flask application
app.data = "Some data"

users = []
user_movie_score_df = pd.pivot_table(pd.read_csv('ratings.small.csv')[['userId', 'movieId', 'rating']], index='userId', columns=['movieId'], values=['rating'], fill_value=0)
movie_df = pd.merge(pd.read_csv('movies.csv'), pd.read_csv('links.csv'), how='left', on=['movieId']).set_index('movieId')

def similarity(u1, u2):
    r, _ = pearsonr(u1, u2)
    return r

@app.route('/')
def index():
    # Returns "Some data"
    return current_app.data

@app.route('/register', methods=["POST"])
def register():
    # Returns "Some data"
    chat_id = request.form.get('chat_id')
    if chat_id not in users:
        users.append(chat_id)
        user_movie_score_df.loc[chat_id] = 0
        return json.dumps({"exists": 0})
    else:
        return json.dumps({"exists": 1})
    
@app.route('/get_unrated_movie', methods=["POST"])
def get_unrated_movie():
    chat_id = request.form.get('chat_id')
    for item in list(user_movie_score_df):
        if user_movie_score_df.loc[chat_id,[item]][0] == 0:
            return json.dumps({"id": str(item[1]), "title": movie_df.loc[item[1],['title']][0], "url": 'http://www.imdb.com/title/tt'+str(10000000 + movie_df.loc[item[1],['imdbId']][0])[1:8]})
            break

@app.route('/rate_movie', methods=["POST"])
def rate_movie():
    user_movie_score_df.loc[request.form.get('chat_id'),[('rating',int(request.form.get('movie_id')))]] = int(request.form.get('rating'))
    return json.dumps({"status": "success"})

@app.route('/recommend', methods=["POST"])
def recommend():
    chat_id = int(request.form.get('chat_id'))
    
    if ((user_movie_score_df.loc[chat_id] > 0).sum(axis=0)) < 10:
        return json.dumps({ "movies": [] })
    else:
        similarity_users = []
        user_rating = user_movie_score_df.loc[chat_id].as_matrix()
        matrix = user_movie_score_df.loc[user_movie_score_df.index != chat_id].as_matrix()
        for x in matrix:
            similarity_users.append(similarity(user_rating, x))
        r_mean_user = np.mean([r for r in user_rating if r > 0])
        r_mean_other_user = np.mean([r for r in matrix[similarity_users.index(max(similarity_users))] if r > 0])
        for x in range(0,len(user_rating)):
            if user_rating[x] != 0:
                user_rating[x] = -1
            else:
                user_rating[x] = r_mean_user + (max(similarity_users) * (matrix[similarity_users.index(max(similarity_users))][x] - r_mean_other_user))
        result = sorted(range(len(user_rating)), key=lambda i: user_rating[i])[-3:]
        return json.dumps({ "movies": [ { "title": movie_df.loc[user_movie_score_df.columns[int(result[0])][1],['title']][0], "url": 'http://www.imdb.com/title/tt'+str(10000000 + movie_df.loc[user_movie_score_df.columns[int(result[0])][1],['imdbId']][0])[1:8] }, { "title": movie_df.loc[user_movie_score_df.columns[int(result[1])][1],['title']][0], "url": 'http://www.imdb.com/title/tt'+str(10000000 + movie_df.loc[user_movie_score_df.columns[int(result[1])][1],['imdbId']][0])[1:8] },{ "title": movie_df.loc[user_movie_score_df.columns[int(result[2])][1],['title']][0], "url": 'http://www.imdb.com/title/tt'+str(10000000 + movie_df.loc[user_movie_score_df.columns[int(result[2])][1],['imdbId']][0])[1:8] }]})
