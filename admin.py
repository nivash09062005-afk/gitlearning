from django.contrib import admin
from .models import InterviewSession, InterviewQuestion, AnswerEvaluation

@admin.register(InterviewSession)
class InterviewSessionAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "role", "topic", "difficulty", "created_at")
    list_filter = ("topic", "difficulty", "created_at")

@admin.register(InterviewQuestion)
class InterviewQuestionAdmin(admin.ModelAdmin):
    list_display = ("id", "session", "order")
    search_fields = ("question_text",)

@admin.register(AnswerEvaluation)
class AnswerEvaluationAdmin(admin.ModelAdmin):
    list_display = ("id", "session", "question", "score", "created_at")
    list_filter = ("score", "created_at")
