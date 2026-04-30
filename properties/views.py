from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import models
from django.db.models import Q
from django.core.paginator import Paginator
from .models import Property, PropertyImage, AccommodationRequest, SavedProperty
from .forms import PropertyForm, PropertyImageForm, PropertySearchForm, AccommodationRequestForm
from accounts.models import Review

def home(request):
    """Homepage with recent properties and testimonials"""
    recent_properties = Property.objects.filter(is_active=True).select_related('landlord').order_by('-created_at')[:18]
    
    # Get featured reviews first, then high-rated recent reviews
    testimonials = Review.objects.select_related('student', 'landlord').filter(
        Q(is_featured=True) | Q(rating__gte=4)
    ).order_by('-is_featured', '-created_at')[:6]
    
    context = {
        'recent_properties': recent_properties,
        'testimonials': testimonials,
    }
    return render(request, 'home.html', context)


def property_list(request):
    """List all active properties with search and filters"""
    properties = Property.objects.none()  # Start with empty queryset
    has_search_criteria = False
    
    # Check if any search parameters are provided
    if request.GET:
        # Check for any non-empty search parameters
        search_params = ['search', 'city', 'campus', 'property_type', 'property_type_filter', 'min_price', 'max_price', 
                        'bedrooms', 'bedrooms_min', 'bedrooms_max', 'bathrooms_min', 'bathrooms_max',
                        'academic_year', 'furnishing', 'bills_included', 'wifi', 'parking', 'garden', 
                        'disabled_access', 'pets_allowed', 'room_type', 'location', 'distance']
        has_search_criteria = any(request.GET.get(param) for param in search_params)
    
    # Only fetch properties if search criteria are provided
    if has_search_criteria:
        properties = Property.objects.filter(is_active=True).select_related('landlord')
        
        # Handle property type filter from radio buttons
        property_type_filter = request.GET.get('property_type_filter')
        if property_type_filter:
            if property_type_filter == 'whole':
                properties = properties.filter(property_type='whole')
            elif property_type_filter == 'room':
                properties = properties.filter(property_type='room')
        
        # Search query
        search = request.GET.get('search')
        if search:
            properties = properties.filter(
                Q(title__icontains=search) | 
                Q(description__icontains=search) |
                Q(city__icontains=search) |
                Q(address__icontains=search)
            )
        
        # City filter
        city = request.GET.get('city')
        if city:
            properties = properties.filter(city__icontains=city)
        
        # Campus filter
        campus = request.GET.get('campus')
        if campus:
            properties = properties.filter(campus__icontains=campus)
        
        # Price range
        min_price = request.GET.get('min_price')
        if min_price:
            try:
                properties = properties.filter(rent_per_month__gte=float(min_price))
            except ValueError:
                pass
        
        max_price = request.GET.get('max_price')
        if max_price:
            try:
                properties = properties.filter(rent_per_month__lte=float(max_price))
            except ValueError:
                pass
        
        # Bedrooms range
        bedrooms_min = request.GET.get('bedrooms_min')
        if bedrooms_min:
            try:
                properties = properties.filter(bedrooms__gte=int(bedrooms_min))
            except ValueError:
                pass
        
        bedrooms_max = request.GET.get('bedrooms_max')
        if bedrooms_max:
            try:
                properties = properties.filter(bedrooms__lte=int(bedrooms_max))
            except ValueError:
                pass
        
        # Bathrooms range
        bathrooms_min = request.GET.get('bathrooms_min')
        if bathrooms_min:
            try:
                properties = properties.filter(bathrooms__gte=int(bathrooms_min))
            except ValueError:
                pass
        
        bathrooms_max = request.GET.get('bathrooms_max')
        if bathrooms_max:
            try:
                properties = properties.filter(bathrooms__lte=int(bathrooms_max))
            except ValueError:
                pass
        
        # Academic year
        academic_year = request.GET.get('academic_year')
        if academic_year:
            properties = properties.filter(academic_year=academic_year)
        
        # Furnishing (can be multiple)
        furnishing_values = request.GET.getlist('furnishing')
        if furnishing_values:
            properties = properties.filter(furnishing__in=furnishing_values)
        
        # Property Type (can be multiple from sidebar checkboxes)
        property_type_values = request.GET.getlist('property_type')
        if property_type_values:
            properties = properties.filter(property_type__in=property_type_values)
        
        # Room Type (can be multiple)
        room_type_values = request.GET.getlist('room_type')
        if room_type_values:
            properties = properties.filter(room_type__in=room_type_values)
        
        # Location filter
        location = request.GET.get('location')
        if location:
            properties = properties.filter(
                Q(address__icontains=location) | 
                Q(city__icontains=location) |
                Q(postcode__icontains=location)
            )
        
        # Boolean filters
        if request.GET.get('bills_included') == 'yes':
            properties = properties.filter(bills_included=True)
        elif request.GET.get('bills_included') == 'no':
            properties = properties.filter(bills_included=False)
        
        if request.GET.get('wifi'):
            properties = properties.filter(wifi=True)
        
        if request.GET.get('parking'):
            properties = properties.filter(parking=True)
        
        if request.GET.get('garden'):
            properties = properties.filter(garden=True)
        
        if request.GET.get('disabled_access'):
            properties = properties.filter(disabled_access=True)
        
        if request.GET.get('pets_allowed') == 'yes':
            properties = properties.filter(pets_allowed=True)
        elif request.GET.get('pets_allowed') == 'no':
            properties = properties.filter(pets_allowed=False)
    
    # Pagination
    paginator = Paginator(properties, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'properties': page_obj,
        'total_count': properties.count(),
        'has_search_criteria': has_search_criteria,
        'request': request,  # Pass request to template for filter persistence
    }
    return render(request, 'properties/property_list.html', context)


def property_detail(request, property_id):
    """View property details"""
    # Allow landlords to view their own properties even if not active
    if request.user.is_authenticated and request.user.user_type == 'landlord':
        property = get_object_or_404(Property, id=property_id)
        # Check if user is the landlord of this property
        if property.landlord != request.user:
            # If not the owner, only show active properties
            property = get_object_or_404(Property, id=property_id, is_active=True)
    else:
        property = get_object_or_404(Property, id=property_id, is_active=True)
    
    property.increment_views()
    
    images = property.images.all()
    is_saved = False
    
    if request.user.is_authenticated and request.user.user_type == 'student':
        is_saved = SavedProperty.objects.filter(student=request.user, property=property).exists()
    
    # Check if property has an active contract
    from contracts.models import Contract
    has_active_contract = Contract.objects.filter(
        property=property,
        status__in=['active', 'pending_signatures']
    ).exists()
    
    context = {
        'property': property,
        'images': images,
        'is_saved': is_saved,
        'has_active_contract': has_active_contract,
    }
    return render(request, 'properties/property_detail.html', context)


@login_required
def add_property(request):
    """Landlords can add new properties"""
    if request.user.user_type != 'landlord':
        messages.error(request, 'Only landlords can add properties.')
        return redirect('home')
    
    if request.method == 'POST':
        form = PropertyForm(request.POST)
        if form.is_valid():
            property = form.save(commit=False)
            property.landlord = request.user
            property.current_bid = property.starting_bid
            property.is_active = True  # Ensure property is active
            property.save()
            messages.success(request, 'Property added successfully!')
            return redirect('add_property_images', property_id=property.id)
    else:
        form = PropertyForm()
    
    return render(request, 'properties/add_property.html', {'form': form})


@login_required
def add_property_images(request, property_id):
    """Add images to a property"""
    property = get_object_or_404(Property, id=property_id, landlord=request.user)
    
    if request.method == 'POST':
        form = PropertyImageForm(request.POST, request.FILES)
        if form.is_valid():
            image = form.save(commit=False)
            image.property = property
            image.save()
            messages.success(request, 'Image added successfully!')
            return redirect('add_property_images', property_id=property.id)
    else:
        form = PropertyImageForm()
    
    images = property.images.all()
    context = {
        'form': form,
        'property': property,
        'images': images,
    }
    return render(request, 'properties/add_property_images.html', context)


@login_required
def edit_property(request, property_id):
    """Edit property details"""
    property = get_object_or_404(Property, id=property_id, landlord=request.user)
    
    if request.method == 'POST':
        form = PropertyForm(request.POST, instance=property)
        if form.is_valid():
            form.save()
            
            # Update image captions
            for image in property.images.all():
                caption_key = f'caption_{image.id}'
                if caption_key in request.POST:
                    caption = request.POST.get(caption_key, '').strip()
                    image.caption = caption
                    image.save()
            
            messages.success(request, 'Property updated successfully!')
            return redirect('property_detail', property_id=property.id)
    else:
        form = PropertyForm(instance=property)
    
    return render(request, 'properties/edit_property.html', {'form': form, 'property': property})


@login_required
def delete_property(request, property_id):
    """Delete a property"""
    property = get_object_or_404(Property, id=property_id, landlord=request.user)
    
    if request.method == 'POST':
        try:
            property.delete()
            messages.success(request, 'Property deleted successfully!')
            return redirect('landlord_dashboard')
        except models.ProtectedError:
            messages.error(request, 'Cannot delete this property because it has active contracts. Contracts must be completed or terminated before the property can be deleted.')
            return redirect('property_detail', property_id=property.id)
    
    # If accessed via GET, redirect to property detail
    messages.warning(request, 'Please use the delete button to delete the property.')
    return redirect('property_detail', property_id=property.id)


@login_required
def delete_property_image(request, image_id):
    """Delete a property image"""
    image = get_object_or_404(PropertyImage, id=image_id)
    property = image.property
    
    # Check if user is the landlord
    if property.landlord != request.user:
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    image.delete()
    messages.success(request, 'Image deleted successfully!')
    return redirect('edit_property', property_id=property.id)


@login_required
def save_property(request, property_id):
    """Save a property for later"""
    if request.user.user_type != 'student':
        messages.error(request, 'Only students can save properties.')
        return redirect('property_detail', property_id=property_id)
    
    property = get_object_or_404(Property, id=property_id)
    saved, created = SavedProperty.objects.get_or_create(student=request.user, property=property)
    
    if created:
        messages.success(request, 'Property saved successfully!')
    else:
        messages.info(request, 'Property already saved.')
    
    return redirect('property_detail', property_id=property_id)


@login_required
def unsave_property(request, property_id):
    """Remove a saved property"""
    if request.user.user_type != 'student':
        return redirect('property_detail', property_id=property_id)
    
    property = get_object_or_404(Property, id=property_id)
    SavedProperty.objects.filter(student=request.user, property=property).delete()
    messages.success(request, 'Property removed from saved list.')
    
    return redirect('property_detail', property_id=property_id)


@login_required
def saved_properties(request):
    """View all saved properties"""
    if request.user.user_type != 'student':
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    saved = SavedProperty.objects.filter(student=request.user).select_related('property')
    
    context = {
        'saved_properties': saved,
    }
    return render(request, 'properties/saved_properties.html', context)


def add_accommodation_request(request):
    """Users can post accommodation requirements"""
    # Allow viewing the form without login, but require login to submit
    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.warning(request, 'Please sign in to post your accommodation ad.')
            return redirect('login')
        
        # Allow both students and landlords to post accommodation ads
        form = AccommodationRequestForm(request.POST)
        if form.is_valid():
            req = form.save(commit=False)
            req.student = request.user
            req.save()
            messages.success(request, 'Accommodation request posted successfully!')
            return redirect('accommodation_requests')
    else:
        form = AccommodationRequestForm()
    
    return render(request, 'properties/post_accommodation_ad.html', {'form': form})


def accommodation_requests(request):
    """View all accommodation requests"""
    requests = AccommodationRequest.objects.filter(is_active=True).select_related('student')
    
    # Pagination
    paginator = Paginator(requests, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'requests': page_obj,
    }
    return render(request, 'properties/accommodation_requests.html', context)


def accommodation_request_detail(request, request_id):
    """View accommodation request details"""
    acc_request = get_object_or_404(AccommodationRequest, id=request_id, is_active=True)
    
    context = {
        'request': acc_request,
    }
    return render(request, 'properties/accommodation_request_detail.html', context)


@login_required
def delete_accommodation_request(request, request_id):
    """Delete accommodation request"""
    acc_request = get_object_or_404(AccommodationRequest, id=request_id)
    
    # Check if user owns this request
    if request.user != acc_request.student:
        messages.error(request, 'You do not have permission to delete this ad.')
        return redirect('accommodation_requests')
    
    if request.method == 'POST':
        acc_request.delete()
        messages.success(request, 'Your accommodation seeking ad has been deleted successfully.')
        return redirect('accommodation_requests')
    
    context = {
        'request': acc_request,
    }
    return render(request, 'properties/delete_accommodation_request.html', context)


def contact(request):
    """Contact form view"""
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        
        # Validate required fields
        if not all([name, email, subject, message]):
            messages.error(request, 'All fields are required.')
            return render(request, 'contact.html')
        
        # Save to database
        from .models import ContactMessage
        ContactMessage.objects.create(
            name=name,
            email=email,
            subject=subject,
            message=message
        )
        
        messages.success(request, f'Thank you {name}! Your message has been received. We will get back to you at {email} soon.')
        
        return redirect('contact')
    
    return render(request, 'contact.html')
