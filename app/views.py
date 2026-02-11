from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import IntegrityError
from .serializers import AllVoterSerializer
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError

class AllVoterBulkInsertAPI(APIView):
    """
    Insert ALL voter data from JSON array
    Django auto-generates ID
    JSON ID is ignored
    """

    def post(self, request):
        if not isinstance(request.data, list):
            return Response(
                {"error": "JSON array expected"},
                status=status.HTTP_400_BAD_REQUEST
            )

        created = 0
        skipped = 0

        for item in request.data:
            serializer = AllVoterSerializer(data=item)
            if serializer.is_valid():
                try:
                    serializer.save()  # id auto-generated here
                    created += 1
                except IntegrityError:
                    # duplicate voter_id
                    skipped += 1
            else:
                skipped += 1

        return Response(
            {
                "created": created,
                "skipped": skipped,
            },
            status=status.HTTP_201_CREATED
        )
        
        
        
     # views.py
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET
from django.db.models import Q
import json
from .models import AllVoter

from django.contrib.auth.decorators import login_required

@login_required
def voter_list(request):
    return render(request, 'voters/voter_management.html')



@require_GET
def get_voters(request):
    """API endpoint to get paginated and filtered voters"""
    # Get search parameters - UPDATED TO MATCH JAVASCRIPT
    search_global = request.GET.get('search', '').strip()  # Global search
    search_voter_id = request.GET.get('voter_id', '').strip()
    search_fathers_name = request.GET.get('fathers_name', '').strip()  # Changed from parents
    search_mothers_name = request.GET.get('mothers_name', '').strip()  # Changed from parents
    search_dob = request.GET.get('dob', '').strip()
    
    # Get sorting parameter
    sort_by = request.GET.get('sort', 'serial_asc')
    
    # Start with all voters
    voters = AllVoter.objects.all()
    
    # Apply filters
    if search_global:
        # Global search across all fields
        voters = voters.filter(
            Q(name__icontains=search_global) |
            Q(voter_id__icontains=search_global) |
            Q(fathers_name__icontains=search_global) |
            Q(mothers_name__icontains=search_global) |
            Q(address__icontains=search_global) |
            Q(dob__icontains=search_global) |
            Q(occupation__icontains=search_global) |
            Q(source_title__icontains=search_global)
        )
    else:
        # Individual field filters (for advanced search)
        if search_voter_id:
            voters = voters.filter(voter_id__icontains=search_voter_id)
        
        if search_fathers_name:
            voters = voters.filter(fathers_name__icontains=search_fathers_name)
        
        if search_mothers_name:
            voters = voters.filter(mothers_name__icontains=search_mothers_name)
        
        if search_dob:
            voters = voters.filter(dob__icontains=search_dob)
    
    # Apply sorting - IMPORTANT: Add this section
    if sort_by == 'serial_asc':
        voters = voters.order_by('serial')
    elif sort_by == 'serial_desc':
        voters = voters.order_by('-serial')
    # Add more sorting options if needed
    elif sort_by == 'name_asc':
        voters = voters.order_by('name')
    elif sort_by == 'name_desc':
        voters = voters.order_by('-name')
    elif sort_by == 'voter_id_asc':
        voters = voters.order_by('voter_id')
    elif sort_by == 'voter_id_desc':
        voters = voters.order_by('-voter_id')
    else:
        # Default sorting by serial ascending
        voters = voters.order_by('serial')
    
    # Get pagination parameters
    page = int(request.GET.get('page', 1))
    per_page = int(request.GET.get('per_page', 25))
    
    # Create paginator
    paginator = Paginator(voters, per_page)
    
    try:
        voters_page = paginator.page(page)
    except:
        voters_page = paginator.page(1)
    
    # Serialize voters
    voters_data = []
    for voter in voters_page:
        voters_data.append({
            'id': voter.id,
            'serial': voter.serial,
            'name': voter.name,
            'voter_id': voter.voter_id,
            'fathers_name': voter.fathers_name,
            'mothers_name': voter.mothers_name,
            'occupation': voter.occupation if voter.occupation else '',
            'dob': voter.dob if voter.dob else '',
            'address': voter.address,
            'source_title': voter.source_title if voter.source_title else '',
            'created_at': voter.created_at.strftime('%Y-%m-%d %H:%M'),
            'updated_at': voter.updated_at.strftime('%Y-%m-%d %H:%M')
        })
    
    return JsonResponse({
        'voters': voters_data,
        'total': paginator.count,
        'page': page,
        'per_page': per_page,
        'total_pages': paginator.num_pages,
        'sort_order': sort_by  # Optional: send back the sort order
    })
    
@csrf_exempt
@require_POST
def create_voter(request):
    """API endpoint to create a new voter"""
    try:
        data = json.loads(request.body)
        
        # Handle serial conversion to integer
        serial_value = data['serial']
        # Remove any non-numeric characters and convert to integer
        if isinstance(serial_value, str):
            # Extract numbers from string
            import re
            numbers = re.findall(r'\d+', serial_value)
            if numbers:
                serial_value = int(numbers[0])
            else:
                serial_value = 0
        elif isinstance(serial_value, (int, float)):
            serial_value = int(serial_value)
        else:
            serial_value = 0
        
        voter = AllVoter.objects.create(
            serial=serial_value,
            name=data['name'],
            voter_id=data['voter_id'],
            fathers_name=data['fathers_name'],
            mothers_name=data['mothers_name'],
            occupation=data.get('occupation', ''),
            dob=data.get('dob', ''),
            address=data['address'],
            source_title=data.get('source_title', '')
        )
        
        return JsonResponse({
            'success': True,
            'message': 'ভোটার সফলভাবে যোগ করা হয়েছে',
            'voter_id': voter.id
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'ত্রুটি: {str(e)}'
        }, status=400)

@csrf_exempt
@require_POST
def update_voter(request, voter_id):
    """API endpoint to update an existing voter"""
    try:
        voter = get_object_or_404(AllVoter, id=voter_id)
        data = json.loads(request.body)
        
        # Handle serial conversion to integer (same as create)
        serial_value = data['serial']
        if isinstance(serial_value, str):
            import re
            numbers = re.findall(r'\d+', serial_value)
            if numbers:
                serial_value = int(numbers[0])
            else:
                serial_value = 0
        elif isinstance(serial_value, (int, float)):
            serial_value = int(serial_value)
        else:
            serial_value = 0
        
        voter.serial = serial_value
        voter.name = data['name']
        voter.voter_id = data['voter_id']
        voter.fathers_name = data['fathers_name']
        voter.mothers_name = data['mothers_name']
        voter.occupation = data.get('occupation', '')
        voter.dob = data.get('dob', '')
        voter.address = data['address']
        voter.source_title = data.get('source_title', '')
        voter.save()
        
        return JsonResponse({
            'success': True,
            'message': 'ভোটার সফলভাবে আপডেট করা হয়েছে'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'ত্রুটি: {str(e)}'
        }, status=400)

@csrf_exempt
@require_POST
def delete_voter(request, voter_id):
    """API endpoint to delete a voter"""
    try:
        voter = get_object_or_404(AllVoter, id=voter_id)
        voter.delete()
        
        return JsonResponse({
            'success': True,
            'message': 'ভোটার সফলভাবে মুছে ফেলা হয়েছে'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'ত্রুটি: {str(e)}'
        }, status=400)

@require_GET
def get_voter_detail(request, voter_id):
    """API endpoint to get details of a specific voter"""
    try:
        voter = get_object_or_404(AllVoter, id=voter_id)
        
        return JsonResponse({
            'success': True,
            'voter': {
                'id': voter.id,
                'serial': voter.serial,
                'name': voter.name,
                'voter_id': voter.voter_id,
                'fathers_name': voter.fathers_name,
                'mothers_name': voter.mothers_name,
                'occupation': voter.occupation if voter.occupation else '',
                'dob': voter.dob if voter.dob else '',
                'address': voter.address,
                'source_title': voter.source_title if voter.source_title else ''
            }
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'ত্রুটি: {str(e)}'
        }, status=404)
        
        
        



def custom_login(request):
    if request.user.is_authenticated:
        return redirect('login')
    
    if request.method == 'POST':
        # Get username/email from form
        username_or_email = request.POST.get('username')
        password = request.POST.get('password')
        
        # Try to authenticate with username first
        user = authenticate(request, username=username_or_email, password=password)
        
        # If authentication fails, try with email
        if user is None:
            try:
                from django.contrib.auth.models import User
                user_obj = User.objects.get(email=username_or_email)
                user = authenticate(request, username=user_obj.username, password=password)
            except User.DoesNotExist:
                user = None
        
        if user is not None:
            login(request, user)
            next_url = request.GET.get('next', 'home')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid username/email or password.')
    
    return render(request, 'login.html')


