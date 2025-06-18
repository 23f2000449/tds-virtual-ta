import json
import os
import glob
from flask import Flask, request, jsonify

app = Flask(__name__)

# Load Discourse posts
try:
    with open('discourse_posts.json', encoding='utf-8') as f:
        forum_posts = json.load(f)
except Exception as e:
    forum_posts = []
    print(f"Error loading discourse_posts.json: {e}")

# Course content configuration
COURSE_CONTENT_PATH = "data/course_content/tools-in-data-science-public"

def search_course_content(question):
    results = []
    for md_file in glob.glob(f"{COURSE_CONTENT_PATH}/**/*.md", recursive=True):
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read().lower()
            if question.lower() in content:
                relative_path = os.path.relpath(md_file, COURSE_CONTENT_PATH)
                results.append({
                    "url": f"https://github.com/sanand0/tools-in-data-science-public/blob/main/{relative_path}",
                    "text": os.path.basename(md_file)
                })
    return results

@app.route('/api/', methods=['POST'])
def answer_question():
    try:
        data = request.get_json(force=True)
        question = data.get('question', '').strip()
        if not question:
            return jsonify({"answer": "No question provided.", "links": []}), 400

        # Search Discourse posts
        discourse_results = []
        for post in forum_posts:
            if question.lower() in post.get('raw', '').lower() or question.lower() in post.get('topic_title', '').lower():
                link = f"https://discourse.onlinedegree.iitm.ac.in/t/{post['topic_id']}/{post['post_number']}"
                discourse_results.append({"url": link, "text": post.get('topic_title', '')[:100]})

        # Search course content
        course_results = search_course_content(question)

        # Combine results
        all_results = discourse_results + course_results

        return jsonify({
            "answer": f"Found {len(all_results)} relevant resources." if all_results else "No results found.",
            "links": all_results
        })

    except Exception as e:
        return jsonify({"answer": f"Error processing request: {str(e)}", "links": []}), 500

if __name__ == '__main__':
    app.run(debug=True)
# To run the Flask app, use the command: python app.py
