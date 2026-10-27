from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.db.models.functions import TruncMonth

from gigs.models import Gig
from orders.models import Order


@login_required
def dashboard(request):

    user = request.user

    # =====================================================
    # SELLER DASHBOARD
    # =====================================================

    if user.is_seller:

        total_gigs = Gig.objects.filter(
            seller=user,
            is_active=True
        ).count()

        orders = Order.objects.filter(
            seller=user
        )

        total_orders = orders.count()

        # ---------------------------
        # Total Revenue
        # ---------------------------

        total_revenue = (
            orders
            .filter(status="Completed")
            .aggregate(total=Sum("amount"))["total"]
            or 0
        )

        # ---------------------------
        # Revenue Chart Data
        # ---------------------------

        monthly_revenue = (
            orders
            .filter(status="Completed")
            .annotate(month=TruncMonth("created_at"))
            .values("month")
            .annotate(total=Sum("amount"))
            .order_by("month")
        )

        chart_labels = [
            item["month"].strftime("%b %Y")
            for item in monthly_revenue
        ]

        chart_data = [
            float(item["total"] or 0)
            for item in monthly_revenue
        ]

        context = {

            "total_gigs": total_gigs,

            "total_orders": total_orders,

            "total_revenue": total_revenue,

            "assessment_score": user.assessment_score,

            "recent_orders": orders.order_by(
                "-created_at"
            )[:5],

            # Revenue chart
            "chart_labels": chart_labels,

            "chart_data": chart_data,

            "assessment_percentage": user.assessment_percentage,

        }

        return render(
            request,
            "dashboard/seller_dashboard.html",
            context,
        )

    # =====================================================
    # BUYER DASHBOARD
    # =====================================================

    orders = Order.objects.filter(
        buyer=user
    )

    context = {

        "total_orders": orders.count(),

        "total_spent": (
            orders.aggregate(
                total=Sum("amount")
            )["total"] or 0
        ),

        "recent_orders": orders.order_by(
            "-created_at"
        )[:5],

    }

    return render(
        request,
        "dashboard/buyer_dashboard.html",
        context,
    )