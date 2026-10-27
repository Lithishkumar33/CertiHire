from django.db.models import Avg, Min
from django.shortcuts import render
from accounts.models import User
from gigs.models import Gig
from reviews.models import Review
from django.core.exceptions import ValidationError
from django.shortcuts import redirect
from django.contrib import messages


def home(request):

    featured_sellers = []

    sellers = User.objects.filter(
        is_seller=True
    ).select_related(
        "profile"
    )

    for seller in sellers:

        gigs = Gig.objects.filter(
            seller=seller,
            is_active=True
        )

        if not gigs.exists():
            continue

        reviews = Review.objects.filter(
            seller=seller
        )

        featured_sellers.append({

            "seller": seller,

            "rating": round(
                reviews.aggregate(
                    Avg("rating")
                )["rating__avg"] or 0,
                1
            ),

            "review_count": reviews.count(),

            "starting_price": gigs.aggregate(
                Min("price")
            )["price__min"],

        })

    featured_sellers = sorted(
        featured_sellers,
        key=lambda x: (
            x["rating"],
            x["review_count"]
        ),
        reverse=True
    )[:3]


    # =====================================================
    # FEATURED GIGS
    # =====================================================

    featured_gigs = []

    gigs = (
        Gig.objects
        .filter(
            is_active=True
        )
        .select_related(
            "seller",
            "seller__profile"
        )
    )

    for gig in gigs:

        reviews = Review.objects.filter(
            seller=gig.seller
        )

        featured_gigs.append({

            "gig": gig,

            "seller": gig.seller,

            "rating": round(
                reviews.aggregate(
                    Avg("rating")
                )["rating__avg"] or 0,
                1
            ),

            "review_count": reviews.count(),

        })

    featured_gigs = sorted(
        featured_gigs,
        key=lambda x: (
            x["rating"],
            x["review_count"]
        ),
        reverse=True
    )[:4]


    # =====================================================
    # DYNAMIC CATEGORIES FROM SELLER SKILLS
    # =====================================================

    category_map = {}

    category_styles = {
        "web": {
            "style": "web",
            "icon": "bi-code-slash"
        },
        "mobile": {
            "style": "mobile",
            "icon": "bi-phone"
        },
        "ai": {
            "style": "ai",
            "icon": "bi-cpu"
        },
        "design": {
            "style": "design",
            "icon": "bi-palette"
        },
    }

    for seller in sellers:

        skills = getattr(
            seller.profile,
            "skills",
            ""
        ) or ""

        for skill in skills.split(","):

            skill = skill.strip()

            if not skill:
                continue

            key = skill.lower()

            if key not in category_map:

                style = "design"
                icon = "bi-palette"

                if any(x in key for x in [
                    "web", "django", "html",
                    "css", "javascript",
                    "react", "node"
                ]):
                    style = "web"
                    icon = "bi-code-slash"

                elif any(x in key for x in [
                    "mobile", "android",
                    "ios", "flutter", "app"
                ]):
                    style = "mobile"
                    icon = "bi-phone"

                elif any(x in key for x in [
                    "ai", "python", "machine",
                    "learning", "data", "ml"
                ]):
                    style = "ai"
                    icon = "bi-cpu"

                category_map[key] = {
                    "name": skill,
                    "count": 0,
                    "style": style,
                    "icon": icon,
                }

            category_map[key]["count"] += 1

    categories = sorted(
        category_map.values(),
        key=lambda x: x["count"],
        reverse=True
    )[:4]


    # =====================================================
    # PLATFORM STATS
    # =====================================================

    registered_user_count = User.objects.count()

    verified_seller_count = User.objects.filter(
        is_seller=True
    ).count()

    active_gig_count = Gig.objects.filter(
        is_active=True
    ).count()

    # If your project already has a completed/order count,
    # replace this with that model's count.
    completed_project_count = 0

    average_rating = round(
        Review.objects.aggregate(
            Avg("rating")
        )["rating__avg"] or 0,
        1
    )


    # =====================================================
    # TESTIMONIALS
    # =====================================================

    testimonials = []

    recent_reviews = (
        Review.objects
        .filter(
            rating__isnull=False
        )
        .select_related(
            "seller",
            "seller__profile"
        )
        .order_by("-id")[:3]
    )

    for review in recent_reviews:

        text = (
            getattr(review, "comment", None)
            or getattr(review, "review", None)
            or getattr(review, "review_text", None)
            or "Great experience with CertiHire."
        )

        photo = None

        profile = getattr(
            review.seller,
            "profile",
            None
        )

        if profile and profile.profile_photo:

            try:
                photo = profile.profile_photo.url
            except ValueError:
                pass

        testimonials.append({

            "name": review.seller.username,

            "text": text,

            "photo": photo,

            "role": "Verified CertiHire User",

        })


    return render(
        request,
        "landing/home.html",
        {
            "featured_sellers": featured_sellers,
            "featured_gigs": featured_gigs,
            "categories": categories,
            "registered_user_count": registered_user_count,
            "completed_project_count": completed_project_count,
            "verified_seller_count": verified_seller_count,
            "active_gig_count": active_gig_count,
            "average_rating": average_rating,
            "testimonials": testimonials,
        }
    )
