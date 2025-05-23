from flask import Flask, request, jsonify
import openai
import os

app = Flask(__name__)

openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route("/reply", methods=["POST"])
def reply():
    review = request.json.get("review")
    if not review:
        return jsonify({"error": "No review text provided"}), 400

    prompt = f"Write a polite, professional response to the following customer review: '{review}'"
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
        reply_text = response.choices[0].message.content.strip()
        return jsonify({"reply": reply_text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/", methods=["GET"])
def home():
    return "Google Review Auto-Reply Service is running."

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
