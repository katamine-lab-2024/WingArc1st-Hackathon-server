from flask import Flask, render_template, Response
from gacha import gacha

app = Flask(__name__)

@app.route('/gacha', methods=['GET'])
def gacha():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
