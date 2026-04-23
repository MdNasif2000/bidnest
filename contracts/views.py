from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from bidding.models import Bid
from .models import Contract, ContractDocument, ContractRenewal
from notifications.views import create_notification

@login_required
def my_contracts(request):
    """View all contracts"""
    if request.user.user_type == 'student':
        contracts = Contract.objects.filter(student=request.user)
    elif request.user.user_type == 'landlord':
        contracts = Contract.objects.filter(landlord=request.user)
    else:
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    context = {
        'contracts': contracts,
    }
    return render(request, 'contracts/my_contracts.html', context)


@login_required
def contract_detail(request, contract_id):
    """View contract details"""
    contract = get_object_or_404(Contract, id=contract_id)
    
    # Check permissions
    if request.user != contract.student and request.user != contract.landlord:
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    additional_docs = contract.additional_documents.all()
    
    context = {
        'contract': contract,
        'additional_docs': additional_docs,
    }
    return render(request, 'contracts/contract_detail.html', context)


@login_required
def generate_contract(request, bid_id):
    """Generate contract from accepted bid"""
    bid = get_object_or_404(Bid, id=bid_id, status='accepted')
    
    # Check permissions
    if request.user != bid.property.landlord:
        messages.error(request, 'Only landlord can generate contract.')
        return redirect('home')
    
    # Check if contract already exists
    existing_contract = Contract.objects.filter(bid=bid).first()
    if existing_contract:
        messages.info(request, 'Contract already exists for this bid.')
        return redirect('contract_detail', contract_id=existing_contract.id)
    
    if request.method == 'POST':
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        terms = request.POST.get('terms_and_conditions')
        special_conditions = request.POST.get('special_conditions', '')
        
        # Validate dates
        from datetime import datetime
        try:
            start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
            
            if end_date_obj <= start_date_obj:
                messages.error(request, 'End date must be after start date.')
                context = {
                    'bid': bid,
                    'default_terms': """
    ASSURED SHORTHOLD TENANCY AGREEMENT
    
    This agreement is made between the Landlord and the Tenant for the property described below.
    
    1. THE PROPERTY
    The property is located at the address specified in this agreement.
    
    2. TERM
    The tenancy shall begin on the Start Date and end on the End Date.
    
    3. RENT
    The Tenant agrees to pay the monthly rent as specified.
    
    4. DEPOSIT
    The Tenant has paid a deposit which will be held in accordance with the Tenancy Deposit Scheme.
    
    5. TENANT'S OBLIGATIONS
    - Pay rent on time
    - Keep the property in good condition
    - Not cause nuisance to neighbors
    - Allow landlord access for inspections with proper notice
    
    6. LANDLORD'S OBLIGATIONS
    - Maintain the property structure
    - Ensure property meets safety standards
    - Protect the deposit in an approved scheme
    - Provide required certificates (Gas Safety, EPC, etc.)
    """,
                }
                return render(request, 'contracts/generate_contract.html', context)
        except ValueError:
            messages.error(request, 'Invalid date format.')
            context = {
                'bid': bid,
                'default_terms': """
    ASSURED SHORTHOLD TENANCY AGREEMENT
    
    This agreement is made between the Landlord and the Tenant for the property described below.
    
    1. THE PROPERTY
    The property is located at the address specified in this agreement.
    
    2. TERM
    The tenancy shall begin on the Start Date and end on the End Date.
    
    3. RENT
    The Tenant agrees to pay the monthly rent as specified.
    
    4. DEPOSIT
    The Tenant has paid a deposit which will be held in accordance with the Tenancy Deposit Scheme.
    
    5. TENANT'S OBLIGATIONS
    - Pay rent on time
    - Keep the property in good condition
    - Not cause nuisance to neighbors
    - Allow landlord access for inspections with proper notice
    
    6. LANDLORD'S OBLIGATIONS
    - Maintain the property structure
    - Ensure property meets safety standards
    - Protect the deposit in an approved scheme
    - Provide required certificates (Gas Safety, EPC, etc.)
    """,
            }
            return render(request, 'contracts/generate_contract.html', context)
        
        contract = Contract.objects.create(
            student=bid.student,
            landlord=bid.property.landlord,
            property=bid.property,
            bid=bid,
            monthly_rent=bid.amount,
            deposit=bid.property.deposit,
            start_date=start_date,
            end_date=end_date,
            terms_and_conditions=terms,
            special_conditions=special_conditions,
            status='pending_signatures'
        )
        
        # Create notification for student
        create_notification(
            user=bid.student,
            notification_type='contract_generated',
            title='Contract Ready for Signature',
            message=f'A tenancy agreement has been generated for {bid.property.title}. Please review and sign the contract.',
            link=f'/contracts/{contract.id}/'
        )
        
        messages.success(request, 'Contract generated successfully!')
        return redirect('contract_detail', contract_id=contract.id)
    
    # Default terms
    default_terms = """
    ASSURED SHORTHOLD TENANCY AGREEMENT
    
    This agreement is made between the Landlord and the Tenant for the property described below.
    
    1. THE PROPERTY
    The property is located at the address specified in this agreement.
    
    2. TERM
    The tenancy shall begin on the Start Date and end on the End Date.
    
    3. RENT
    The Tenant agrees to pay the monthly rent as specified.
    
    4. DEPOSIT
    The Tenant has paid a deposit which will be held in accordance with the Tenancy Deposit Scheme.
    
    5. TENANT'S OBLIGATIONS
    - Pay rent on time
    - Keep the property in good condition
    - Not cause nuisance to neighbors
    - Allow landlord access for inspections with proper notice
    
    6. LANDLORD'S OBLIGATIONS
    - Maintain the property structure
    - Ensure property meets safety standards
    - Protect the deposit in an approved scheme
    - Provide required certificates (Gas Safety, EPC, etc.)
    """
    
    context = {
        'bid': bid,
        'default_terms': default_terms,
    }
    return render(request, 'contracts/generate_contract.html', context)


@login_required
def sign_contract(request, contract_id):
    """Sign a contract"""
    contract = get_object_or_404(Contract, id=contract_id)
    
    # Check permissions
    if request.user != contract.student and request.user != contract.landlord:
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    # Check if already signed
    if request.user == contract.student and contract.student_signed:
        messages.info(request, 'You have already signed this contract.')
        return redirect('contract_detail', contract_id=contract.id)
    
    if request.user == contract.landlord and contract.landlord_signed:
        messages.info(request, 'You have already signed this contract.')
        return redirect('contract_detail', contract_id=contract.id)
    
    if request.method == 'POST':
        if request.user == contract.student:
            contract.student_signed = True
            contract.student_signed_at = timezone.now()
            
            # Notify landlord
            create_notification(
                user=contract.landlord,
                notification_type='contract_signed',
                title='Student Signed Contract',
                message=f'{contract.student.get_full_name() or contract.student.username} has signed the contract for {contract.property.title}.',
                link=f'/contracts/{contract.id}/'
            )
            
        elif request.user == contract.landlord:
            contract.landlord_signed = True
            contract.landlord_signed_at = timezone.now()
            
            # Notify student
            create_notification(
                user=contract.student,
                notification_type='contract_signed',
                title='Landlord Signed Contract',
                message=f'The landlord has signed the contract for {contract.property.title}.',
                link=f'/contracts/{contract.id}/'
            )
        
        contract.save()
        
        # If both signed, activate contract
        if contract.is_fully_signed():
            contract.status = 'active'
            contract.save()
            
            # Notify both parties
            create_notification(
                user=contract.student,
                notification_type='contract_signed',
                title='Contract is Now Active!',
                message=f'The tenancy agreement for {contract.property.title} is now active. Your tenancy begins on {contract.start_date.strftime("%d %b %Y")}.',
                link=f'/contracts/{contract.id}/'
            )
            create_notification(
                user=contract.landlord,
                notification_type='contract_signed',
                title='Contract is Now Active!',
                message=f'The tenancy agreement for {contract.property.title} is now active. Tenancy begins on {contract.start_date.strftime("%d %b %Y")}.',
                link=f'/contracts/{contract.id}/'
            )
            
            messages.success(request, 'Contract is now active!')
        else:
            messages.success(request, 'Contract signed successfully!')
        
        return redirect('contract_detail', contract_id=contract.id)
    
    context = {
        'contract': contract,
    }
    return render(request, 'contracts/sign_contract.html', context)


@login_required
def request_renewal(request, contract_id):
    """Request contract renewal"""
    contract = get_object_or_404(Contract, id=contract_id)
    
    # Check permissions
    if request.user != contract.student and request.user != contract.landlord:
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    if contract.status != 'active':
        messages.error(request, 'Only active contracts can be renewed.')
        return redirect('contract_detail', contract_id=contract.id)
    
    if request.method == 'POST':
        new_start_date = request.POST.get('new_start_date')
        new_end_date = request.POST.get('new_end_date')
        new_monthly_rent = request.POST.get('new_monthly_rent', contract.monthly_rent)
        
        ContractRenewal.objects.create(
            original_contract=contract,
            requested_by=request.user,
            new_start_date=new_start_date,
            new_end_date=new_end_date,
            new_monthly_rent=new_monthly_rent
        )
        
        messages.success(request, 'Renewal request submitted!')
        return redirect('contract_detail', contract_id=contract.id)
    
    context = {
        'contract': contract,
    }
    return render(request, 'contracts/request_renewal.html', context)


@login_required
def upload_document(request, contract_id):
    """Upload additional documents to contract"""
    contract = get_object_or_404(Contract, id=contract_id)
    
    # Check permissions
    if request.user != contract.student and request.user != contract.landlord:
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    if request.method == 'POST':
        document_type = request.POST.get('document_type')
        document_file = request.FILES.get('document_file')
        description = request.POST.get('description', '')
        
        ContractDocument.objects.create(
            contract=contract,
            document_type=document_type,
            document_file=document_file,
            uploaded_by=request.user,
            description=description
        )
        
        messages.success(request, 'Document uploaded successfully!')
        return redirect('contract_detail', contract_id=contract.id)
    
    context = {
        'contract': contract,
    }
    return render(request, 'contracts/upload_document.html', context)



@login_required
def request_termination(request, contract_id):
    """Request early contract termination"""
    contract = get_object_or_404(Contract, id=contract_id)
    
    # Check permissions
    if request.user != contract.student and request.user != contract.landlord:
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    # Check if contract is active
    if contract.status != 'active':
        messages.error(request, 'Only active contracts can be terminated.')
        return redirect('contract_detail', contract_id=contract.id)
    
    # Check if there's already a pending termination request
    from .models import ContractTermination
    pending_request = ContractTermination.objects.filter(
        contract=contract,
        status='requested'
    ).first()
    
    if pending_request:
        messages.info(request, 'There is already a pending termination request for this contract.')
        return redirect('contract_detail', contract_id=contract.id)
    
    if request.method == 'POST':
        reason = request.POST.get('reason')
        reason_details = request.POST.get('reason_details')
        proposed_date = request.POST.get('proposed_termination_date')
        notice_period = request.POST.get('notice_period_days', 30)
        
        # Validate proposed date
        from datetime import datetime
        try:
            proposed_date_obj = datetime.strptime(proposed_date, '%Y-%m-%d').date()
            today = timezone.now().date()
            
            if proposed_date_obj < contract.start_date:
                messages.error(request, 'Termination date cannot be before the contract start date.')
                return render(request, 'contracts/request_termination.html', {'contract': contract})
            
            if proposed_date_obj < today:
                messages.error(request, 'Termination date cannot be in the past.')
                return render(request, 'contracts/request_termination.html', {'contract': contract})
            
            if proposed_date_obj > contract.end_date:
                messages.error(request, 'Termination date cannot be after contract end date.')
                return render(request, 'contracts/request_termination.html', {'contract': contract})
        except ValueError:
            messages.error(request, 'Invalid date format.')
            return render(request, 'contracts/request_termination.html', {'contract': contract})
        
        # Create termination request
        termination = ContractTermination.objects.create(
            contract=contract,
            requested_by=request.user,
            reason=reason,
            reason_details=reason_details,
            proposed_termination_date=proposed_date,
            notice_period_days=notice_period
        )
        
        # Notify the other party
        other_party = termination.get_other_party()
        create_notification(
            user=other_party,
            notification_type='termination_request',
            title='Contract Termination Request',
            message=f'{request.user.get_full_name() or request.user.username} has requested to terminate the contract for {contract.property.title}.',
            link=f'/contracts/{contract.id}/termination/{termination.id}/'
        )
        
        messages.success(request, 'Termination request submitted. Waiting for approval from the other party.')
        return redirect('contract_detail', contract_id=contract.id)
    
    context = {
        'contract': contract,
    }
    return render(request, 'contracts/request_termination.html', context)


@login_required
def termination_detail(request, contract_id, termination_id):
    """View and respond to termination request"""
    from .models import ContractTermination
    contract = get_object_or_404(Contract, id=contract_id)
    termination = get_object_or_404(ContractTermination, id=termination_id, contract=contract)
    
    # Check permissions
    if request.user != contract.student and request.user != contract.landlord:
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    # Handle response
    if request.method == 'POST':
        action = request.POST.get('action')
        response_message = request.POST.get('response_message', '')
        
        # Only the other party can respond
        if request.user == termination.requested_by:
            messages.error(request, 'You cannot respond to your own termination request.')
            return redirect('termination_detail', contract_id=contract.id, termination_id=termination.id)
        
        if termination.status != 'requested':
            messages.error(request, 'This termination request has already been processed.')
            return redirect('contract_detail', contract_id=contract.id)
        
        if action == 'approve':
            termination.status = 'approved'
            termination.responded_by = request.user
            termination.responded_at = timezone.now()
            termination.response_message = response_message
            termination.actual_termination_date = termination.proposed_termination_date
            termination.save()
            
            # Update contract status
            contract.status = 'terminated'
            contract.save()
            
            # Notify requester
            create_notification(
                user=termination.requested_by,
                notification_type='termination_approved',
                title='Termination Request Approved',
                message=f'Your termination request for {contract.property.title} has been approved. Contract will end on {termination.actual_termination_date.strftime("%d %b %Y")}.',
                link=f'/contracts/{contract.id}/'
            )
            
            messages.success(request, 'Termination request approved. Contract will be terminated on the proposed date.')
            
        elif action == 'reject':
            termination.status = 'rejected'
            termination.responded_by = request.user
            termination.responded_at = timezone.now()
            termination.response_message = response_message
            termination.save()
            
            # Notify requester
            create_notification(
                user=termination.requested_by,
                notification_type='termination_rejected',
                title='Termination Request Rejected',
                message=f'Your termination request for {contract.property.title} has been rejected.',
                link=f'/contracts/{contract.id}/'
            )
            
            messages.info(request, 'Termination request rejected.')
        
        return redirect('contract_detail', contract_id=contract.id)
    
    context = {
        'contract': contract,
        'termination': termination,
    }
    return render(request, 'contracts/termination_detail.html', context)
