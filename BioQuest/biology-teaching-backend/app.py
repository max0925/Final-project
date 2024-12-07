
from flask import Flask, request, jsonify
import requests
import json
import sqlite3
from flask_cors import CORS
from openai import OpenAI



app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Set API key
client = OpenAI(api_key="")
UNSPLASH_ACCESS_KEY = "bxeQJmSPTSJV9xa9TBBYYl_cgASvM5yFAYCB4jDAkpI"
YOUTUBE_API_KEY = "AIzaSyBW72sl0V-U5dhToSjpEcIW3hnnAswVpss"

# ---------------------
# OpenAI API features
# ---------------------

def generate_explanation(topic):
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                      "content": f"Explain {topic} in simple terms.",
                      }
                      ]
        )
        # Get the response content correctly
        explanation = response.choices[0].message.content.strip()  # Confirm the property access method
        return explanation
    except Exception as e:
        # Print error details
        print(f"Error: {e}")
        return "An error occurred while fetching explanation."

# ---------------------
# Unsplash API 
# ---------------------
def fetch_image(topic):
    url = f"https://api.unsplash.com/search/photos?query={topic}&client_id={UNSPLASH_ACCESS_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data['results']:
            return data['results'][0]['urls']['regular']
    return None

# ---------------------
# YouTube API 
# ---------------------
def fetch_video(topic):
    url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&type=video&q={topic}&key={YOUTUBE_API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data['items']:
            return f"https://www.youtube.com/watch?v={data['items'][0]['id']['videoId']}"
    return None
# ---------------------
# SQLite 功能
# ---------------------
def fetch_questions(topic):
    conn = sqlite3.connect("quiz.db")
    cursor = conn.cursor()
    cursor.execute("SELECT question FROM questions WHERE topic=?", (topic,))
    questions = cursor.fetchall()
    conn.close()
    return [q[0] for q in questions]

# ---------------------
# Flask routing
# ---------------------

# Receives user input and generates content
@app.route('/query', methods=['POST'])
def query():
    data = request.json
    topic = data.get('topic', 'biology')
    explanation = generate_explanation(topic)
    image = fetch_image(topic)
    video = fetch_video(topic)
    return jsonify({
        "status": "success",
        "data": {
            "topic": topic,
            "explanation": explanation,
            "resources": {
                "image": image,
                "video": video
            }
        }
    })

# Get quiz questions
def generate_quiz(topic, num_questions=3):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are an assistant helping teachers create quiz questions for students aged 10 to 12."},
            {"role": "user", "content": f"Create {num_questions} multiple-choice quiz questions about {topic}. Each question should have 4 options, and the correct one should be marked."}
        ]
    )
    quiz_content = response['choices'][0]['text']  # Update how you get content
    try:
        quiz_questions = json.loads(quiz_content)  # Try parsing in JSON format
    except json.JSONDecodeError:
        quiz_questions = {"error": "Invalid JSON from GPT-4o"}
    return quiz_questions

@app.route('/quiz', methods=['GET'])
def get_quiz():
    topic = request.args.get('topic', 'biology')
    num_questions = int(request.args.get('num_questions', 3))
    dynamic_questions = generate_quiz(topic, num_questions)
    return jsonify({"topic": topic, "questions": dynamic_questions})

# Initialize the database (if the table does not exist)
def init_db():
    conn = sqlite3.connect("quiz.db")
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        topic TEXT,
        score INTEGER
    )
    """)
    conn.commit()
    conn.close()

@app.route('/quiz', methods=['POST'])
def submit_quiz():
    data = request.json
    username = data.get('username', 'Anonymous')
    topic = data.get('topic', 'biology')
    answers = data.get('answers', {})
    correct_answers = {"question1": "A", "question2": "C"}  # Sample correct answer
    score = sum(1 for q, a in answers.items() if correct_answers.get(q) == a)

    conn = sqlite3.connect("quiz.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO user_results (username, topic, score) VALUES (?, ?, ?)",
                   (username, topic, score))
    conn.commit()
    conn.close()

    return jsonify({"status": "success", "score": score})

@app.route('/')
def home():
    return jsonify({
        "message": "Welcome to the BioQuest API!",
        "endpoints": {
            "/query": "POST - Generate explanations, images, and videos for a given topic."
        }
    })

if __name__ == "__main__":
    app.run(debug=True, port=8000)