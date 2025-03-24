from flask import Flask, request, jsonify
import openai
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Load the OpenAI API key securely from environment or .env
openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route("/api/search", methods=["POST"])
def search():
    data = request.get_json()
    query = data.get("query", "")
    
    # Placeholder for real PubMed/PubChem/CrossRef integration
    dummy_result = [{
        "title": "Example Fluorophore Study on Bimanes",
        "authors": "Doe J, Smith A",
        "abstract": "This is a mock abstract for a Bimane-based fluorophore study."
    }]
    return jsonify({"results": dummy_result})

@app.route("/api/summarize", methods=["POST"])
def summarize():
    data = request.get_json()
    text = data.get("text", "")
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful scientific research assistant."},
                {"role": "user", "content": f"""Summarize the following text:\n{text}"""}
            ]
        )
        summary = response['choices'][0]['message']['content']
        return jsonify({"summary": summary})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
