from flask import Flask, Response
from flask_cors import CORS
from gacha import gacha
import json
from lib.playercard import split_video_into_frames

app = Flask(__name__)
CORS(app)

@app.route('/gacha', methods=['GET'])
def gacha_api():
    result_json = json.dumps(gacha())
    return Response(result_json, mimetype='application/json')

@app.route('/img/<card_img>', methods=['GET'])
def get_img_api(card_img):
    with open(f'./uploads/{card_img}.jpg', 'rb') as f:
        img = f.read()
    return Response(img, mimetype='image/jpeg')

@app.route('/video/<card_img>', methods=['GET'])
def get_video_api(card_img):
    frames = split_video_into_frames(f'./uploads/{card_img}.mp4')
    def generate():
        for frame in frames:
            yield frame

    return Response(generate(), mimetype='image/jpeg')
    

if __name__ == '__main__':
    app.run(debug=True)
