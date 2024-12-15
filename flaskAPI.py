import os
from flask import Flask, request, jsonify, render_template
import google.generativeai as genai

from dotenv import load_dotenv

load_dotenv()

# Access the API key
api_key = os.getenv("GEMINI_API_KEY")

# Configure the API with the key
genai.configure(api_key=api_key)

# Create the model configuration
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

# Initialize the model
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
    system_instruction=(
        "You are Sandy, the frontend web development chatbot assistant. "
        "You will only answer questions related to front-end web development, "
        "i.e., HTML, JavaScript, CSS, etc."
    ),
)

# Initialize Flask app
app = Flask(__name__)

# Track chat sessions
chat_sessions = {}


@app.route('/')
def index():
    """Render the home page with a simple chat interface."""
    return render_template("index.html")


@app.route('/chat', methods=['POST'])
def chat():
    """Handle user messages and return the chatbot's response."""
    user_message = request.json.get('message')
    session_id = request.json.get('session_id')

    # Initialize a chat session if it doesn't exist
    if session_id not in chat_sessions:
        chat_sessions[session_id] = model.start_chat(
            history=[
                {"role": "user", "parts": ["what is your name"]},
                {"role": "model", "parts": ["I'm Sandy, your frontend web development chatbot assistant."]},
            ]
        )

    # Get the chat session
    chat_session = chat_sessions[session_id]

    # Send the user's message and get the model's response
    response = chat_session.send_message(user_message)

    return jsonify({"response": response.text})


if __name__ == '__main__':
    app.run(debug=True)
