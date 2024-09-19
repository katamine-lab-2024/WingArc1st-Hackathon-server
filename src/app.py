from flask import Flask, render_template, Response
from gacha import gacha
import json

app = Flask(__name__)

@app.route('/gacha', methods=['GET'])
def gacha_api():
    result_json = json.dumps(gacha())
    return Response(result_json, mimetype='application/json')

if __name__ == '__main__':
    app.run(debug=True)
