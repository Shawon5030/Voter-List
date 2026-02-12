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
        
import json
import re
from django.http import JsonResponse
from django.db.models import Q
from django.core.paginator import Paginator
from django.views.decorators.http import require_GET, require_POST
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import AllVoter

# --- সহায়ক ফাংশন (Helper Function) ---
def clean_search_term(term):
    """সার্চ টার্ম থেকে ডট (.) এবং বাড়তি স্পেস রিমুভ করে সার্চ সহজ করে"""
    if not term:
        return ""
    # ডট এবং স্পেস রিমুভ করা হচ্ছে যাতে 'মোঃ মুনির' এবং 'মুনির' একই রেজাল্ট দেয়
    return re.sub(r'[\.\s]', '', term)

# --- টেমপ্লেট ভিউ ---
@login_required
def voter_list(request):
    """ভোট ব্যবস্থাপনার মূল পেজ লোড করবে"""
    return render(request, 'voters/voter_management.html')

# --- API এন্ডপয়েন্টস ---

@require_GET
def get_voters(request):
    """সঠিক সর্টিং এবং উন্নত ফিল্টারিং সহ ভোটার লিস্ট রিটার্ন করবে"""
    # সার্চ প্যারামিটার গ্রহণ
    search_global = request.GET.get('search', '').strip()
    search_voter_id = request.GET.get('voter_id', '').strip()
    search_fathers_name = request.GET.get('fathers_name', '').strip()
    search_mothers_name = request.GET.get('mothers_name', '').strip()
    search_dob = request.GET.get('dob', '').strip()
    
    # সর্টিং প্যারামিটার (ডিফল্ট: সিরিয়াল অনুযায়ী ছোট থেকে বড়)
    sort_by = request.GET.get('sort', 'serial_asc')
    
    voters = AllVoter.objects.all()
    
    # ১. উন্নত গ্লোবাল সার্চ লজিক
    if search_global:
        cleaned_term = clean_search_term(search_global)
        voters = voters.filter(
            Q(name__icontains=search_global) |
            Q(name__icontains=cleaned_term) | # ডট/স্পেস ছাড়া সার্চ
            Q(voter_id__icontains=search_global) |
            Q(fathers_name__icontains=search_global) |
            Q(mothers_name__icontains=search_global) |
            Q(address__icontains=search_global)
        ).distinct()

    # ২. আলাদা ফিল্ড ফিল্টার (Advanced Filter)
    if search_voter_id:
        voters = voters.filter(voter_id__icontains=search_voter_id)
    if search_fathers_name:
        voters = voters.filter(fathers_name__icontains=search_fathers_name)
    if search_mothers_name:
        voters = voters.filter(mothers_name__icontains=search_mothers_name)
    if search_dob:
        voters = voters.filter(dob__icontains=search_dob)

    # ৩. সর্টিং হ্যান্ডলিং (সিরিয়াল ০0০১, ০0১৬ এর অর্ডার ঠিক রাখা)
    if sort_by == 'serial_asc':
        voters = voters.order_by('serial')
    elif sort_by == 'serial_desc':
        voters = voters.order_by('-serial')
    elif sort_by == 'name_asc':
        voters = voters.order_by('name')
    elif sort_by == 'name_desc':
        voters = voters.order_by('-name')
    else:
        # ডিফল্টভাবে সিরিয়াল অনুযায়ী ছোট থেকে বড় সাজানো
        voters = voters.order_by('serial')

    # ৪. পেজিনেশন
    page = int(request.GET.get('page', 1))
    per_page = int(request.GET.get('per_page', 25))
    paginator = Paginator(voters, per_page)
    
    try:
        voters_page = paginator.page(page)
    except:
        voters_page = paginator.page(1)

    # ডাটা ফরম্যাটিং
    voters_data = []
    for voter in voters_page:
        voters_data.append({
            'id': voter.id,
            # ডাটাবেজে ইন্টিজার থাকলেও ডিসপ্লেতে ৪ ডিজিট (যেমন: 0001) দেখাবে
            'serial': str(voter.serial).zfill(4), 
            'name': voter.name,
            'voter_id': voter.voter_id,
            'fathers_name': voter.fathers_name,
            'mothers_name': voter.mothers_name,
            'occupation': voter.occupation or '',
            'dob': voter.dob or '',
            'address': voter.address,
            'source_title': voter.source_title or '',
        })
    
    return JsonResponse({
        'voters': voters_data,
        'total': paginator.count,
        'page': page,
        'per_page': per_page,
        'total_pages': paginator.num_pages,
        'sort_order': sort_by
    })

@require_GET
def get_voter_detail(request, voter_id):
    """নির্দিষ্ট ভোটারের বিস্তারিত তথ্য রিটার্ন করবে"""
    voter = get_object_or_404(AllVoter, id=voter_id)
    return JsonResponse({
        'success': True,
        'voter': {
            'id': voter.id,
            'serial': str(voter.serial).zfill(4),
            'name': voter.name,
            'voter_id': voter.voter_id,
            'fathers_name': voter.fathers_name,
            'mothers_name': voter.mothers_name,
            'occupation': voter.occupation or '',
            'dob': voter.dob or '',
            'address': voter.address,
            'source_title': voter.source_title or ''
        }
    })

@csrf_exempt
@require_POST
def create_voter(request):
    """নতুন ভোটার রেকর্ড তৈরি"""
    try:
        data = json.loads(request.body)
        serial_val = data.get('serial', '0')
        # বাংলা বা ইংলিশ ইনপুট যাই হোক, শুধু সংখ্যা ফিল্টার করে ইন্টিজার বানানো হচ্ছে
        clean_serial = int(re.sub(r'\D', '', str(serial_val))) if str(serial_val) else 0
        
        voter = AllVoter.objects.create(
            serial=clean_serial,
            name=data['name'],
            voter_id=data['voter_id'],
            fathers_name=data['fathers_name'],
            mothers_name=data['mothers_name'],
            address=data['address'],
            dob=data.get('dob', ''),
            source_title=data.get('source_title', '')
        )
        return JsonResponse({'success': True, 'message': 'ভোটার সফলভাবে যোগ করা হয়েছে'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)

@csrf_exempt
@require_POST
def update_voter(request, voter_id):
    """বিদ্যমান ভোটার রেকর্ড আপডেট"""
    try:
        voter = get_object_or_404(AllVoter, id=voter_id)
        data = json.loads(request.body)
        
        serial_val = data.get('serial', voter.serial)
        voter.serial = int(re.sub(r'\D', '', str(serial_val)))
        voter.name = data['name']
        voter.voter_id = data['voter_id']
        voter.fathers_name = data['fathers_name']
        voter.mothers_name = data['mothers_name']
        voter.address = data['address']
        voter.save()
        
        return JsonResponse({'success': True, 'message': 'আপডেট সফল হয়েছে'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)

@csrf_exempt
@require_POST
def delete_voter(request, voter_id):
    """ভোটার রেকর্ড মুছে ফেলা"""
    voter = get_object_or_404(AllVoter, id=voter_id)
    voter.delete()
    return JsonResponse({'success': True, 'message': 'সফলভাবে মুছে ফেলা হয়েছে'})

def custom_login(request):
    """ইউজারনাম অথবা ইমেইল দিয়ে লগইন লজিক"""
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        u_name = request.POST.get('username')
        pwd = request.POST.get('password')
        
        user = authenticate(request, username=u_name, password=pwd)
        if user is None:
            try:
                from django.contrib.auth.models import User
                user_obj = User.objects.get(email=u_name)
                user = authenticate(request, username=user_obj.username, password=pwd)
            except User.DoesNotExist:
                user = None
        
        if user:
            login(request, user)
            return redirect(request.GET.get('next', 'home'))
        else:
            messages.error(request, 'ইউজারনাম বা পাসওয়ার্ড ভুল।')
            
    return render(request, 'login.html')