# AI Mock Interview Platform

A Django starter project for practicing Python, OOP, Django, SQL and HR interviews. Includes authentication, interview sessions, question generation, typed answers, browser-based speech recognition, answer evaluation, scores, and topic progress.

## Features

- Django registration, login and logout
- Select target role, topic, and difficulty
- Generates up to five questions for a session
- Voice transcription through the browser Web Speech API where supported
- Evaluate answers and show score, strengths, and improvements
- Dashboard with recent sessions and weak-topic suggestions
- SQLite works by default; optional MySQL configuration
- Optional OpenAI-compatible LLM API integration
- Django admin for viewing sessions, questions, and evaluations

## Requirements

- Python 3.10+
- MySQL Server only if you choose MySQL
- Modern browser; speech recognition availability varies by browser and device
- Optional LLM API key for semantic evaluation

## Windows setup (PowerShell or CMD)

```bat
cd ai_mock_interview_platform
py -m venv venv
venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
copy .env.example .env
python manage.py makemigrations interview
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Open `http://127.0.0.1:8000/`.

If `py` is unavailable, use `python` instead. If your environment does not have a compatible Python version, install Python 3.11 or 3.12 and recreate the virtual environment.

## Configure MySQL (optional)

1. Create a database in MySQL:
   ```sql
   CREATE DATABASE mock_interview CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```
2. In `.env`, set:
   ```env
   DB_ENGINE=mysql
   DB_NAME=mock_interview
   DB_USER=root
   DB_PASSWORD=your_mysql_password
   DB_HOST=127.0.0.1
   DB_PORT=3306
   ```
3. Install dependencies again if needed, then run:
   ```bat
   python manage.py migrate
   ```

If `mysqlclient` fails to install on Windows, use a supported Python version and follow the mysqlclient Windows installation requirements. The default SQLite mode avoids needing MySQL for initial testing.

## Enable AI model evaluation (optional)

This project supports an OpenAI-compatible `/chat/completions` endpoint. Add your own valid credentials to `.env`:

```env
LLM_API_KEY=your_api_key_here
LLM_BASE_URL=https://api.openai.com/v1
LLM_MODEL=gpt-4o-mini
```

Restart the Django server after changing `.env`. Keep API keys on the server; never put them in HTML or JavaScript. API use may incur charges. If no key is configured or the API request fails, the app uses a simple keyword-based demo fallback.

## Voice input

Click **Answer by voice** and allow microphone access. Browser speech recognition may require HTTPS outside localhost, internet connectivity, and browser support. The current implementation uses English (India). You can change `recognition.lang` in `static/js/interview.js`. Always review the transcript before submitting. Typing answers is supported as a fallback.

## How scoring works

- With a configured LLM, the model returns score, feedback, strengths and improvements.
- Without an LLM, the demo evaluator checks expected keywords and answer length. It is not a reliable semantic grade and is only intended for local development.
- Scores are practice feedback, not a definitive measurement of a candidate's ability.

## Main project structure

```text
ai_mock_interview_platform/
├── manage.py
├── config/
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
├── interview/
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── ai_service.py
│   └── admin.py
├── templates/
│   ├── base.html
│   ├── interview/
│   └── registration/
├── static/
│   ├── css/style.css
│   └── js/interview.js
├── requirements.txt
└── .env.example
```

## Important before public deployment

- Set a strong `SECRET_KEY`, `DEBUG=False`, and correct `ALLOWED_HOSTS`.
- Use HTTPS, configure secure cookies, and configure database backups.
- Add rate limits and usage limits to protect any paid LLM endpoint.
- Consider adding automated tests, pagination, logging, and API response validation before production.
