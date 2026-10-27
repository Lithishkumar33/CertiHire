from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum
from assessment.models import Question
from accounts.models import User
from gigs.models import Gig
from orders.models import Order
from django.db import models
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required

# =========================================================
# ADMIN LOGIN
# =========================================================

def admin_login(request):

    if request.user.is_authenticated and request.user.is_staff:
        return redirect("admin_dashboard")

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None and user.is_staff:

            login(request, user)

            return redirect("admin_dashboard")

        messages.error(
            request,
            "Invalid admin credentials."
        )

    return render(
        request,
        "adminpanel/login.html"
    )


# =========================================================
# ADMIN DASHBOARD
# =========================================================

@login_required
def admin_dashboard(request):

    if not request.user.is_staff:
        return redirect("admin_login")


    # -----------------------------------------------------
    # USERS
    # -----------------------------------------------------

    total_buyers = User.objects.filter(
        is_seller=False
    ).count()

    total_sellers = User.objects.filter(
        is_seller=True
    ).count()


    # -----------------------------------------------------
    # APPROVED SELLERS
    # -----------------------------------------------------

    approved_sellers = User.objects.filter(
        is_seller=True,
        is_approved=True
    ).count()


    # -----------------------------------------------------
    # GIGS
    # -----------------------------------------------------

    total_gigs = Gig.objects.count()


    # -----------------------------------------------------
    # ORDERS
    # -----------------------------------------------------

    total_orders = Order.objects.count()


    # -----------------------------------------------------
    # REVENUE
    # -----------------------------------------------------

    completed_orders = Order.objects.filter(
        status="Completed"
    )

    total_revenue = completed_orders.aggregate(
        total=Sum("amount")
    )["total"] or 0


    # -----------------------------------------------------
    # ASSESSMENTS
    # -----------------------------------------------------
    #
    # A score greater than 0 means the seller has submitted
    # an assessment.
    # -----------------------------------------------------

    assessment_submitted = User.objects.filter(
        is_seller=True,
        assessment_score__gt=0
    ).count()


    # -----------------------------------------------------
    # PENDING APPROVALS
    # -----------------------------------------------------

    pending_approvals = User.objects.filter(
        is_seller=True,
        assessment_passed=True,
        is_approved=False
    ).count()


    # -----------------------------------------------------
    # DASHBOARD
    # -----------------------------------------------------

    return render(
        request,
        "adminpanel/dashboard.html",
        {
            "total_buyers": total_buyers,
            "total_sellers": total_sellers,
            "approved_sellers": approved_sellers,
            "total_gigs": total_gigs,
            "total_orders": total_orders,
            "total_revenue": total_revenue,
            "assessment_submitted": assessment_submitted,
            "pending_approvals": pending_approvals,
        }
    )


# =========================================================
# ADMIN LOGOUT
# =========================================================

@login_required
def admin_logout(request):

    if not request.user.is_staff:
        return redirect("dashboard")

    logout(request)

    return redirect("admin_login")


# =========================================================
# USERS MANAGEMENT
# =========================================================

@login_required
def manage_users(request):

    if not request.user.is_staff:
        return redirect("admin_login")


    # -----------------------------------------------------
    # BUYERS
    # -----------------------------------------------------

    buyers = User.objects.filter(
        is_seller=False
    ).order_by("-created_at")


    # -----------------------------------------------------
    # SELLERS
    # -----------------------------------------------------

    sellers = User.objects.filter(
        is_seller=True
    ).order_by("-created_at")


    return render(
        request,
        "adminpanel/users.html",
        {
            "buyers": buyers,
            "sellers": sellers,
        }
    )


# =========================================================
# APPROVE SELLER
# =========================================================

@staff_member_required
def approve_seller(request, pk):

    print("====================================")
    print("APPROVE SELLER FUNCTION CALLED")
    print("SELLER ID:", pk)
    print("====================================")

    seller = get_object_or_404(
        User,
        pk=pk,
        is_seller=True
    )

    print("SELLER:", seller.username)
    print("SELLER EMAIL:", seller.email)

    # ==========================================
    # APPROVE SELLER
    # ==========================================

    seller.is_approved = True
    seller.assessment_rejected = False

    seller.save(
        update_fields=[
            "is_approved",
            "assessment_rejected"
        ]
    )

    print("SELLER APPROVED IN DATABASE")

    # ==========================================
    # CHECK EMAIL
    # ==========================================

    if not seller.email:

        print("ERROR: SELLER HAS NO EMAIL")

        messages.warning(
            request,
            f"{seller.username} approved, "
            "but no email address is registered."
        )

        return redirect(
            "manage_users"
        )

    print("EMAIL ADDRESS FOUND:", seller.email)

    # ==========================================
    # SEND APPROVAL EMAIL
    # ==========================================

    try:

        print("Loading approval email template...")

        html_message = render_to_string(
            "emails/seller_approved.html",
            {
                "username": seller.username,

                "dashboard_url":
                    request.build_absolute_uri(
                        "/dashboard/"
                    ),
            }
        )

        print("APPROVAL TEMPLATE LOADED")

        email = EmailMultiAlternatives(

            subject=(
                "Your CertiHire Seller Application "
                "Has Been Approved"
            ),

            body=(
                f"Hi {seller.username},\n\n"

                "Congratulations!\n\n"

                "Your CertiHire seller application "
                "has been approved.\n\n"

                "You can now access your seller "
                "dashboard and start offering "
                "your services.\n\n"

                "Regards,\n"
                "Lithish Kumar\n"
                "Founder / Administrator\n"
                "CertiHire"
            ),

            from_email=settings.DEFAULT_FROM_EMAIL,

            to=[
                seller.email
            ],

        )

        print("EMAIL OBJECT CREATED")

        email.attach_alternative(
            html_message,
            "text/html"
        )

        print("HTML ATTACHED")

        email.send(
            fail_silently=False
        )

        print("====================================")
        print("APPROVAL EMAIL SENT SUCCESSFULLY")
        print("TO:", seller.email)
        print("====================================")

        messages.success(
            request,
            f"{seller.username} has been approved "
            "and approval email has been sent."
        )

    except Exception as e:

        print("====================================")
        print("APPROVAL EMAIL FAILED")
        print("ERROR:", repr(e))
        print("SELLER EMAIL:", seller.email)
        print("====================================")

        messages.warning(
            request,
            f"{seller.username} has been approved, "
            "but the approval email could not be sent."
        )

    return redirect(
        "manage_users"
    )
# =========================================================
# ASSESSMENT MANAGEMENT
# =========================================================

@login_required
def assessment_management(request):

    if not request.user.is_staff:
        return redirect("admin_login")

    questions = Question.objects.all().order_by("id")

    return render(
        request,
        "adminpanel/assessment.html",
        {
            "questions": questions,
        }
    )


# =========================================================
# ADD QUESTION
# =========================================================

@login_required
def add_question(request):

    if not request.user.is_staff:
        return redirect("admin_login")

    if request.method == "POST":

        question_text = request.POST.get("question")
        option_a = request.POST.get("option_a")
        option_b = request.POST.get("option_b")
        option_c = request.POST.get("option_c")
        option_d = request.POST.get("option_d")
        correct_answer = request.POST.get("correct_answer")

        Question.objects.create(
            question=question_text,
            option_a=option_a,
            option_b=option_b,
            option_c=option_c,
            option_d=option_d,
            correct_answer=correct_answer
        )

        messages.success(
            request,
            "Question added successfully."
        )

        return redirect("assessment_management")

    return render(
        request,
        "adminpanel/add_question.html"
    )


# =========================================================
# EDIT QUESTION
# =========================================================

@login_required
def edit_question(request, pk):

    if not request.user.is_staff:
        return redirect("admin_login")

    question = get_object_or_404(
        Question,
        pk=pk
    )

    if request.method == "POST":

        question.question = request.POST.get("question")
        question.option_a = request.POST.get("option_a")
        question.option_b = request.POST.get("option_b")
        question.option_c = request.POST.get("option_c")
        question.option_d = request.POST.get("option_d")
        question.correct_answer = request.POST.get(
            "correct_answer"
        )

        question.save()

        messages.success(
            request,
            "Question updated successfully."
        )

        return redirect("assessment_management")

    return render(
        request,
        "adminpanel/edit_question.html",
        {
            "question": question,
        }
    )


# =========================================================
# DELETE QUESTION
# =========================================================

@login_required
def delete_question(request, pk):

    if not request.user.is_staff:
        return redirect("admin_login")

    question = get_object_or_404(
        Question,
        pk=pk
    )

    question.delete()

    messages.success(
        request,
        "Question deleted successfully."
    )

    return redirect("assessment_management")

# =========================================================
# GIGS MANAGEMENT
# =========================================================

@login_required
def manage_gigs(request):

    if not request.user.is_staff:
        return redirect("admin_login")

    gigs = Gig.objects.select_related(
        "seller"
    ).order_by("-id")

    active_gigs = gigs.filter(
        is_active=True
    ).count()

    inactive_gigs = gigs.filter(
        is_active=False
    ).count()

    return render(
        request,
        "adminpanel/gigs.html",
        {
            "gigs": gigs,
            "active_gigs": active_gigs,
            "inactive_gigs": inactive_gigs,
        }
    )
    
# =========================================================
# ORDERS MANAGEMENT
# =========================================================

@login_required
def manage_orders(request):

    if not request.user.is_staff:
        return redirect("admin_login")

    orders = Order.objects.select_related(
        "buyer",
        "seller",
        "gig"
    ).order_by("-created_at")

    total_orders = orders.count()

    completed_orders = orders.filter(
        status="Completed"
    ).count()

    pending_orders = orders.filter(
        status="Pending"
    ).count()

    cancelled_orders = orders.filter(
        status="Cancelled"
    ).count()

    total_revenue = orders.filter(
        status="Completed"
    ).aggregate(
        total=Sum("amount")
    )["total"] or 0

    return render(
        request,
        "adminpanel/orders.html",
        {
            "orders": orders,

            "total_orders": total_orders,

            "completed_orders": completed_orders,

            "pending_orders": pending_orders,

            "cancelled_orders": cancelled_orders,

            "total_revenue": total_revenue,
        }
    )

# =========================================================
# REVENUE MANAGEMENT
# =========================================================

@login_required
def revenue_management(request):

    if not request.user.is_staff:
        return redirect("admin_login")

    # -----------------------------------------------------
    # Completed orders only
    # -----------------------------------------------------

    completed_orders = Order.objects.filter(
        status="Completed"
    ).select_related(
        "buyer",
        "seller",
        "gig"
    )


    # -----------------------------------------------------
    # Total Revenue
    # -----------------------------------------------------

    total_revenue = completed_orders.aggregate(
        total=Sum("amount")
    )["total"] or 0


    # -----------------------------------------------------
    # Completed Order Count
    # -----------------------------------------------------

    completed_order_count = completed_orders.count()


    # -----------------------------------------------------
    # Average Order Value
    # -----------------------------------------------------

    if completed_order_count > 0:

        average_order_value = (
            total_revenue / completed_order_count
        )

    else:

        average_order_value = 0


    # -----------------------------------------------------
    # Sellers who generated revenue
    # -----------------------------------------------------

    seller_revenue = completed_orders.values(
        "seller",
        "seller__username",
        "seller__profile_image"
    ).annotate(
        order_count=models.Count("id"),
        revenue=Sum("amount")
    ).order_by(
        "-revenue"
    )


    # -----------------------------------------------------
    # Number of earning sellers
    # -----------------------------------------------------

    earning_sellers = seller_revenue.count()


    # -----------------------------------------------------
    # Category Revenue
    # -----------------------------------------------------

    category_revenue = completed_orders.values(
        "gig__category"
    ).annotate(
        order_count=models.Count("id"),
        revenue=Sum("amount")
    ).order_by(
        "-revenue"
    )


    # -----------------------------------------------------
    # Recent completed orders
    # -----------------------------------------------------

    recent_orders = completed_orders.order_by(
        "-created_at"
    )[:10]


    return render(
        request,
        "adminpanel/revenue.html",
        {
            "total_revenue": total_revenue,

            "completed_orders": completed_order_count,

            "average_order_value": round(
                average_order_value,
                2
            ),

            "earning_sellers": earning_sellers,

            "seller_revenue": seller_revenue,

            "category_revenue": category_revenue,

            "recent_orders": recent_orders,
        }
    )
    

