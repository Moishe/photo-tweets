from flask import Flask
from flask import Response
from flask_cors import CORS

import TwitterPhotos

app = Flask(__name__, static_url_path='')
CORS(app)

@app.route("/")
def hello_world():
  return app.send_static_file('index.html')

@app.route("/photos")
def get_photos():
  json = TwitterPhotos.TwitterPhotos('1344411611960901637').fetch_photo_tweets()
  return Response(json, mimetype='application/json')
