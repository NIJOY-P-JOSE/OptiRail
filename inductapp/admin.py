from django.contrib import admin
from .models import UserProfile, Train, Certificate, JobCard

# These inline classes are necessary for the improved TrainAdmin
class CertificateInline(admin.TabularInline):
    model = Certificate
    extra = 1 # Shows one empty form to add a new item

class JobCardInline(admin.TabularInline):
    model = JobCard
    extra = 1

# --- Your original, detailed admin views ---

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'employee_id', 'department')
    list_filter = ('role', 'department')
    search_fields = ('user__username', 'employee_id')

@admin.register(Train)
class TrainAdmin(admin.ModelAdmin):
    list_display = ('train_number', 'train_name', 'status', 'rank', 'current_mileage')
    list_filter = ('status',) # Removed 'model' as it is not in your final model
    search_fields = ('train_number', 'train_name')
    ordering = ['rank']
    
    # KEY ADDITION: This line adds the ability to manage certificates 
    # and job cards from within the train's detail page in the admin.
    inlines = [CertificateInline, JobCardInline]

@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    # 'upload_date' is not in the final Certificate model, replaced with issue/expiry dates
    list_display = ('train', 'name', 'issue_date', 'expiry_date', 'is_verified')
    list_filter = ('is_verified', 'expiry_date')
    search_fields = ('name', 'train__train_number')

@admin.register(JobCard)
class JobCardAdmin(admin.ModelAdmin):
    # 'assigned_to' is not in the final JobCard model
    list_display = ('train', 'title', 'status', 'priority', 'created_at')
    list_filter = ('status', 'priority')
    search_fields = ('title', 'train__train_number')