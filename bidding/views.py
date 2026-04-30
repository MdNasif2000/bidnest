from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from properties.models import Property
from .models import Bid, BidHistory
from .forms import BidForm, CounterOfferForm
from notifications.views import create_notification

@login_required
def place_bid(request, property_id):
    """Students place bids on properties"""
    if request.user.user_type != 'student':
        messages.error(request, 'Only students can place bids.')
        return redirect('property_detail', property_id=property_id)
    
    property = get_object_or_404(Property, id=property_id, is_active=True)
    
    # Check if property already has an active contract
    from contracts.models import Contract
    has_active_contract = Contract.objects.filter(
        property=property,
        status__in=['active', 'pending_signatures']
    ).exists()
    
    if has_active_contract:
        messages.error(request, 'This property already has an active contract and is no longer available for bidding.')
        return redirect('property_detail', property_id=property_id)
    
    # Check if student already has a pending bid
    existing_bid = Bid.objects.filter(
        property=property,
        student=request.user,
        status__in=['pending', 'countered']
    ).first()
    
    if existing_bid:
        messages.warning(request, 'You already have an active bid on this property.')
        return redirect('property_detail', property_id=property_id)
    
    if request.method == 'POST':
        form = BidForm(request.POST)
        if form.is_valid():
            bid = form.save(commit=False)
            
            # Validate bid amount is not less than starting bid
            if bid.amount < property.starting_bid:
                messages.error(request, f'Your bid must be at least £{property.starting_bid} (the starting bid amount).')
                return render(request, 'bidding/place_bid.html', {'form': form, 'property': property})
            
            bid.property = property
            bid.student = request.user
            bid.save()
            
            # Update property current bid if this is higher
            if bid.amount > property.current_bid:
                property.current_bid = bid.amount
                property.save()
            
            # Create bid history
            BidHistory.objects.create(
                bid=bid,
                action='created',
                amount=bid.amount,
                note=bid.message,
                created_by=request.user
            )
            
            # Create notification for landlord
            create_notification(
                user=property.landlord,
                notification_type='bid_received',
                title='New Bid Received!',
                message=f'{request.user.get_full_name() or request.user.username} placed a bid of £{bid.amount} on {property.title}',
                link=f'/bidding/received/'
            )
            
            messages.success(request, 'Your bid has been placed successfully!')
            return redirect('my_bids')
    else:
        form = BidForm(initial={'amount': property.starting_bid})
    
    context = {
        'form': form,
        'property': property,
    }
    return render(request, 'bidding/place_bid.html', context)


@login_required
def my_bids(request):
    """View all bids placed by student"""
    if request.user.user_type != 'student':
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    bids = Bid.objects.filter(student=request.user).select_related('property')
    
    context = {
        'bids': bids,
    }
    return render(request, 'bidding/my_bids.html', context)


@login_required
def received_bids(request):
    """View all bids received by landlord"""
    if request.user.user_type != 'landlord':
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    bids = Bid.objects.filter(
        property__landlord=request.user
    ).select_related('property', 'student').order_by('-created_at')
    
    # Filter by status
    status_filter = request.GET.get('status')
    if status_filter:
        bids = bids.filter(status=status_filter)
    
    context = {
        'bids': bids,
        'status_filter': status_filter,
    }
    return render(request, 'bidding/received_bids.html', context)


@login_required
def bid_detail(request, bid_id):
    """View bid details"""
    bid = get_object_or_404(Bid, id=bid_id)
    
    # Check permissions
    if request.user != bid.student and request.user != bid.property.landlord:
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    history = bid.history.all()
    
    context = {
        'bid': bid,
        'history': history,
    }
    return render(request, 'bidding/bid_detail.html', context)


@login_required
def accept_bid(request, bid_id):
    """Landlord accepts a bid"""
    bid = get_object_or_404(Bid, id=bid_id)
    
    if request.user != bid.property.landlord:
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    if bid.status != 'pending' and bid.status != 'countered':
        messages.error(request, 'This bid cannot be accepted.')
        return redirect('received_bids')
    
    if request.method == 'POST':
        bid.accept()
        
        # Create bid history
        BidHistory.objects.create(
            bid=bid,
            action='accepted',
            amount=bid.amount,
            note='Bid accepted by landlord',
            created_by=request.user
        )
        
        # Create notification for student
        create_notification(
            user=bid.student,
            notification_type='bid_accepted',
            title='Your Bid Was Accepted!',
            message=f'Congratulations! Your bid of £{bid.amount} on {bid.property.title} has been accepted. A contract will be generated soon.',
            link=f'/bidding/my-bids/'
        )
        
        messages.success(request, 'Bid accepted successfully!')
        return redirect('received_bids')
    
    return render(request, 'bidding/accept_bid.html', {'bid': bid})


@login_required
def reject_bid(request, bid_id):
    """Landlord rejects a bid"""
    bid = get_object_or_404(Bid, id=bid_id)
    
    if request.user != bid.property.landlord:
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    if request.method == 'POST':
        bid.reject()
        
        # Create bid history
        BidHistory.objects.create(
            bid=bid,
            action='rejected',
            amount=bid.amount,
            note='Bid rejected by landlord',
            created_by=request.user
        )
        
        # Create notification for student
        create_notification(
            user=bid.student,
            notification_type='bid_rejected',
            title='Bid Not Accepted',
            message=f'Your bid of £{bid.amount} on {bid.property.title} was not accepted. You can place a new bid or browse other properties.',
            link=f'/bidding/my-bids/'
        )
        
        messages.success(request, 'Bid rejected.')
        return redirect('received_bids')
    
    return render(request, 'bidding/reject_bid.html', {'bid': bid})


@login_required
def counter_offer(request, bid_id):
    """Landlord makes a counter offer"""
    bid = get_object_or_404(Bid, id=bid_id)
    
    if request.user != bid.property.landlord:
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    if bid.status not in ['pending', 'countered']:
        messages.error(request, 'Cannot counter this bid.')
        return redirect('received_bids')
    
    if request.method == 'POST':
        form = CounterOfferForm(request.POST)
        if form.is_valid():
            counter_amount = form.cleaned_data['counter_amount']
            counter_message = form.cleaned_data['counter_message']
            
            bid.counter_offer(counter_amount, counter_message)
            
            # Create bid history
            BidHistory.objects.create(
                bid=bid,
                action='countered',
                amount=counter_amount,
                note=counter_message,
                created_by=request.user
            )
            
            # Create notification for student
            create_notification(
                user=bid.student,
                notification_type='bid_countered',
                title='Counter Offer Received',
                message=f'The landlord has made a counter offer of £{counter_amount} on {bid.property.title}. Review and respond to the offer.',
                link=f'/bidding/my-bids/'
            )
            
            messages.success(request, 'Counter offer sent successfully!')
            return redirect('received_bids')
    else:
        form = CounterOfferForm(initial={'counter_amount': bid.amount})
    
    context = {
        'form': form,
        'bid': bid,
    }
    return render(request, 'bidding/counter_offer.html', context)


@login_required
def withdraw_bid(request, bid_id):
    """Student withdraws their bid"""
    bid = get_object_or_404(Bid, id=bid_id, student=request.user)
    
    if bid.status not in ['pending', 'countered']:
        messages.error(request, 'This bid cannot be withdrawn.')
        return redirect('my_bids')
    
    if request.method == 'POST':
        bid.withdraw()
        
        # Create bid history
        BidHistory.objects.create(
            bid=bid,
            action='withdrawn',
            amount=bid.amount,
            note='Bid withdrawn by student',
            created_by=request.user
        )
        
        messages.success(request, 'Bid withdrawn successfully.')
        return redirect('my_bids')
    
    return render(request, 'bidding/withdraw_bid.html', {'bid': bid})


@login_required
def accept_counter_offer(request, bid_id):
    """Student accepts landlord's counter offer"""
    bid = get_object_or_404(Bid, id=bid_id, student=request.user)
    
    if bid.status != 'countered':
        messages.error(request, 'No counter offer to accept.')
        return redirect('my_bids')
    
    if request.method == 'POST':
        # Store counter amount before updating
        accepted_amount = bid.counter_amount
        
        # Update bid amount to counter amount
        bid.amount = accepted_amount
        bid.status = 'accepted'
        bid.save()
        
        # Update property current bid
        property = bid.property
        property.current_bid = accepted_amount
        property.save()
        
        # Reject all other pending bids for this property
        Bid.objects.filter(property=property, status__in=['pending', 'countered']).exclude(id=bid.id).update(status='rejected')
        
        # Create bid history
        BidHistory.objects.create(
            bid=bid,
            action='counter_accepted',
            amount=accepted_amount,
            note='Counter offer accepted by student',
            created_by=request.user
        )
        
        # Create notification for landlord
        create_notification(
            user=property.landlord,
            notification_type='bid_accepted',
            title='Counter Offer Accepted!',
            message=f'{bid.student.get_full_name() or bid.student.username} accepted your counter offer of £{accepted_amount} on {property.title}.',
            link=f'/bidding/received/'
        )
        
        messages.success(request, 'Counter offer accepted!')
        return redirect('my_bids')
    
    return render(request, 'bidding/accept_counter_offer.html', {'bid': bid})
