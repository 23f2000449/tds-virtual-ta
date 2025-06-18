import requests
from datetime import datetime
import json
import time

BASE_URL = "https://discourse.onlinedegree.iitm.ac.in"
CATEGORY = "courses/tds-kb"
START_DATE = datetime(2025, 1, 1)
END_DATE = datetime(2025, 4, 14)
OUTPUT_FILE = "discourse_posts.json"

COOKIES = {
    "_ga": "GA1.1.1577740537.1726071435",
    "_ga_5HTJMW67XK": "GS1.1.1726071439.1.1.1726071590.0.0.0",
    "_ga_08NPRH5L4M": "GS1.1.1726071435.1.1.1726071605.45.0.0",
    "_t": "s34jFf7uxG%2B2bQHDjItZcv9ZR%2BImbLERGSVuZqScCPn7KZdxpWExzoDwghPfG6wtS0JSKWAn0Cq%2FuaZ2wi%2ByVR8YHkv87lZSWKfmmRP1%2FQz6bAEIBOPu6dQ32eBU4mRbwkQ9LN7J9mNVgsvqB%2FbVP504Rzmsu7DHUBT9pyxr2qCnLrAmSDWrYsMlOtYCNw8uuKzn5nlyEN2Lqm0mMQozqGd2C5BoIs3oJcxkqjRfAlJ2qKTM2k%2FlJQmql0uq7M0PSXdrnzVkROuo7hOQjiiaShfIlJV7r7WQ5I8mJflT9QX%2FOOzrrYbKxVHsSMSP2LjC--fCeoHBoOsB3%2Fd6vg--glxolWJK6hSlmjrsLLc%2FPA%3D%3D",
    "_forum_session": "aSBXTqRab2LRQ2W7REQHqO6HLV7GIxMaJ1bNXwiYB2hv8AcccbIqGrF0knGC6QI9oY22LH1VzhF9SzBs8FCFLWGKYmmSpTITmzrLBZBY7JFtMMNGHH%2BO5eNkIJxAsGSXqqObloy90bZqgYvWP7Oi4QwSbte7sEoympBRdCZUJtV2c74h8E03WJk4dE94ftHlUZjbuAkF7YhB7pK6jVeBG87hCgHbXopirZsluiAzl9LhxCskhSHpZvqP8OkutVVpHyFJxxS9MIG1oo7X8P2%2Fibj6SPY0wQ%3D%3D--LLEbLwvjeleXUtzD--vm2M7g0D0IxTdGLON%2BNRhA%3D%3D"
}

def parse_datetime(s):
    try:
        return datetime.strptime(s, "%Y-%m-%dT%H:%M:%S.%fZ")
    except ValueError:
        return datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ")

def fetch_topics(base_url, category, start_date, end_date, cookies):
    topics = []
    page = 0
    while True:
        url = f"{base_url}/c/{category}.json?page={page}"
        print(f"Fetching page {page}...")
        response = requests.get(url, cookies=cookies)
        if response.status_code != 200:
            print(f"Failed to fetch page {page}. Status: {response.status_code}")
            break
        try:
            data = response.json()
        except json.JSONDecodeError:
            print("Invalid JSON response. Check cookies or URL.")
            break
        topic_list = data.get("topic_list", {}).get("topics", [])
        if not topic_list:
            print("No more topics found.")
            break
        for topic in topic_list:
            created_at = parse_datetime(topic["created_at"])
            if start_date <= created_at <= end_date:
                topics.append(topic)
            elif created_at < start_date:
                print("Reached topics older than start date. Stopping.")
                return topics
        page += 1
        time.sleep(1)
    return topics

def fetch_posts(base_url, topic_id, cookies):
    url = f"{base_url}/t/{topic_id}.json"
    response = requests.get(url, cookies=cookies)
    if response.status_code != 200:
        print(f"Failed to fetch topic {topic_id}. Status: {response.status_code}")
        return []
    try:
        data = response.json()
    except json.JSONDecodeError:
        print("Invalid JSON response. Check cookies or URL.")
        return []
    posts = data.get("post_stream", {}).get("posts", [])
    for post in posts:
        post["topic_id"] = topic_id
        post["topic_title"] = data.get("title")
    return posts

def main():
    print("Starting Discourse scraper...")
    print(f"Scraping category: {CATEGORY} from {START_DATE} to {END_DATE}")
    topics = fetch_topics(BASE_URL, CATEGORY, START_DATE, END_DATE, COOKIES)
    print(f"Found {len(topics)} topics in date range.")

    all_posts = []
    for topic in topics:
        print(f"Fetching posts for topic ID {topic['id']} - {topic['title']}")
        posts = fetch_posts(BASE_URL, topic["id"], COOKIES)
        all_posts.extend(posts)
        time.sleep(1)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(all_posts, f, ensure_ascii=False, indent=2)
    print(f"Scraping complete. Posts saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
# This script scrapes posts from a Discourse forum within a specified date range and saves them to a JSON file.