from django.conf import settings
from django.db import models

class InterviewSession(models.Model):
    TOPICS = [
        ("Python", "Python"),
        ("OOP", "OOP"),
        ("Django", "Django"),
        ("SQL", "SQL"),
        ("HR", "HR"),
    ]
    LEVELS = [("Beginner", "Beginner"), ("Intermediate", "Intermediate"), ("Advanced", "Advanced")]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="interview_sessions")
    role = models.CharField(max_length=100, default="Python Developer")
    topic = models.CharField(max_length=30, choices=TOPICS, default="Python")
    difficulty = models.CharField(max_length=20, choices=LEVELS, default="Beginner")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.topic} - {self.created_at:%Y-%m-%d}"

class InterviewQuestion(models.Model):
    session = models.ForeignKey(InterviewSession, on_delete=models.CASCADE, related_name="questions")
    question_text = models.TextField()
    expected_points = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=1)

    def __str__(self):
        return self.question_text[:80]

class AnswerEvaluation(models.Model):
    session = models.ForeignKey(InterviewSession, on_delete=models.CASCADE, related_name="evaluations")
    question = models.ForeignKey(InterviewQuestion, on_delete=models.CASCADE, related_name="evaluations")
    answer_text = models.TextField()
    score = models.PositiveSmallIntegerField(default=0)
    feedback = models.TextField(blank=True)
    strengths = models.TextField(blank=True)
    improvements = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.session.user} - {self.score}/100"
