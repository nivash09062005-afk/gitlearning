import json
import os
import requests

QUESTIONS = {
    "Python": {
        "Beginner": [
            ("What is the difference between a list and a tuple in Python?", "mutability; list can change; tuple is immutable"),
            ("What is the difference between == and is?", "equality; object identity"),
            ("What are Python dictionaries used for?", "key-value pairs; keys are unique"),
        ],
        "Intermediate": [
            ("Explain list comprehension and give an example.", "compact syntax; iterable; condition optional"),
            ("What is the difference between shallow copy and deep copy?", "nested objects; references; independent copy"),
            ("What is a generator in Python?", "yield; lazy evaluation; iterator"),
        ],
        "Advanced": [
            ("Explain decorators and give a practical use case.", "wrapper function; callable; extends behavior"),
            ("What is the Global Interpreter Lock (GIL)?", "CPython; one thread executes Python bytecode at a time; CPU-bound implications"),
            ("Compare asyncio, threading, and multiprocessing.", "I/O-bound; concurrency; CPU-bound; processes"),
        ],
    },
    "OOP": {
        "Beginner": [
            ("What is a class and what is an object?", "blueprint; instance"),
            ("Explain inheritance in Python.", "reuse; parent; child"),
        ],
        "Intermediate": [
            ("Explain encapsulation and polymorphism with Python examples.", "data hiding; same interface; different behavior"),
            ("What is method overriding?", "subclass; same method name; new implementation"),
        ],
        "Advanced": [
            ("What is MRO in Python and why does it matter?", "method resolution order; inheritance; C3 linearization"),
            ("Explain composition versus inheritance.", "has-a; is-a; coupling"),
        ],
    },
    "Django": {
        "Beginner": [
            ("What is Django and what does MTV mean?", "web framework; Model Template View"),
            ("What is a Django model?", "database table; fields; ORM"),
        ],
        "Intermediate": [
            ("What is the difference between select_related and prefetch_related?", "foreign key; one query; separate queries; many-to-many"),
            ("Explain Django middleware.", "request response; processing layer"),
        ],
        "Advanced": [
            ("How would you secure a Django REST API?", "authentication; permissions; validation; throttling; HTTPS"),
            ("How can you improve a slow Django queryset?", "indexes; query inspection; select_related; prefetch_related; pagination"),
        ],
    },
    "SQL": {
        "Beginner": [
            ("What is the difference between WHERE and HAVING?", "row filtering; aggregate filtering"),
            ("What is a primary key?", "unique; not null; identify row"),
        ],
        "Intermediate": [
            ("Explain INNER JOIN and LEFT JOIN.", "matching rows; all left rows; nulls"),
            ("What is an index and what trade-off does it introduce?", "faster reads; storage; write overhead"),
        ],
        "Advanced": [
            ("How would you find duplicate email addresses in a table?", "GROUP BY; HAVING COUNT"),
            ("Explain database transactions and ACID.", "atomicity; consistency; isolation; durability"),
        ],
    },
    "HR": {
        "Beginner": [
            ("Tell me about yourself as a Python Developer fresher.", "education; skills; project; career goal"),
            ("Why do you want to work as a Python Developer?", "interest; relevant skills; learning; contribution"),
        ],
        "Intermediate": [
            ("Describe a technical problem you solved and how you approached it.", "problem; steps; outcome; learning"),
            ("How do you handle feedback or a mistake in your code?", "ownership; reproduce; fix; test; learn"),
        ],
        "Advanced": [
            ("Tell me about a time you had to prioritize competing tasks.", "impact; deadlines; communication; trade-offs"),
            ("How would you explain a complex technical issue to a non-technical person?", "audience; plain language; analogy; confirm understanding"),
        ],
    },
}

def _llm_request(prompt):
    api_key = os.getenv("LLM_API_KEY", "").strip()
    if not api_key:
        return None
    base_url = os.getenv("LLM_BASE_URL", "https://api.openai.com/v1").rstrip("/")
    model = os.getenv("LLM_MODEL", "gpt-4o-mini")
    try:
        response = requests.post(
            f"{base_url}/chat/completions",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={"model": model, "messages": [
                {"role": "system", "content": "You are a fair technical interview coach. Return valid JSON only when asked for JSON."},
                {"role": "user", "content": prompt},
            ], "temperature": 0.3},
            timeout=45,
        )
        response.raise_for_status()
        content = response.json()["choices"][0]["message"]["content"]
        return content
    except (requests.RequestException, KeyError, ValueError, TypeError):
        return None

def generate_questions(topic, difficulty, count=5):
    """Generate questions via LLM when configured; otherwise use built-in questions."""
    prompt = (
        f"Create {count} interview questions for a {difficulty} level {topic} interview. "
        "Return JSON only in this format: {\"questions\":[{\"question\":\"...\",\"expected_points\":\"...\"}]}. "
        "Do not include answers in question text."
    )
    raw = _llm_request(prompt)
    if raw:
        try:
            data = json.loads(raw)
            items = data.get("questions", [])
            cleaned = [(str(x["question"]), str(x.get("expected_points", ""))) for x in items if x.get("question")]
            if cleaned:
                return cleaned[:count]
        except (json.JSONDecodeError, TypeError, KeyError):
            pass
    return QUESTIONS.get(topic, QUESTIONS["Python"]).get(
        difficulty, QUESTIONS["Python"]["Beginner"]
    )[:count]

def evaluate_answer(question, expected_points, answer):
    """Return a structured evaluation. LLM output is validated; local fallback is demonstrative."""
    prompt = f"""
Evaluate this interview answer fairly. Score 0-100 based on correctness, relevance and completeness.
Question: {question}
Expected concepts: {expected_points}
Candidate answer: {answer}
Return JSON only:
{{"score": 0, "feedback": "brief explanation", "strengths": "what was correct", "improvements": "specific next steps"}}
Do not reward unrelated length. If answer is empty, score 0.
"""
    raw = _llm_request(prompt)
    if raw:
        try:
            data = json.loads(raw)
            score = max(0, min(100, int(data.get("score", 0))))
            return {
                "score": score,
                "feedback": str(data.get("feedback", "Review the key concepts."))[:2000],
                "strengths": str(data.get("strengths", ""))[:1500],
                "improvements": str(data.get("improvements", ""))[:1500],
            }
        except (json.JSONDecodeError, TypeError, ValueError):
            pass

    if not answer.strip():
        return {"score": 0, "feedback": "No answer was provided.", "strengths": "Not assessed.", "improvements": "Try answering in your own words, then include a small example."}
    keywords = [x.strip().lower() for x in expected_points.replace(";", ",").split(",") if x.strip()]
    answer_lower = answer.lower()
    matched = [word for word in keywords if word in answer_lower]
    score = round(100 * len(matched) / max(1, len(keywords)))
    if len(answer.split()) >= 15:
        score = min(100, score + 10)
    return {
        "score": score,
        "feedback": "Demo evaluation: this score checks for expected keywords and answer length. Configure an LLM API for semantic evaluation.",
        "strengths": ("Mentioned: " + ", ".join(matched)) if matched else "You attempted the question.",
        "improvements": ("Review these concepts: " + ", ".join([x for x in keywords if x not in matched])) if len(matched) < len(keywords) else "Add a concise example and explain when the concept is useful.",
    }
