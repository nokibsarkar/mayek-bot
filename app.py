from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from t import MeiteiToBengali

app = Flask(__name__)
allowed_hosts = [
    'https://mayek-bot.toolforge.org',
    'http://localhost:3000',
    'https://mni.wikipedia.org',
    'https://mni.m.wikipedia.org',
]
CORS(app, resources={"/*": {"origins": allowed_hosts}}, methods=['GET', 'POST', 'OPTIONS'], supports_credentials=True)

def transliterate(request):
    text = request.form.get('text')
    if text is None:
        return None
    return MeiteiToBengali.transliterate(text)

@app.get("/")
def index():
    return render_template('index.html')
@app.post("/")
def index_post():
    transliterated_text = transliterate(request) or ""
    return render_template('index.html', transliterated_text=transliterated_text, original_text=request.form.get('text'))

@app.post("/api/transliterate")
def transliterate_mni():
    transliterated_text = transliterate(request)
    if transliterated_text is None:
        return jsonify({"error": "Invalid request"})
    return transliterated_text

if __name__ == '__main__':
    app.run(debug=True, port=5000)