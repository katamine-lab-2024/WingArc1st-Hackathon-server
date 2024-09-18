from flask import Flask, render_template, request, Response
from lib.gacha import gacha10
from PIL import Image
import io

app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    return render_template('menu.html')

@app.route('/gacha', methods=['GET'])
def gacha():
    results = gacha10()

    return render_template('gacha.html', results=results)

# ガチャの結果から画像を取得する
# get /card?card_img=xxxxxxでとれる
@app.route('/card', methods=['GET'])
def card():
    imgname = request.args.get('img')
    rarity = request.args.get('rarity')

    # if rarity == 'UR':
    #     # 動画を読み込んでresponseとして返す

        
    image = Image.open('uploads/' + imgname)
    img_io = io.BytesIO()
    image.save(img_io, 'JPEG')
    img_io.seek(0)

    return Response(img_io, mimetype='image/jpeg')


@app.route('/create', methods=['GET'])
def create():
    return render_template('create.html')

@app.route('/collection', methods=['GET'])
def collection():
    return f'collection'

if __name__ == '__main__':
    app.run(debug=True)
