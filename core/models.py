from django.db import models
from django.contrib.auth.hashers import make_password, check_password
from django.utils import timezone

GROUP_HASHER = "pbkdf2_sha256_group"


class Group(models.Model):
    name = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=128)
    # Bumped to log out every device currently signed in as this group.
    session_version = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    def set_password(self, raw):
        self.password = make_password(raw, hasher=GROUP_HASHER)

    def check_password(self, raw):
        def upgrade(raw_password):
            self.set_password(raw_password)
            self.save(update_fields=["password"])
        return check_password(raw, self.password, setter=upgrade, preferred=GROUP_HASHER)

    def solved_problems(self):
        return Submission.objects.filter(
            group=self, status=Submission.Status.ACCEPTED
        ).values_list("problem_id", flat=True).distinct()

    def tries_count(self):
        return Submission.objects.filter(group=self).count()


class Contest(models.Model):
    """Singleton holding the contest clock state."""

    started_at = models.DateTimeField(null=True, blank=True)
    duration_seconds = models.PositiveIntegerField(default=3 * 60 * 60)
    paused_seconds = models.PositiveIntegerField(default=0)
    paused_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name_plural = "Contest"

    def __str__(self):
        return "Contest settings"

    @classmethod
    def get(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    @property
    def is_paused(self):
        return self.paused_at is not None

    def elapsed_seconds(self, now=None):
        if not self.started_at:
            return 0
        now = now or timezone.now()
        end = self.paused_at or now
        return max(0, int((end - self.started_at).total_seconds()) - self.paused_seconds)

    def remaining_seconds(self, now=None):
        return max(0, self.duration_seconds - self.elapsed_seconds(now))

    def is_running(self, now=None):
        if not self.started_at or self.is_paused:
            return False
        return self.remaining_seconds(now) > 0

    def is_open(self, now=None):
        """Accepting submissions (running and not paused)."""
        if not self.started_at:
            return False
        if self.is_paused:
            return False
        return self.remaining_seconds(now) > 0

    def state_label(self, now=None):
        if not self.started_at:
            return "not_started"
        if self.is_paused:
            return "paused"
        if self.remaining_seconds(now) <= 0:
            return "ended"
        return "running"


class Problem(models.Model):
    class Level(models.TextChoices):
        EASY = "easy", "Easy"
        MEDIUM = "medium", "Medium"
        HARD = "hard", "Hard"

    slug = models.SlugField(unique=True)
    title = models.CharField(max_length=200)
    level = models.CharField(max_length=10, choices=Level.choices)
    lesson = models.CharField(max_length=100, default="General")
    seq = models.PositiveIntegerField(default=0, help_text="Global order 1..N")
    order = models.PositiveIntegerField(default=0, help_text="Order within its level")
    statement = models.TextField(help_text="HTML allowed")
    input_format = models.TextField(blank=True)
    output_format = models.TextField(blank=True)
    hint = models.TextField(blank=True)
    starter_code = models.TextField(blank=True)

    class Meta:
        ordering = ["seq", "id"]

    def __str__(self):
        return f"{self.order}. {self.title}"

    @property
    def sample_test(self):
        return self.tests.filter(is_sample=True).first() or self.tests.first()


class TestCase(models.Model):
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE, related_name="tests")
    input_text = models.TextField()
    expected_output = models.TextField()
    is_sample = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]


class Submission(models.Model):
    class Status(models.TextChoices):
        ACCEPTED = "accepted", "Accepted"
        WRONG = "wrong", "Wrong Answer"
        ERROR = "error", "Error"
        TIMEOUT = "timeout", "Time Limit Exceeded"
        BLOCKED = "blocked", "Blocked code"

    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="submissions")
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE, related_name="submissions")
    code = models.TextField()
    status = models.CharField(max_length=10, choices=Status.choices)
    detail = models.JSONField(default=dict, blank=True)
    contest_elapsed = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.group} - {self.problem} - {self.status}"


class SavedCode(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    code = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("group", "problem")
