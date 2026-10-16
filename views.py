from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.db.models import Avg
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from .ai_service import generate_questions, evaluate_answer
from .models import InterviewSession, InterviewQuestion, AnswerEvaluation

def home(request):
    return render(request, "interview/home.html")

def signup(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Account created. Welcome!")
            return redirect("dashboard")
    else:
        form = UserCreationForm()
    return render(request, "registration/signup.html", {"form": form})

@login_required
def dashboard(request):
    sessions = InterviewSession.objects.filter(user=request.user).order_by("-created_at")[:10]
    evaluations = AnswerEvaluation.objects.filter(session__user=request.user)
    average = evaluations.aggregate(avg=Avg("score"))["avg"] or 0
    topic_stats = []
    for topic, label in InterviewSession.TOPICS:
        stats = evaluations.filter(session__topic=topic).aggregate(avg=Avg("score"), total=Avg("score"))
        count = evaluations.filter(session__topic=topic).count()
        if count:
            topic_stats.append({"topic": topic, "average": round(stats["avg"] or 0), "count": count})
    weak_topics = [x for x in topic_stats if x["average"] < 60]
    return render(request, "interview/dashboard.html", {
        "sessions": sessions, "average": round(average), "evaluation_count": evaluations.count(),
        "topic_stats": topic_stats, "weak_topics": weak_topics,
    })

@login_required
def start_interview(request):
    if request.method == "POST":
        topic = request.POST.get("topic", "Python")
        difficulty = request.POST.get("difficulty", "Beginner")
        role = request.POST.get("role", "Python Developer").strip()[:100] or "Python Developer"
        valid_topics = dict(InterviewSession.TOPICS)
        valid_levels = dict(InterviewSession.LEVELS)
        if topic not in valid_topics or difficulty not in valid_levels:
            messages.error(request, "Please choose a valid topic and difficulty.")
            return redirect("start_interview")
        session = InterviewSession.objects.create(user=request.user, role=role, topic=topic, difficulty=difficulty)
        for index, (question, points) in enumerate(generate_questions(topic, difficulty, 5), start=1):
            InterviewQuestion.objects.create(session=session, question_text=question, expected_points=points, order=index)
        return redirect("take_interview", session_id=session.id)
    return render(request, "interview/start.html", {
        "topics": InterviewSession.TOPICS, "levels": InterviewSession.LEVELS,
    })

@login_required
def take_interview(request, session_id):
    session = get_object_or_404(InterviewSession, id=session_id, user=request.user)
    questions = session.questions.all().order_by("order")
    answered_ids = set(session.evaluations.values_list("question_id", flat=True))
    return render(request, "interview/take_interview.html", {
        "session": session, "questions": questions, "answered_ids": answered_ids,
    })

@login_required
@require_POST
def submit_answer(request, session_id, question_id):
    session = get_object_or_404(InterviewSession, id=session_id, user=request.user)
    question = get_object_or_404(InterviewQuestion, id=question_id, session=session)
    answer = request.POST.get("answer", "").strip()
    if len(answer) > 10000:
        return JsonResponse({"error": "Answer is too long. Keep it under 10,000 characters."}, status=400)
    evaluation = evaluate_answer(question.question_text, question.expected_points, answer)
    AnswerEvaluation.objects.update_or_create(
        session=session, question=question,
        defaults={
            "answer_text": answer,
            "score": evaluation["score"],
            "feedback": evaluation["feedback"],
            "strengths": evaluation["strengths"],
            "improvements": evaluation["improvements"],
        },
    )
    return JsonResponse({
        "score": evaluation["score"], "feedback": evaluation["feedback"],
        "strengths": evaluation["strengths"], "improvements": evaluation["improvements"],
    })

@login_required
def results(request, session_id):
    session = get_object_or_404(InterviewSession, id=session_id, user=request.user)
    evaluations = session.evaluations.select_related("question").all()
    average = evaluations.aggregate(avg=Avg("score"))["avg"] or 0
    return render(request, "interview/results.html", {
        "session": session, "evaluations": evaluations, "average": round(average),
        "total": session.questions.count(), "completed": evaluations.count(),
    })
