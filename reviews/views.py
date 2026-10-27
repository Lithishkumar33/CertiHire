from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from orders.models import Order
from notifications.utils import create_notification

from .models import Review
from .forms import ReviewForm
from django.db.models import Avg, Count



@login_required
def add_review(request, order_id):

    order = get_object_or_404(
        Order.objects.select_related(
            "buyer",
            "seller",
            "gig"
        ),
        id=order_id
    )

    # Only buyer can review
    if request.user != order.buyer:

        messages.error(
            request,
            "Only the buyer can review this order."
        )

        return redirect("order_detail", pk=order.id)

    # Order must be completed
    if order.status != "Completed":

        messages.error(
            request,
            "You can review only completed orders."
        )

        return redirect("order_detail", pk=order.id)

    # Prevent duplicate reviews
    if hasattr(order, "review"):

        messages.info(
            request,
            "You have already reviewed this order."
        )

        return redirect("order_detail", pk=order.id)

    if request.method == "POST":

        form = ReviewForm(request.POST)

        if form.is_valid():

            review = form.save(commit=False)

            review.order = order
            review.buyer = order.buyer
            review.seller = order.seller

            review.save()

            create_notification(
                user=order.seller,
                title="New Review Received",
                message=f"{order.buyer.username} rated you {review.rating}/5 ⭐",
                link="/reviews/"
            )

            messages.success(
                request,
                "Thank you for your review!"
            )

            return redirect("order_detail", pk=order.id)

    else:

        form = ReviewForm()

    return render(
        request,
        "reviews/add_review.html",
        {
            "form": form,
            "order": order,
        }
    )



@login_required
def reviews(request):

    if request.user.is_seller:

        reviews = (
            Review.objects.filter(
                seller=request.user
            )
            .select_related(
                "buyer",
                "order",
                "order__gig"
            )
            .order_by("-created_at")
        )

        average_rating = reviews.aggregate(
            avg=Avg("rating")
        )["avg"] or 0

        total_reviews = reviews.count()

        rating_breakdown = reviews.values(
            "rating"
        ).annotate(
            total=Count("id")
        ).order_by("-rating")

        # Optional: mark reviews as read if you add an is_read field later
        # reviews.filter(is_read=False).update(is_read=True)

        context = {

            "reviews": reviews,

            "average_rating": round(average_rating, 1),

            "total_reviews": total_reviews,

            "rating_breakdown": rating_breakdown,

            "is_seller": True,

        }

    else:

        reviews = (
            Review.objects.filter(
                buyer=request.user
            )
            .select_related(
                "seller",
                "order",
                "order__gig"
            )
            .order_by("-created_at")
        )

        context = {

            "reviews": reviews,

            "is_seller": False,

        }

    return render(
        request,
        "reviews/reviews.html",
        context
    )