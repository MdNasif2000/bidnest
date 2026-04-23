# BidNest - Complete A-Z Guide

**Version:** 1.0  
**Last Updated:** April 2026  
**Platform:** Student Accommodation Bidding System

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [System Overview](#system-overview)
3. [Installation & Setup](#installation--setup)
4. [User Roles & Features](#user-roles--features)
5. [Core Workflows](#core-workflows)
6. [Technical Architecture](#technical-architecture)

---

## Quick Start

### Fastest Way to Get Started (3 Commands)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Setup database (creates db.sqlite3 automatically)
python manage.py migrate

# 3. Create admin user and start
python manage.py createsuperuser
python manage.py runserver
```

**Visit:** http://127.0.0.1:8000/

### Or Use Automated Script

```bash
quick_start_sqlite.bat
```

---

## System Overview

### What is BidNest?

BidNest is a comprehensive web platform for student accommodation in the UK. It enables:

- Students to search and bid on properties
- Landlords to list properties and manage bids
- Secure contract generation and digital signing
- Real-time messaging between parties
- Payment processing with escrow(To be implemented)
- Review and rating system

### Technology Stack

- **Backend:** Django 5.1.5
- **Database:** SQLite (zero configuration!)
- **Frontend:** HTML5, CSS3, JavaScript
- **Real-time:** Django Channels (WebSockets)
- **Task Queue:** Celery + Redis (optional)
- **Payment:** Stripe API (To be implemented)
- **E-Signature:** DocuSign API (To be implemented)

### Key Statistics

- 7 Django apps
- 10+ database models
- 50+ views and templates
- Complete CRUD operations
- Real-time features
- Automated notifications

---

## Installation & Setup

### Prerequisites

- Python 3.10+ (Required for Django 5.1)
- That's it! SQLite is built into Python

### Step-by-Step Setup

#### 1. Clone and Navigate

```bash
git clone <repository-url>
cd bidnest
```

#### 2. Create Virtual Environment

```bash
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac
```

#### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

#### 4. Setup Database

```bash
python manage.py migrate
```

#### 5. Create Superuser

```bash
python manage.py createsuperuser
```

#### 6. Collect Static Files

```bash
python manage.py collectstatic --noinput
```

#### 7. Run Server

```bash
python manage.py runserver
```

### Environment Configuration (Optional)

Copy `.env.example` to `.env` and configure:

- API keys (Stripe, DocuSign, Onfido)
- Email settings
- Debug mode

---

## User Roles & Features

### 1. Students

**Registration & Profile:**

- Register with email and password
- Complete profile (university, course, year)
- Upload verification documents -ID, proof of study (To be implemented)
- Manage personal information

**Property Search:**

- Browse all available properties
- Advanced search filters (location, price, type, amenities)
- Save favorite properties
- View property details and images
- Post accommodation requirements

**Bidding:**

- Place bids on properties (must be >= starting bid)
- View bid history and status
- Withdraw bids before acceptance
- Accept/reject counter-offers from landlords
- Cannot bid on properties with active contracts

**Messaging:**

- Direct chat with landlords
- Real-time message updates
- Message read status
- Delete conversations
- Unread message count in navigation

**Contracts:**

- Review generated contracts
- Digital signature
- View contract details and status
- Request early termination (requires landlord approval)
- Receive expiry notifications (30, 7, 0 days before)

**Payments:** (To be implemented)

- Secure payment processing
- Escrow system (funds held until contract activation)
- Payment history
- Refund requests

**Reviews:**

- Rate and review landlords (1-5 stars)
- Only after active or completed contract
- Edit or delete own reviews
- Receive notifications when landlord responds

### 2. Landlords

**Registration & Profile:**

- Register with business information
- Complete landlord profile
- Upload business documents
- View ratings and reviews

**Property Management:**

- Create property listings
- Upload multiple property images
- Edit property details
- Activate/deactivate listings
- Cannot delete properties with active contracts
- View property statistics

**Bid Management:**

- View all received bids
- Accept bids (generates contract automatically)
- Reject bids with optional reason
- Make counter-offers
- View complete bid history

**Messaging:**

- Direct chat with students
- Real-time message updates
- Message read status
- Delete conversations
- Unread message count in navigation

**Contracts:**

- Auto-generated from accepted bids
- Generate custom contracts
- Set tenancy dates
- Digital signature
- View all contracts and status
- Approve/reject termination requests

**Reviews:**

- View all reviews from students
- Respond to reviews
- Reviews display on profile page
- Receive notifications for new reviews

**Dashboard:**

- View all properties
- Monitor active bids
- Track contracts
- Analytics and statistics

### 3. Admins

**User Management:**

- View all users (students, landlords)
- Approve/reject registrations
- Manage user accounts
- Handle disputes

**Property Oversight:**

- View all properties
- Approve/reject listings
- Monitor property activity
- Handle reported issues

**Bid & Contract Monitoring:**

- View all bids and contracts
- Resolve disputes
- Override decisions if needed

**Payment Management:** (To be implemented)

- Monitor all transactions
- Process refunds
- View payment history
- Handle payment issues

**System Management:**

- View notifications
- Manage contact form submissions
- System analytics
- Generate reports

---

## Core Workflows

### Workflow 1: Student Finds and Bids on Property

1. **Student registers** → Completes profile → Uploads documents (To be implemented)
2. **Searches properties** → Uses filters (location, price, type)
3. **Views property details** → Checks images, amenities, landlord info
4. **Places bid** → Amount must be >= starting bid
5. **Landlord receives notification** → Reviews bid
6. **Landlord accepts/rejects/counters** → Student notified
7. **If accepted** → Contract auto-generated → Both parties sign
8. **Payment processed** → Held in escrow → Released on contract activation

### Workflow 2: Bidding Negotiation

1. **Student places bid** → e.g., £500/month
2. **Landlord makes counter-offer** → e.g., £550/month
3. **Student receives notification** → Reviews counter-offer
4. **Student accepts counter** → Contract generated at £550/month
5. **OR Student rejects** → Can place new bid or withdraw

### Workflow 3: Contract Lifecycle

1. **Contract generated** → Status: "draft"
2. **Both parties sign** → Status: "pending_signatures"
3. **Payment made** → Status: "active" (To be implemented)
4. **During tenancy** → Either party can request termination
5. **Termination request** → Other party must approve
6. **If approved** → Status: "terminated"
7. **Contract expires** → Status: "expired"
8. **Notifications sent** → 30, 7, 0 days before expiry

### Workflow 4: Messaging

1. **Student clicks "Message Landlord"** on property
2. **Conversation created** → Real-time chat opens
3. **Messages sent** → WebSocket updates in real-time
4. **Read status tracked** → Unread count in navigation
5. **Either party can delete** → Conversation removed

### Workflow 5: Review System

1. **Contract must be active or completed** → Eligibility check
2. **Student writes review** → Rates 1-5 stars + comment
3. **Landlord receives notification** → Views review on profile
4. **Landlord responds** → Student notified
5. **Review displays** → On landlord profile page
6. **Student can edit/delete** → Within reasonable time

### Workflow 6: Contract Termination

1. **Either party requests termination** → Provides reason and date
2. **Termination date must be** → Between contract start and end
3. **Other party receives notification** → Reviews request
4. **Approve** → Contract status changes to "terminated"
5. **Reject** → Contract remains active
6. **Notice period** → Configurable (default 30 days)

---

## Technical Architecture

### Project Structure

```
bidnest/
├── accounts/           # User management, profiles, reviews
├── properties/         # Property listings, search, accommodation requests
├── bidding/            # Bidding system, negotiations, bid history
├── messaging/          # Real-time chat, conversations
├── payments/           # Payment processing, escrow, refunds
├── contracts/          # Contract generation, signing, termination
├── notifications/      # In-app notifications
├── api/                # REST API endpoints
├── templates/          # HTML templates
├── static/             # CSS, JavaScript, images
├── media/              # User uploads
└── bidnest/            # Project settings
```

### Django Apps Overview

#### 1. accounts

- Custom User model with role-based access
- StudentProfile and LandlordProfile models
- Review system for landlords
- Registration, login, profile management

#### 2. properties

- Property model with full details
- PropertyImage for multiple images
- AccommodationRequest for student posts
- SavedProperty for favorites
- Advanced search and filtering
- ContactMessage for contact form

#### 3. bidding

- Bid model for student bids
- BidHistory for complete negotiation trail
- Counter-offer system
- Bid validation (minimum amount, no bidding on contracted properties)

#### 4. messaging

- Conversation model (between student and landlord)
- Message model with read status
- Real-time WebSocket support
- Delete conversation feature

#### 5. payments (To be implemented)

- Payment model for transactions
- Refund model for refund requests
- Stripe integration
- Escrow system

#### 6. contracts

- Contract model with status tracking
- ContractTermination for early termination
- Auto-generation from accepted bids
- Digital signature support
- Celery tasks for expiry notifications

#### 7. notifications

- Notification model for in-app alerts
- Multiple notification types
- Read/unread status
- AJAX-based unread count

---

## Changelog

### Version 1.0 (April 2026)

- Initial release
- Complete bidding system
- Contract management
- Real-time messaging
- Payment processing (To be implemented)
- Review system
- Notification system
- All core features implemented

---

## License

**Copyright © 2026 | All Rights Reserved by BidNest**

---

## Contact

For issues, questions, or support:

- Email: Mdnasif17@gmail.com
- GitHub: https://github.com/MdNasif2000/bidnest.git

---

**End of Complete Guide**

_Last Updated: April 26, 2026_
