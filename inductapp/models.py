from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone  # <<< --- ADD THIS IMPORT

# Role choices for staff
ROLE_CHOICES = [
    ('admin', 'Administrator'),
    ('train_operator', 'Train Operator'),
    ('metro_officer', 'Metro Officer'),
    ('cleaner', 'Cleaner'),
    ('maintenance_worker', 'Maintenance Worker'),
    ('staff1', 'Staff Level 1'),
    ('staff2', 'Staff Level 2'),
]

STATUS_CHOICES = [
    ('ok', 'OK - Ready for Service'),
    ('minor_maintenance', 'Minor Maintenance Required'),
    ('cannot_schedule', 'Cannot Schedule - Critical Issues'),
]


class UserProfile(models.Model):
    """Extended user profile with role information."""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='staff1')
    employee_id = models.CharField(max_length=20, unique=True, null=True, blank=True)
    department = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"


class Train(models.Model):
    """Train model with all induction-related data."""
    train_number = models.CharField(max_length=20, unique=True)
    train_name = models.CharField(max_length=100)
    current_mileage = models.IntegerField(default=0)
    last_service_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ok')
    rank = models.IntegerField(default=99)
    status_notes = models.TextField(blank=True, help_text="Brief explanation of current status")
    current_stabling_bay = models.CharField(max_length=50, blank=True)
    cleaning_status = models.CharField(max_length=100, default='Clean')
    maintenance_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['rank', 'train_number']

    def __str__(self):
        return f"{self.train_number} - {self.train_name}"

    def get_status_color(self):
        color_map = {'ok': 'success', 'minor_maintenance': 'warning', 'cannot_schedule': 'danger'}
        return color_map.get(self.status, 'secondary')


class Certificate(models.Model):
    """Train certificates and documents."""
    train = models.ForeignKey(Train, on_delete=models.CASCADE, related_name='certificates')
    name = models.CharField(max_length=200)
    file = models.FileField(upload_to='certificates/')
    issue_date = models.DateField(null=True)
    expiry_date = models.DateField(null=True)
    is_verified = models.BooleanField(default=False)
    extracted_data = models.JSONField(null=True, blank=True)

    def __str__(self):
        return f"{self.train.train_number} - {self.name}"

    @property
    def is_expired(self):
        if self.expiry_date:
            return self.expiry_date < timezone.now().date()
        return False


class JobCard(models.Model):
    """Maintenance job cards."""
    train = models.ForeignKey(Train, on_delete=models.CASCADE, related_name='job_cards')
    title = models.CharField(max_length=200)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'), ('in_progress', 'In Progress'),
        ('completed', 'Completed'), ('cancelled', 'Cancelled')
    ], default='pending')
    priority = models.CharField(max_length=10, choices=[
        ('low', 'Low'), ('medium', 'Medium'),
        ('high', 'High'), ('critical', 'Critical')
    ], default='medium')
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.train.train_number} - {self.title}"