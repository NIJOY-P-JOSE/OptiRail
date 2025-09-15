from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
from .models import Train, Certificate, JobCard, UserProfile, ROLE_CHOICES
import json
import csv
import io
import pandas as pd
from datetime import datetime, date
import os


# Mock data for demonstration
MOCK_TRAINS = [
    {
        'id': 1,
        'train_number': 'KM-001',
        'train_name': 'Aluva Express',
        'status': 'ok',
        'rank': 1,
        'current_mileage': 45320,
        'status_notes': 'All systems operational',
        'current_stabling_bay': 'Bay-A1',
        'cleaning_status': 'Clean',
        'last_service_date': '2024-01-15',
    },
    {
        'id': 2,
        'train_number': 'KM-002', 
        'train_name': 'Kochi Central',
        'status': 'minor_maintenance',
        'rank': 2,
        'current_mileage': 38750,
        'status_notes': 'Minor brake pad replacement needed',
        'current_stabling_bay': 'Bay-B2',
        'cleaning_status': 'Needs cleaning',
        'last_service_date': '2024-01-10',
    },
    {
        'id': 3,
        'train_number': 'KM-003',
        'train_name': 'Ernakulam South',
        'status': 'cannot_schedule',
        'rank': 5,
        'current_mileage': 52100,
        'status_notes': 'Critical electrical system fault - requires immediate attention',
        'current_stabling_bay': 'Maintenance Bay',
        'cleaning_status': 'Clean',
        'last_service_date': '2024-01-05',
    },
    {
        'id': 4,
        'train_number': 'KM-004',
        'train_name': 'Marine Drive',
        'status': 'ok',
        'rank': 3,
        'current_mileage': 41200,
        'status_notes': 'Recently serviced, all systems green',
        'current_stabling_bay': 'Bay-A2',
        'cleaning_status': 'Clean',
        'last_service_date': '2024-01-20',
    },
    {
        'id': 5,
        'train_number': 'KM-005',
        'train_name': 'Kaloor Specialist',
        'status': 'minor_maintenance',
        'rank': 4,
        'current_mileage': 33900,
        'status_notes': 'Scheduled maintenance due next week',
        'current_stabling_bay': 'Bay-B1',
        'cleaning_status': 'Needs deep cleaning',
        'last_service_date': '2024-01-12',
    },
     {
        'id': 6,
        'train_number': 'KM-006',
        'train_name': 'Aluva Express',
        'status': 'ok',
        'rank': 1,
        'current_mileage': 45320,
        'status_notes': 'All systems operational',
        'current_stabling_bay': 'Bay-A1',
        'cleaning_status': 'Clean',
        'last_service_date': '2024-01-15',
    },
]


def get_mock_train(train_id):
    """Get mock train data by ID."""
    for train in MOCK_TRAINS:
        if train['id'] == int(train_id):
            return train
    return None



def login_view(request):
    """Handle user login with role assignment."""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # Mock authentication - for demo: any username/password combo works
        if username and password:
            # Save user info in session
            request.session['user_id'] = username
            request.session['username'] = username
            
            # Assign role based on username
            role_mapping = {
                'admin': 'admin',
                'operator': 'train_operator', 
                'officer': 'metro_officer',
                'cleaner': 'cleaner',
                'maintenance': 'maintenance_worker',
                'staff1': 'staff1',
                'staff2': 'staff2'
            }
            
            assigned_role = 'admin'  # Default role
            for key, role in role_mapping.items():
                if key in username.lower():
                    assigned_role = role
                    break
            
            request.session['user_role'] = assigned_role
            request.session['is_authenticated'] = True   # store as boolean
            
            messages.success(request, f'Welcome! Logged in as {assigned_role.replace("_", " ").title()}')
            return redirect('ranklist')
        else:
            messages.error(request, 'Please enter both username and password')
    
    return render(request, 'inductapp/login.html')


def logout_view(request):
    """Handle user logout."""
    request.session.flush()  # clears the session
    messages.success(request, 'You have been logged out successfully')
    return redirect('login')


def ranklist_view(request):
    """Display ranked list of trains with search and filtering."""
    if not request.session.get('is_authenticated', False):
        return redirect('login')
    
    # Get sorting parameter
    sort_by = request.GET.get('sort', 'rank')
    search_query = request.GET.get('search', '').strip()
    
    trains = MOCK_TRAINS.copy()
    
    # Apply search filter
    if search_query:
        trains = [t for t in trains if 
                 search_query.lower() in t['train_number'].lower() or 
                 search_query.lower() in t['train_name'].lower()]
    
    # Apply sorting
    if sort_by == 'mileage':
        trains.sort(key=lambda x: x['current_mileage'], reverse=True)
    elif sort_by == 'date':
        trains.sort(key=lambda x: x['last_service_date'], reverse=True)
    else:  # Default to rank
        trains.sort(key=lambda x: x['rank'])
    
    context = {
        'trains': trains,
        'current_sort': sort_by,
        'search_query': search_query,
        'user_role': request.session.get('user_role', 'staff1'),
        'username': request.session.get('username', 'User')
    }
    
    return render(request, 'inductapp/ranklist.html', context)



def train_detail_view(request, train_id):
    """Display detailed train information with role-based editing."""
    if not request.session.get('is_authenticated'):
        return redirect('login')
        
    train = get_mock_train(train_id)
    if not train:
        messages.error(request, 'Train not found')
        return redirect('ranklist')
    
    user_role = request.session.get('user_role', 'staff1')
    
    # Handle form submission for updates
    if request.method == 'POST':
        # Mock update - in production, save to database
        field_name = request.POST.get('field_name')
        field_value = request.POST.get('field_value')
        
        # Check permissions
        can_edit = can_user_edit_field(user_role, field_name)
        
        if can_edit:
            # Update mock data
            if field_name in train:
                train[field_name] = field_value
                messages.success(request, f'Updated {field_name} successfully')
            else:
                messages.error(request, 'Invalid field')
        else:
            messages.error(request, 'You do not have permission to edit this field')
        
        return redirect('train_detail', train_id=train_id)
    
    # Mock certificates and job cards
    mock_certificates = [
        {'id': 1, 'name': 'Safety Certificate', 'upload_date': '2024-01-15', 'is_verified': True},
        {'id': 2, 'name': 'Maintenance Record', 'upload_date': '2024-01-10', 'is_verified': False}
    ]
    
    mock_job_cards = [
        {'id': 1, 'title': 'Brake Inspection', 'status': 'completed', 'priority': 'medium'},
        {'id': 2, 'title': 'Engine Check', 'status': 'pending', 'priority': 'high'}
    ]
    
    context = {
        'train': train,
        'certificates': mock_certificates,
        'job_cards': mock_job_cards,
        'user_role': user_role,
        'can_edit': get_user_permissions(user_role),
        'username': request.session.get('username', 'User')
    }
    
    return render(request, 'inductapp/train_detail.html', context)


def can_user_edit_field(role, field_name):
    """Check if user role can edit specific field."""
    role_permissions = {
        'admin': ['*'],  # Admin can edit everything
        'train_operator': ['current_mileage', 'operational_notes'],
        'metro_officer': ['status_notes', 'inspection_notes', 'status'],
        'cleaner': ['cleaning_status', 'cleaning_notes'],
        'maintenance_worker': ['maintenance_notes', 'status'],
        'staff1': ['cleaning_status'],
        'staff2': ['cleaning_status', 'operational_notes'],
    }
    
    user_perms = role_permissions.get(role, [])
    return '*' in user_perms or field_name in user_perms


def get_user_permissions(role):
    """Get all fields user can edit."""
    role_permissions = {
        'admin': ['*'],
        'train_operator': ['current_mileage', 'operational_notes'],
        'metro_officer': ['status_notes', 'inspection_notes', 'status'],
        'cleaner': ['cleaning_status', 'cleaning_notes'], 
        'maintenance_worker': ['maintenance_notes', 'status'],
        'staff1': ['cleaning_status'],
        'staff2': ['cleaning_status', 'operational_notes'],
    }
    
    return role_permissions.get(role, [])



def upload_view(request):
    """Handle CSV/Excel file uploads."""
    if not request.session.get('is_authenticated', False):
        return redirect('login')
        
    context = {
        'user_role': request.session.get('user_role', 'staff1'),
        'username': request.session.get('username', 'User')
    }
    
    if request.method == 'POST' and request.FILES.get('file'):
        uploaded_file = request.FILES['file']
        
        try:
            # Read file based on extension
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            elif uploaded_file.name.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(uploaded_file)
            else:
                messages.error(request, 'Please upload a CSV or Excel file')
                return render(request, 'inductapp/upload.html', context)
            
            # Convert to list of dicts for template
            preview_data = df.to_dict('records')[:10]  # Show first 10 rows
            column_names = list(df.columns)
            
            context.update({
                'preview_data': preview_data,
                'column_names': column_names,
                'total_rows': len(df),
                'file_name': uploaded_file.name
            })
            
            # Store data in session for import
            request.session['upload_data'] = df.to_dict('records')
            
        except Exception as e:
            messages.error(request, f'Error reading file: {str(e)}')
    
    return render(request, 'inductapp/upload.html', context)



# API Endpoints

@csrf_exempt
def api_import_data(request):
    """Import uploaded CSV/Excel data to database."""
    if request.method == 'POST':
        upload_data = request.session.get('upload_data', [])
        
        if not upload_data:
            return JsonResponse({'error': 'No data to import'}, status=400)
        
        # Mock import process - replace with actual DB operations
        imported_count = len(upload_data)
        
        # Clear session data
        request.session.pop('upload_data', None)
        
        return JsonResponse({
            'success': True,
            'message': f'Successfully imported {imported_count} records',
            'imported_count': imported_count
        })
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)


@csrf_exempt  
def api_chat(request):
    """Handle chatbot conversations."""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_message = data.get('message', '').strip()
            
            # Mock AI responses - replace with actual AI integration
            mock_responses = {
                'hello': 'Hello! I\'m the Kochi Metro AI assistant. How can I help you today?',
                'trains': 'I can help you with train information, maintenance schedules, and operational queries.',
                'status': 'You can check train status on the ranklist page. Red means critical issues, orange is minor maintenance, and green is ready for service.',
                'help': 'I can assist with: train status, maintenance queries, certificate verification, and general metro operations questions.',
                'default': 'I understand you\'re asking about metro operations. Could you be more specific about what information you need?'
            }
            
            # Simple keyword matching
            response = mock_responses['default']
            for keyword, reply in mock_responses.items():
                if keyword in user_message.lower():
                    response = reply
                    break
            
            return JsonResponse({
                'success': True,
                'response': response,
                'timestamp': datetime.now().isoformat()
            })
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)


@csrf_exempt
def api_extract_certificate(request):
    """Extract data from uploaded certificates using AI OCR."""
    if request.method == 'POST' and request.FILES.get('certificate'):
        uploaded_file = request.FILES['certificate']
        
        # Save file temporarily
        file_name = default_storage.save(f'temp/{uploaded_file.name}', ContentFile(uploaded_file.read()))
        
        # Mock AI extraction - replace with actual OCR/ML integration
        mock_extracted_data = {
            'certificate_type': 'Safety Compliance Certificate',
            'issued_to': 'Kochi Metro Rail Corporation',
            'issue_date': '2024-01-15',
            'expiry_date': '2025-01-15',
            'certificate_number': 'KM-SAFETY-2024-001',
            'issuing_authority': 'Railway Safety Commissioner',
            'train_number': 'KM-001',
            'compliance_status': 'VALID',
            'extracted_fields': {
                'safety_rating': 'A+',
                'last_inspection': '2024-01-10',
                'next_inspection': '2024-07-10'
            }
        }
        
        return JsonResponse({
            'success': True,
            'extracted_data': mock_extracted_data,
            'file_path': file_name,
            'confidence_score': 0.95
        })
    
    return JsonResponse({'error': 'No file uploaded'}, status=400)



# inductapp/views.py

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from .models import Train # Make sure Train is imported
import csv
import io
from datetime import datetime




@csrf_exempt
def api_generate_report(request):
    """Generate and download reports from the database."""
    
    # This view now accepts GET requests
    if request.method == 'GET':
        try:
            # Get data from the DATABASE, not mock data
            trains = Train.objects.all().values(
                'rank', 'train_number', 'train_name', 'status', 
                'current_mileage', 'cleaning_status', 
                'current_stabling_bay', 'status_notes'
            )
            
            if not trains:
                return JsonResponse({'error': 'No train data to report'}, status=404)

            # Generate CSV in memory
            output = io.StringIO()
            writer = csv.DictWriter(output, fieldnames=trains[0].keys())
            writer.writeheader()
            writer.writerows(trains)
            
            # Create the HttpResponse object with the correct content-type header.
            response = HttpResponse(output.getvalue(), content_type='text/csv')
            filename = f'metro_trains_report_{datetime.now().strftime("%Y%m%d")}.csv'
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            
            return response

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)











