# CertiHire — Certified Freelance Marketplace & Talent Platform

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.1%2B-092E20?logo=django&logoColor=white)](https://www.djangoproject.com/)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-7952B3?logo=bootstrap&logoColor=white)](https://getbootstrap.com/)
[![JavaScript](https://img.shields.io/badge/JavaScript-ES6%2B-F7DF1E?logo=javascript&logoColor=black)](https://developer.mozilla.org/)
[![Database](https://img.shields.io/badge/Database-SQLite%20%7C%20PostgreSQL-336791?logo=postgresql&logoColor=white)](https://www.postgresql.org/)

> **CertiHire** is an end-to-end online freelance marketplace connecting businesses with certified independent talent. In addition to traditional gig listings and order placement, CertiHire integrates an automated **Skill Assessment Engine** that verifies freelancer competencies before they offer specialized services, establishing verified trust between buyers and sellers.

---

## 🌟 Key Features

### 1. Dual-Role Authentication & Onboarding
- Role-based account creation for **Clients** (buyers) and **Freelancers** (sellers).
- Custom profile management with bio, portfolio showcase, hourly/fixed rates, and skill tags.

### 2. Verified Skill Assessment Engine
- Integrated quiz and assessment module testing freelancer domain knowledge.
- Automated score evaluation and credentialing before enabling category-specific gig creation.

### 3. Gig Discovery & Management
- Multi-tier gig packages with scope deliverables and delivery timelines.
- Real-time search and multi-criteria category filtering for clients.
- Rich media showcase supporting gig preview images.

### 4. Order Lifecycle & Delivery Workflow
- Milestone-oriented order management tracking states: Pending → In Progress → Delivered → Completed / Cancelled.
- Secure client delivery reviews, revision requests, and order approval.

### 5. In-App Messaging & Notifications
- Integrated buyer-seller messaging system with context processors for unread count.
- Dynamic notification toasts for order status transitions, new messages, and assessment completions.

### 6. Ratings & Social Proof
- 5-star rating system with verified customer reviews.
- Seller performance badges and rating aggregations.

### 7. Dual Control Dashboards & Admin Portal
- **Freelancer Dashboard**: Track active orders, pending deliveries, earnings summary, and gig analytics.
- **Client Dashboard**: Manage ongoing purchases, track milestones, and view order receipts.
- **Custom Admin Panel**: Dedicated administrative interface for platform moderation and dispute handling.

---

## 🏗️ System Architecture

`
┌─────────────────────────────────────────────────────────────┐
│                      Client Browser                         │
│       (Bootstrap 5, Responsive UI, JavaScript Fetch)        │
└──────────────────────────────┬──────────────────────────────┘
                               │ HTTP / WebSocket Requests
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                     Django Web Layer                        │
│  ┌────────────────────┐ ┌──────────────────┐ ┌───────────┐  │
│  │   Authentication   │ │  Gig & Category  │ │  Orders   │  │
│  │    & Profiles      │ │    Management    │ │  Workflow │  │
│  └────────────────────┘ └──────────────────┘ └───────────┘  │
│  ┌────────────────────┐ ┌──────────────────┐ ┌───────────┐  │
│  │  Skill Assessment  │ │    Messaging     │ │  Reviews  │  │
│  │     Engine         │ │  & Notifications │ │ & Ratings │  │
│  └────────────────────┘ └──────────────────┘ └───────────┘  │
└──────────────────────────────┬──────────────────────────────┘
                               │ ORM Queries
                               ▼
┌─────────────────────────────────────────────────────────────┐
│               Database Layer (SQLite / PostgreSQL)          │
│   Users • Gigs • Orders • Questions • Messages • Reviews    │
└─────────────────────────────────────────────────────────────┘
`

---

## 🛠️ Technology Stack

- **Backend Framework**: Python, Django 5.1+, Django Channels, Daphne ASGI
- **Frontend**: HTML5, CSS3, Bootstrap 5, JavaScript (ES6+), FontAwesome
- **Database**: SQLite (Development) / PostgreSQL (Production ready)
- **PDF & Media**: ReportLab, Pillow (PIL)
- **Configuration**: Python-Decouple (.env support)

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- pip and irtualenv

### Installation Steps

1. **Clone the repository:**
   `ash
   git clone https://github.com/Lithishkumar33/CertiHire.git
   cd CertiHire
   `

2. **Create and activate a virtual environment:**
   `ash
   # Windows
   python -m venv venv
   .\venv\Scripts\activate

   # Linux / macOS
   python3 -m venv venv
   source venv/bin/activate
   `

3. **Install dependencies:**
   `ash
   pip install -r requirements.txt
   `

4. **Environment Configuration:**
   `ash
   cp .env.example .env
   # Edit .env with your SECRET_KEY and preferences if needed
   `

5. **Apply Database Migrations:**
   `ash
   python manage.py makemigrations
   python manage.py migrate
   `

6. **Create an Administrator Account:**
   `ash
   python manage.py createsuperuser
   `

7. **Run the Development Server:**
   `ash
   python manage.py runserver
   `
   Open your browser at http://127.0.0.1:8000/.

---

## 📁 Project Structure

`
Certi_Hire/
│── accounts/          # User authentication, registration & roles
│── adminpanel/        # Custom administrator management interface
│── assessment/        # Skill test questions & qualification models
│── chat/              # In-app messaging and context processor
│── dashboard/         # Client & Freelancer analytical dashboards
│── gigs/              # Gig creation, search, filtering & packages
│── landing/           # High-conversion homepage & explore views
│── notifications/     # Notification context processors & alerts
│── orders/            # Order placement, status tracking & milestone flow
│── payments/          # Transaction history and payment handling
│── profiles/          # Freelancer public profiles, bio & badges
│── reviews/           # Rating and client testimonial system
│── Certi_Hire/        # Core settings, urls, asgi & wsgi
│── templates/         # Modular Django HTML templates
│── static/            # Custom CSS, JS scripts, and assets
│── manage.py          # Django CLI utility
└── requirements.txt   # Project dependencies
`

---

## 👨‍💻 Author

**Lithish Kumar G**  
- **Email:** [7760lithish@gmail.com](mailto:7760lithish@gmail.com)  
- **LinkedIn:** [linkedin.com/in/lithish-kumar-g-aa0b67279](https://www.linkedin.com/in/lithish-kumar-g-aa0b67279)  
- **GitHub:** [github.com/Lithishkumar33](https://github.com/Lithishkumar33)  
- **Location:** Bengaluru, Karnataka, India  
