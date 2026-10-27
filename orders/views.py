from io import BytesIO

from django.shortcuts import (
    render,
    redirect,
    get_object_or_404
)

from django.contrib.auth.decorators import login_required
from django.contrib import messages

from django.http import HttpResponse

from django.db.models import Q

from reviews.models import Review
from gigs.models import Gig

from .models import Order
from .forms import DeliverableForm

from notifications.utils import create_notification

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)

from reportlab.lib import colors

from reportlab.lib.pagesizes import A4

from reportlab.lib.styles import (
    getSampleStyleSheet,
    ParagraphStyle
)

from reportlab.lib.enums import (
    TA_CENTER,
    TA_LEFT
)

from reportlab.lib.units import inch


# =========================================================
# ORDER SUMMARY
# =========================================================

@login_required
def order_summary(request, gig_id):

    if request.user.is_seller:
        return redirect("dashboard")

    gig = get_object_or_404(
        Gig,
        id=gig_id,
        is_active=True
    )

    # Check if the buyer has already ordered this gig
    existing_order = Order.objects.filter(
        buyer=request.user,
        gig=gig
    ).exclude(status="Cancelled").exists() # Exclude cancelled orders if applicable

    if existing_order:
        messages.warning(
            request,
            "You have already purchased this gig and cannot order it again."
        )
        return redirect("gig_detail", pk=gig.id)

    return render(
        request,
        "orders/order_summary.html",
        {
            "gig": gig
        }
    )


# =========================================================
# ORDERS LIST
# =========================================================

@login_required
def orders(request):

    if request.user.is_seller:

        orders = (
            Order.objects
            .filter(
                seller=request.user
            )
            .select_related(
                "buyer",
                "seller",
                "gig"
            )
            .order_by("-created_at")
        )

    else:

        orders = (
            Order.objects
            .filter(
                buyer=request.user
            )
            .select_related(
                "buyer",
                "seller",
                "gig"
            )
            .order_by("-created_at")
        )

    # =====================================================
    # FIND SELLER'S FIRST COMPLETED ORDER
    # =====================================================

    first_completed_order_id = None

    if request.user.is_seller:

        first_completed_order = (
            Order.objects
            .filter(
                seller=request.user,
                status="Completed"
            )
            .order_by("created_at", "id")
            .first()
        )

        if first_completed_order:

            first_completed_order_id = (
                first_completed_order.id
            )

    return render(
        request,
        "orders/orders.html",
        {
            "orders": orders,

            "first_completed_order_id":
                first_completed_order_id,
        }
    )


# =========================================================
# ACCEPT ORDER
# =========================================================

@login_required
def accept_order(request, pk):

    order = get_object_or_404(
        Order,
        pk=pk,
        seller=request.user
    )

    if order.status != "Pending":

        return redirect("orders")

    order.status = "Confirmed"

    order.save()

    create_notification(

        user=order.buyer,

        title="Order Accepted",

        message=(
            f"{order.seller.username} "
            f"accepted your order for "
            f"'{order.gig.title}'."
        ),

        link=f"/orders/{order.id}/"

    )

    messages.success(
        request,
        "Order accepted successfully."
    )

    return redirect("orders")


# =========================================================
# START ORDER
# =========================================================

@login_required
def start_order(request, pk):

    order = get_object_or_404(
        Order,
        pk=pk,
        seller=request.user
    )

    if order.status != "Confirmed":

        return redirect("orders")

    order.status = "In Progress"

    order.save()

    create_notification(

        user=order.buyer,

        title="Work Started",

        message=(
            f"{order.seller.username} "
            f"started working on "
            f"'{order.gig.title}'."
        ),

        link=f"/orders/{order.id}/"

    )

    messages.success(
        request,
        "Work started."
    )

    return redirect("orders")


# =========================================================
# ORDER DETAIL
# =========================================================

@login_required
def order_detail(request, pk):

    if request.user.is_seller:

        order = get_object_or_404(

            Order.objects.select_related(
                "buyer",
                "seller",
                "gig"
            ),

            pk=pk,

            seller=request.user

        )

    else:

        order = get_object_or_404(

            Order.objects.select_related(
                "buyer",
                "seller",
                "gig"
            ),

            pk=pk,

            buyer=request.user

        )

    review = Review.objects.filter(
        order=order
    ).first()

    # =====================================================
    # CHECK WHETHER THIS IS FIRST COMPLETED ORDER
    # =====================================================

    is_first_completed_order = False

    if request.user.is_seller and order.status == "Completed":

        first_completed_order = (
            Order.objects
            .filter(
                seller=request.user,
                status="Completed"
            )
            .order_by("created_at", "id")
            .first()
        )

        if (
            first_completed_order
            and first_completed_order.id == order.id
        ):

            is_first_completed_order = True

    return render(
        request,
        "orders/order_detail.html",
        {
            "order": order,

            "review": review,

            "has_review": review is not None,

            "is_first_completed_order":
                is_first_completed_order,
        }
    )


# =========================================================
# UPLOAD DELIVERABLE
# =========================================================

@login_required
def upload_deliverable(request, pk):

    order = get_object_or_404(
        Order,
        pk=pk,
        seller=request.user
    )

    if order.status not in [
        "In Progress",
        "Revision"
    ]:

        return redirect(
            "order_detail",
            pk=pk
        )

    if request.method == "POST":

        form = DeliverableForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():

            delivery = form.save(
                commit=False
            )

            delivery.order = order

            delivery.uploaded_by = request.user

            delivery.save()

            order.status = "Delivered"

            order.save()

            create_notification(

                user=order.buyer,

                title="Deliverables Uploaded",

                message=(
                    f"{order.seller.username} "
                    f"uploaded deliverables for "
                    f"'{order.gig.title}'."
                ),

                link=f"/orders/{order.id}/"

            )

            messages.success(
                request,
                "Deliverables uploaded successfully."
            )

            return redirect(
                "order_detail",
                pk=order.pk
            )

    else:

        form = DeliverableForm()

    return render(
        request,
        "orders/upload_deliverable.html",
        {
            "form": form,
            "order": order
        }
    )


# =========================================================
# APPROVE DELIVERY
# =========================================================

@login_required
def approve_delivery(request, pk):

    order = get_object_or_404(
        Order,
        pk=pk,
        buyer=request.user
    )

    if order.status != "Delivered":

        return redirect(
            "order_detail",
            pk=pk
        )

    order.status = "Completed"

    order.save()

    create_notification(

        user=order.seller,

        title="Order Completed",

        message=(
            f"{order.buyer.username} "
            f"approved your delivery for "
            f"'{order.gig.title}'."
        ),

        link=f"/orders/{order.id}/"

    )

    messages.success(

        request,

        "Delivery approved successfully. "
        "You can now leave a review for the seller."

    )

    return redirect(
        "order_detail",
        pk=pk
    )


# =========================================================
# REQUEST REVISION
# =========================================================

@login_required
def request_revision(request, pk):

    order = get_object_or_404(
        Order,
        pk=pk,
        buyer=request.user
    )

    if order.status != "Delivered":

        return redirect(
            "order_detail",
            pk=pk
        )

    order.status = "Revision"

    order.save()

    create_notification(

        user=order.seller,

        title="Revision Requested",

        message=(
            f"{order.buyer.username} "
            f"requested a revision for "
            f"'{order.gig.title}'."
        ),

        link=f"/orders/{order.id}/"

    )

    messages.info(
        request,
        "Revision requested."
    )

    return redirect(
        "order_detail",
        pk=pk
    )


# =========================================================
# DOWNLOAD FIRST COMPLETION CERTIFICATE
# =========================================================

@login_required
def download_certificate(request, pk):

    order = get_object_or_404(
        Order,
        pk=pk,
        seller=request.user,
        status="Completed"
    )

    # Already downloaded
    if order.certificate_downloaded:
        messages.warning(
            request,
            "Certificate has already been downloaded."
        )
        return redirect("orders")

    # Check whether this is seller's first completed order
    first_completed_order = (
        Order.objects
        .filter(
            seller=request.user,
            status="Completed"
        )
        .order_by("created_at", "id")
        .first()
    )

    if not first_completed_order:
        return redirect("orders")

    if first_completed_order.id != order.id:
        messages.warning(
            request,
            "Certificate is available only for your first completed order."
        )
        return redirect("orders")

    # Generate certificate
    from .utils import generate_certificate_pdf

    certificate_pdf = generate_certificate_pdf(order)

    # Mark as downloaded
    order.certificate_downloaded = True
    order.save(update_fields=["certificate_downloaded"])

    response = HttpResponse(
        certificate_pdf,
        content_type="application/pdf"
    )

    response[
        "Content-Disposition"
    ] = (
        f'attachment; '
        f'filename="CertiHire_Certificate_Order_{order.id}.pdf"'
    )

    return response