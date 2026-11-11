from django.contrib import admin
from .models import Group, Contest, Problem, TestCase, Submission, SavedCode


class TestCaseInline(admin.TabularInline):
    model = TestCase
    extra = 1


@admin.register(Problem)
class ProblemAdmin(admin.ModelAdmin):
    list_display = ("order", "title", "level", "lesson")
    list_filter = ("level", "lesson")
    inlines = [TestCaseInline]


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at")
    fields = ("name", "password")
    help_text = "Password is hashed automatically on save."

    def save_model(self, request, obj, form, change):
        raw = form.cleaned_data.get("password", "")
        if raw and not raw.startswith(("pbkdf2_", "argon2", "bcrypt")):
            obj.set_password(raw)
            obj.session_version += 1
        super().save_model(request, obj, form, change)


@admin.register(Contest)
class ContestAdmin(admin.ModelAdmin):
    list_display = ("__str__", "started_at", "duration_seconds", "paused_at")


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ("group", "problem", "status", "contest_elapsed", "created_at")
    list_filter = ("status", "problem__level")


@admin.register(SavedCode)
class SavedCodeAdmin(admin.ModelAdmin):
    list_display = ("group", "problem", "updated_at")
