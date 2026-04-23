from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Avg
from .forms import (StudentRegistrationForm, LandlordRegistrationForm, 
                    UserLoginForm, StudentProfileUpdateForm, 
                    LandlordProfileUpdateForm, ReviewForm)
from .models import User, StudentProfile, LandlordProfile, Review

def register(request):
    """Unified registration view for both students and landlords"""
    student_form = None
    landlord_form = None
    # Check if user_type is passed in GET parameter (from property rent ad link)
    selected_user_type = request.GET.get('type', 'student')
    
    if request.method == 'POST':
        user_type = request.POST.get('user_type')
        selected_user_type = user_type
        
        if user_type == 'student':
            form = StudentRegistrationForm(request.POST)
            student_form = form
        elif user_type == 'landlord':
            form = LandlordRegistrationForm(request.POST)
            landlord_form = form
        else:
            messages.error(request, 'Please select a user type.')
            return render(request, 'accounts/register.html', {
                'selected_user_type': selected_user_type
            })
        
        if form.is_valid():
            try:
                user = form.save()
                login(request, user)
                messages.success(request, 'Registration successful! Welcome to BidNest.')
                
                # Check if there's a next parameter to redirect after registration
                next_url = request.GET.get('next') or request.POST.get('next')
                if next_url:
                    return redirect(next_url)
                
                if user_type == 'student':
                    return redirect('property_list')
                else:
                    return redirect('landlord_dashboard')
            except Exception as e:
                messages.error(request, f'Registration error: {str(e)}')
        else:
            # Show form errors
            for field, errors in form.errors.items():
                for error in errors:
                    if field == '__all__':
                        messages.error(request, f'{error}')
                    else:
                        messages.error(request, f'{field}: {error}')
    
    return render(request, 'accounts/register.html', {
        'student_form': student_form,
        'landlord_form': landlord_form,
        'selected_user_type': selected_user_type
    })


def register_student(request):
    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful! Please complete your profile.')
            return redirect('student_profile')
    else:
        form = StudentRegistrationForm()
    return render(request, 'accounts/register_student.html', {'form': form})


def register_landlord(request):
    if request.method == 'POST':
        form = LandlordRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful! Please complete your profile.')
            return redirect('landlord_profile')
    else:
        form = LandlordRegistrationForm()
    return render(request, 'accounts/register_landlord.html', {'form': form})


def user_login(request):
    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {user.username}!')
                
                # Redirect all users to home page
                return redirect('home')
    else:
        form = UserLoginForm()
    return render(request, 'accounts/login.html', {'form': form})


@login_required
def user_logout(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')


@login_required
def student_profile(request):
    if request.user.user_type != 'student':
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    profile = get_object_or_404(StudentProfile, user=request.user)
    
    if request.method == 'POST':
        form = StudentProfileUpdateForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('student_profile')
    else:
        form = StudentProfileUpdateForm(instance=profile)
    
    return render(request, 'accounts/student_profile.html', {'form': form, 'profile': profile})


@login_required
def landlord_profile(request):
    if request.user.user_type != 'landlord':
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    profile = get_object_or_404(LandlordProfile, user=request.user)
    
    if request.method == 'POST':
        form = LandlordProfileUpdateForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('landlord_profile')
    else:
        form = LandlordProfileUpdateForm(instance=profile)
    
    return render(request, 'accounts/landlord_profile.html', {'form': form, 'profile': profile})


@login_required
def landlord_dashboard(request):
    if request.user.user_type != 'landlord':
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    profile = get_object_or_404(LandlordProfile, user=request.user)
    properties = request.user.properties.all()
    reviews = Review.objects.filter(landlord=request.user)
    
    context = {
        'profile': profile,
        'properties': properties,
        'reviews': reviews,
        'total_properties': properties.count(),
    }
    return render(request, 'accounts/landlord_dashboard.html', context)


@login_required
def add_review(request, landlord_id):
    if request.user.user_type != 'student':
        messages.error(request, 'Only students can leave reviews.')
        return redirect('home')
    
    landlord = get_object_or_404(User, id=landlord_id, user_type='landlord')
    
    # Check if student already reviewed this landlord
    existing_review = Review.objects.filter(student=request.user, landlord=landlord).first()
    if existing_review:
        messages.warning(request, 'You have already reviewed this landlord. You can edit your existing review.')
        return redirect('edit_review', review_id=existing_review.id)
    
    # Check eligibility - Only students who have an active or completed contract can review
    from contracts.models import Contract
    has_contract = Contract.objects.filter(
        student=request.user,
        property__landlord=landlord,
        status__in=['active', 'completed']  # Allow reviews for active and completed contracts
    ).exists()
    
    if not has_contract:
        messages.error(request, 'You can only review landlords you have rented from. You need an active or completed rental contract.')
        return redirect('landlord_detail', landlord_id=landlord.id)
    
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.student = request.user
            review.landlord = landlord
            review.save()
            
            # Auto-verify if student has completed contract
            review.verify_review()
            
            # Update landlord's average rating
            landlord_profile = landlord.landlord_profile
            reviews = Review.objects.filter(landlord=landlord)
            landlord_profile.average_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0
            landlord_profile.total_reviews = reviews.count()
            landlord_profile.save()
            
            # Create notification for landlord
            from notifications.views import create_notification
            create_notification(
                user=landlord,
                notification_type='review',
                title='New Review Received',
                message=f'{request.user.get_full_name() or request.user.username} left a {review.rating}-star review for you.',
                link=f'/accounts/landlord/dashboard/'
            )
            
            messages.success(request, 'Review submitted successfully!')
            return redirect('landlord_detail', landlord_id=landlord.id)
    else:
        form = ReviewForm()
    
    return render(request, 'accounts/add_review.html', {'form': form, 'landlord': landlord})


@login_required
def edit_review(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    
    # Check permissions
    if request.user != review.student:
        messages.error(request, 'You can only edit your own reviews.')
        return redirect('home')
    
    # Check if can still edit (within 30 days)
    if not review.can_edit(request.user):
        messages.error(request, 'Reviews can only be edited within 30 days of posting.')
        return redirect('landlord_detail', landlord_id=review.landlord.id)
    
    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            
            # Update landlord's average rating
            landlord_profile = review.landlord.landlord_profile
            reviews = Review.objects.filter(landlord=review.landlord)
            landlord_profile.average_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0
            landlord_profile.save()
            
            messages.success(request, 'Review updated successfully!')
            return redirect('landlord_detail', landlord_id=review.landlord.id)
    else:
        form = ReviewForm(instance=review)
    
    context = {
        'form': form,
        'review': review,
        'landlord': review.landlord,
        'is_edit': True,
    }
    return render(request, 'accounts/add_review.html', context)


@login_required
def delete_review(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    
    # Check permissions
    if request.user != review.student:
        messages.error(request, 'You can only delete your own reviews.')
        return redirect('home')
    
    landlord_id = review.landlord.id
    
    if request.method == 'POST':
        review.delete()
        
        # Update landlord's average rating
        landlord_profile = User.objects.get(id=landlord_id).landlord_profile
        reviews = Review.objects.filter(landlord_id=landlord_id)
        landlord_profile.average_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0
        landlord_profile.total_reviews = reviews.count()
        landlord_profile.save()
        
        messages.success(request, 'Review deleted successfully.')
        return redirect('landlord_detail', landlord_id=landlord_id)
    
    return render(request, 'accounts/delete_review.html', {'review': review})


@login_required
def respond_to_review(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    
    # Check permissions - only the landlord being reviewed can respond
    if request.user != review.landlord:
        messages.error(request, 'You can only respond to reviews about you.')
        return redirect('home')
    
    if request.method == 'POST':
        response = request.POST.get('response', '').strip()
        if response:
            from django.utils import timezone
            review.landlord_response = response
            review.response_date = timezone.now()
            review.save()
            
            # Create notification for the student
            from notifications.views import create_notification
            create_notification(
                user=review.student,
                notification_type='review',
                title='Landlord Responded to Your Review',
                message=f'{request.user.get_full_name() or request.user.username} responded to your review.',
                link=f'/accounts/landlord/{review.landlord.id}/'
            )
            
            messages.success(request, 'Response posted successfully!')
        else:
            messages.error(request, 'Response cannot be empty.')
        
        return redirect('landlord_dashboard')
    
    return render(request, 'accounts/respond_review.html', {'review': review})


def landlord_detail(request, landlord_id):
    landlord = get_object_or_404(User, id=landlord_id, user_type='landlord')
    profile = landlord.landlord_profile
    properties = landlord.properties.filter(is_active=True)
    reviews = Review.objects.filter(landlord=landlord)
    
    # Check if current user can review this landlord
    can_review = False
    if request.user.is_authenticated and request.user.user_type == 'student':
        # Check if student hasn't already reviewed
        already_reviewed = Review.objects.filter(
            student=request.user,
            landlord=landlord
        ).exists()
        
        if not already_reviewed:
            # Check if student has active or completed contract with this landlord
            from contracts.models import Contract
            has_contract = Contract.objects.filter(
                student=request.user,
                property__landlord=landlord,
                status__in=['active', 'completed']  # Allow reviews for active and completed contracts
            ).exists()
            can_review = has_contract
    
    context = {
        'landlord': landlord,
        'profile': profile,
        'properties': properties,
        'reviews': reviews,
        'can_review': can_review,
    }
    return render(request, 'accounts/landlord_detail.html', context)

