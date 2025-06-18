# TDS Virtual TA

A Flask-based API that answers student questions using TDS course content and Discourse forum posts.

## Features

- Answers questions using both TDS course content and Discourse posts
- Returns relevant links with each answer
- Easy to deploy on Render, Railway, or Heroku

## Setup

1. Clone the repository
2. Run `pip install -r requirements.txt`
3. Run the scraper: `python discourse_scraper.py`
4. Start the API: `python app.py`

## Deployment

- **Render:** Connect your repo and use the Procfile.
- **Railway/Heroku:** Similar setup.

## Project Structure

- `app.py` — Main Flask API
- `discourse_scraper.py` — Discourse scraper
- `requirements.txt` — Dependencies
- `Procfile` — Deployment config
- `LICENSE` — MIT License
- `data/course_content/tools-in-data-science-public/` — Course content submodule
