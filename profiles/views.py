from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Avg, Sum
from .forms import SettingsForm, ChangePasswordForm
from .forms import ProfileForm
from django.contrib.auth import update_session_auth_hash
from reviews.models import Review
from orders.models import Order
from gigs.models import Gig


@login_required
def profile(request):

    profile = request.user.profile

    if request.method == "POST":

        form = ProfileForm(
            request.POST,
            request.FILES,
            instance=profile
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Profile updated successfully."
            )

            return redirect("profile")

    else:

        form = ProfileForm(
            instance=profile
        )

    completed_orders = 0
    active_gigs = 0
    total_reviews = 0
    average_rating = 0
    total_earnings = 0

    if request.user.is_seller:

        completed_orders = Order.objects.filter(
            seller=request.user,
            status="Completed"
        ).count()

        active_gigs = Gig.objects.filter(
            seller=request.user,
            is_active=True
        ).count()

        reviews = Review.objects.filter(
            seller=request.user
        )

        total_reviews = reviews.count()

        average_rating = reviews.aggregate(
            Avg("rating")
        )["rating__avg"] or 0

        total_earnings = Order.objects.filter(
            seller=request.user,
            status="Completed"
        ).aggregate(
            Sum("amount")
        )["amount__sum"] or 0

    else:

        completed_orders = Order.objects.filter(
            buyer=request.user,
            status="Completed"
        ).count()

    return render(
        request,
        "profiles/profile.html",
        {
            "form": form,
            "profile": profile,
            "completed_orders": completed_orders,
            "active_gigs": active_gigs,
            "total_reviews": total_reviews,
            "average_rating": round(average_rating,1),
            "total_earnings": total_earnings,
        }
    )
    
from .forms import SettingsForm


@login_required
def settings(request):

    profile = request.user.profile

    if request.method == "POST":

        form = SettingsForm(
            request.POST,
            instance=profile
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Settings updated successfully."
            )

            return redirect("settings")

    else:

        form = SettingsForm(
            instance=profile
        )

    return render(
        request,
        "profiles/settings.html",
        {
            "form": form,
        }
    )
    



@login_required
def change_password(request):

    if request.method == "POST":

        form = ChangePasswordForm(
            request.user,
            request.POST
        )

        if form.is_valid():

            new_password = form.cleaned_data["new_password"]

            request.user.set_password(new_password)
            request.user.save()

            # Keep user logged in after password change
            update_session_auth_hash(
                request,
                request.user
            )

            messages.success(
                request,
                "Your password has been changed successfully."
            )

            return redirect("settings")

    else:

        form = ChangePasswordForm(
            request.user
        )

    return render(
        request,
        "profiles/change_password.html",
        {
            "form": form
        }
    )