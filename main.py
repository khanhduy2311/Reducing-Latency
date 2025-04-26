from flask import Flask, request, jsonify, render_template
from flask_compress import Compress
from qa_model import qa

app = Flask(__name__)
Compress(app)

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/api/ask', methods=['POST'])
def ask():
    data = request.get_json()
    question = data.get("question")
    premises = data.get("premises")

    if not question or not premises:
        return jsonify({"error": "Missing question or premises"}), 400

    result = qa(question=question, context=premises)

    return jsonify({
        "answer": result["answer"],
        "score": round(result["score"], 4)
    })

if __name__ == '__main__':
    app.run(debug=True)
