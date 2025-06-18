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
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read().lower()
                if question.lower() in content:
                    relative_path = os.path.relpath(md_file, COURSE_CONTENT_PATH)
                    results.append({
                        "url": f"https://github.com/sanand0/tools-in-data-science-public/blob/main/{relative_path}",
                        "text": os.path.basename(md_file)
                    })
        except Exception as e:
            print(f"Error reading {md_file}: {e}")
    return results

@app.route('/api/', methods=['POST'])
def answer_question():
    try:
        data = request.get_json(force=True)
        question = data.get('question', '').strip().lower()
        image = data.get('image', None)  # Optional base64-encoded image

        if not question:
            return jsonify({"answer": "No question provided.", "links": []}), 400

        # Search Discourse posts
        discourse_results = []
        for post in forum_posts:
            if not isinstance(post, dict):
                continue
            # Search both 'content' and 'topic_title' fields (adjust for your JSON structure)
            content = post.get('content', '').lower() or post.get('raw', '').lower()
            topic_title = post.get('topic_title', '').lower()
            if question in content or question in topic_title:
                topic_id = post.get('topic_id', '')
                post_number = post.get('post_number', '')
                link = f"https://discourse.onlinedegree.iitm.ac.in/t/{topic_id}/{post_number}"
                discourse_results.append({
                    "url": link,
                    "text": topic_title[:100]
                })

        # Search course content
        course_results = search_course_content(question)

        # Combine results
        all_results = discourse_results + course_results

        # If image is provided but not processed, mention it in the answer
        image_mention = " (Image upload is not supported at this time.)" if image else ""
        answer = f"Found {len(all_results)} relevant resources." if all_results else "No results found."
        answer += image_mention

        return jsonify({
            "answer": answer,
            "links": all_results
        })

    except Exception as e:
        return jsonify({"answer": f"Error processing request: {str(e)}", "links": []}), 500

if __name__ == '__main__':
    app.run(debug=True)
# Run the Flask app
# Use `flask run` or `python app.py` to start the server