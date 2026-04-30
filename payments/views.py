from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from bidding.models import Bid
from .models import Payment, Refund
import stripe

stripe.api_key = settings.STRIPE_SECRET_KEY

@login_required
def payment_history(request):
    """View payment history"""
    if request.user.user_type == 'student':
        payments = Payment.objects.filter(student=request.user)
    elif request.user.user_type == 'landlord':
        payments = Payment.objects.filter(landlord=request.user)
    else:
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    context = {
        'payments': payments,
    }
    return render(request, 'payments/payment_history.html', context)


@login_required
def initiate_payment(request, bid_id):
    """Initiate payment for accepted bid"""
    bid = get_object_or_404(Bid, id=bid_id, student=request.user, status='accepted')
    
    # Check if payment already exists
    existing_payment = Payment.objects.filter(bid=bid).first()
    if existing_payment:
        messages.info(request, 'Payment already initiated for this bid.')
        return redirect('payment_detail', payment_id=existing_payment.id)
    
    if request.method == 'POST':
        payment_type = request.POST.get('payment_type', 'deposit')
        
        # Calculate amount based on payment type
        if payment_type == 'deposit':
            amount = bid.property.deposit
        elif payment_type == 'full_payment':
            amount = bid.property.deposit + bid.property.rent_per_month
        else:
            amount = bid.property.rent_per_month
        
        # Create payment record
        payment = Payment.objects.create(
            student=request.user,
            landlord=bid.property.landlord,
            property=bid.property,
            bid=bid,
            amount=amount,
            payment_type=payment_type,
            status='pending',
            description=f"{payment_type.replace('_', ' ').title()} for {bid.property.title}"
        )
        
        messages.success(request, 'Payment initiated. Please complete the payment.')
        return redirect('process_payment', payment_id=payment.id)
    
    context = {
        'bid': bid,
    }
    return render(request, 'payments/initiate_payment.html', context)


@login_required
def process_payment(request, payment_id):
    """Process payment with Stripe"""
    payment = get_object_or_404(Payment, id=payment_id, student=request.user)
    
    if payment.status not in ['pending', 'failed']:
        messages.info(request, 'This payment has already been processed.')
        return redirect('payment_detail', payment_id=payment.id)
    
    if request.method == 'POST':
        try:
            # Create Stripe PaymentIntent
            intent = stripe.PaymentIntent.create(
                amount=int(payment.amount * 100),  # Convert to pence
                currency='gbp',
                metadata={
                    'payment_id': payment.id,
                    'student_id': request.user.id,
                    'landlord_id': payment.landlord.id,
                }
            )
            
            payment.stripe_payment_intent_id = intent.id
            payment.status = 'processing'
            payment.save()
            
            # In a real implementation, you would redirect to Stripe Checkout
            # For now, we'll simulate successful payment
            payment.status = 'held_in_escrow'
            payment.save()
            
            messages.success(request, 'Payment successful! Funds are held in escrow.')
            return redirect('payment_detail', payment_id=payment.id)
            
        except stripe.error.StripeError as e:
            payment.status = 'failed'
            payment.save()
            messages.error(request, f'Payment failed: {str(e)}')
            return redirect('process_payment', payment_id=payment.id)
    
    context = {
        'payment': payment,
        'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
    }
    return render(request, 'payments/process_payment.html', context)


@login_required
def payment_detail(request, payment_id):
    """View payment details"""
    payment = get_object_or_404(Payment, id=payment_id)
    
    # Check permissions
    if request.user != payment.student and request.user != payment.landlord:
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    context = {
        'payment': payment,
    }
    return render(request, 'payments/payment_detail.html', context)


@login_required
def release_payment(request, payment_id):
    """Release payment from escrow (admin or after contract signing)"""
    payment = get_object_or_404(Payment, id=payment_id)
    
    # Only admin or system can release payments
    if not request.user.is_staff:
        messages.error(request, 'Access denied.')
        return redirect('payment_detail', payment_id=payment.id)
    
    if payment.status != 'held_in_escrow':
        messages.error(request, 'Payment is not in escrow.')
        return redirect('payment_detail', payment_id=payment.id)
    
    if request.method == 'POST':
        payment.status = 'released'
        from django.utils import timezone
        payment.released_at = timezone.now()
        payment.save()
        
        messages.success(request, 'Payment released to landlord.')
        return redirect('payment_detail', payment_id=payment.id)
    
    return render(request, 'payments/release_payment.html', {'payment': payment})


@login_required
def request_refund(request, payment_id):
    """Request a refund"""
    payment = get_object_or_404(Payment, id=payment_id, student=request.user)
    
    if payment.status not in ['held_in_escrow', 'released']:
        messages.error(request, 'Refund cannot be requested for this payment.')
        return redirect('payment_detail', payment_id=payment.id)
    
    if request.method == 'POST':
        reason = request.POST.get('reason')
        amount = request.POST.get('amount', payment.amount)
        
        Refund.objects.create(
            payment=payment,
            amount=amount,
            reason=reason,
            requested_by=request.user
        )
        
        messages.success(request, 'Refund request submitted.')
        return redirect('payment_detail', payment_id=payment.id)
    
    context = {
        'payment': payment,
    }
    return render(request, 'payments/request_refund.html', context)
