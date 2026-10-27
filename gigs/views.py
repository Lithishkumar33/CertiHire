from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import GigForm
from django.http import HttpResponse
from .models import Gig
from django.shortcuts import get_object_or_404
from django.contrib import messages
from reviews.models import Review
from django.db.models import Avg
from orders.models import Order  # Make sure this import is present

@login_required
def create_gig(request):
    if not request.user.is_seller:
        return HttpResponse("Only sellers can create gigs.")

    if not request.user.assessment_passed:
        return render(
            request,
            "gigs/assessment_required.html"
        )

    if request.method == "POST":
        form = GigForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():
            gig = form.save(commit=False)
            gig.seller = request.user
            gig.save()
            return redirect("my_gigs")
    else:
        form = GigForm()

    return render(
        request,
        "gigs/create_gig.html",
        {
            "form": form
        }
    )

@login_required
def my_gigs(request):
    gigs = Gig.objects.filter(
        seller=request.user
    )

    return render(
        request,
        "gigs/my_gigs.html",
        {
            "gigs": gigs
        }
    )


from django.db.models import Q

def gig_list(request):
    gigs = Gig.objects.filter(is_active=True).select_related("seller")

    # 1. Search Query
    search_query = request.GET.get("q", "")
    if search_query:
        gigs = gigs.filter(
            Q(title__icontains=search_query) | 
            Q(description__icontains=search_query) |
            Q(category__icontains=search_query)
        )

    # 2. Category Filter
    selected_category = request.GET.get("category", "")
    if selected_category and selected_category != "All Categories":
        gigs = gigs.filter(category=selected_category)

    # 3. Price Sorting
    price_sort = request.GET.get("sort", "")
    if price_sort == "low_high":
        gigs = gigs.order_by("price")
    elif price_sort == "high_low":
        gigs = gigs.order_by("-price")
    else:
        gigs = gigs.order_by("-id") # Default newest first

    # Get unique categories for dropdown options dynamically (optional)
    categories = Gig.objects.filter(is_active=True).values_list("category", flat=True).distinct()

    return render(
        request,
        "marketplace/marketplace.html",
        {
            "gigs": gigs,
            "categories": categories,
            "search_query": search_query,
            "selected_category": selected_category,
            "price_sort": price_sort,
        }
    )


def gig_detail(request, pk):
    gig = get_object_or_404(
        Gig,
        pk=pk,
        is_active=True
    )

    related_gigs = Gig.objects.filter(
        category=gig.category,
        is_active=True
    ).exclude(
        pk=gig.pk
    )[:3]

    # Reviews for this gig only
    gig_reviews = (
        Review.objects.filter(
            order__gig=gig
        )
        .select_related(
            "buyer"
        )
        .order_by("-created_at")
    )

    average_rating = (
        gig_reviews.aggregate(
            average=Avg("rating")
        )["average"] or 0
    )

    total_reviews = gig_reviews.count()

    # Check if the user has already ordered this gig
    has_ordered = False
    if request.user.is_authenticated and not request.user.is_seller:
        has_ordered = Order.objects.filter(buyer=request.user, gig=gig).exists()

    return render(
        request,
        "marketplace/gig_detail.html",
        {
            "gig": gig,
            "related_gigs": related_gigs,
            "gig_reviews": gig_reviews,
            "average_rating": round(average_rating, 1),
            "total_reviews": total_reviews,
            "has_ordered": has_ordered,
        }
    )

@login_required
def edit_gig(request, pk):
    gig = get_object_or_404(
        Gig,
        pk=pk,
        seller=request.user
    )

    if request.method == "POST":
        form = GigForm(
            request.POST,
            request.FILES,
            instance=gig
        )

        if form.is_valid():
            form.save()
            return redirect("my_gigs")
    else:
        form = GigForm(instance=gig)

    return render(
        request,
        "gigs/edit_gig.html",
        {
            "form": form,
            "gig": gig,
        }
    )

@login_required
def delete_gig(request, pk):
    gig = get_object_or_404(
        Gig,
        pk=pk,
        seller=request.user
    )

    if request.method == "POST":
        gig.delete()
        messages.success(
            request,
            "Gig deleted successfully."
        )
        return redirect("my_gigs")

    return render(
        request,
        "gigs/delete_gig.html",
        {
            "gig": gig
        }
    )