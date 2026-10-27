from django.shortcuts import redirect, get_object_or_404, render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
import json
from gigs.models import Gig
from orders.models import Order
from notifications.utils import create_notification
from .models import Payment
from .services import create_cashfree_order, verify_cashfree_payment
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER
from reportlab.pdfbase import pdfmetrics
from .utils import (
    generate_invoice_pdf,
    send_payment_success_email,
)


def initiate_payment(request, gig_id):

    if request.user.is_seller:
        return redirect("dashboard")

    gig = get_object_or_404(
        Gig,
        id=gig_id,
        is_active=True
    )

    cashfree = create_cashfree_order(
        request,
        gig
    )

    if "payment_session_id" not in cashfree:
        return redirect("payment_failed")

    Payment.objects.create(

        buyer=request.user,

        gig=gig,

        amount=gig.price,

        cashfree_order_id=cashfree["order_id"],

        payment_session_id=cashfree["payment_session_id"]

    )

    return render(

        request,

        "payments/payment.html",

        {

            "payment_session_id": cashfree["payment_session_id"],

            "order_id": cashfree["order_id"]

        }

    )


def payment_success(request, order_id):

    print("====================================")
    print("PAYMENT SUCCESS VIEW CALLED")
    print("ORDER ID:", order_id)
    print("====================================")

    payment = get_object_or_404(
        Payment,
        cashfree_order_id=order_id
    )

    print("Payment found:", payment.id)

    # Verify payment with Cashfree
    try:

        response = verify_cashfree_payment(order_id)

        print("Cashfree response:")
        print(response)

    except Exception as e:

        print("====================================")
        print("CASHFREE VERIFICATION ERROR")
        print(repr(e))
        print("====================================")

        payment.status = "FAILED"
        payment.save(update_fields=["status"])

        return redirect("payment_failed")


    # =====================================================
    # CHECK PAYMENT STATUS
    # =====================================================

    if response.get("payment_status") == "SUCCESS":

        print("PAYMENT IS PAID")


        # =================================================
        # UPDATE PAYMENT
        # =================================================

        payment.status = "SUCCESS"

        payment.save(
            update_fields=["status"]
        )


        # =================================================
        # CREATE / GET ORDER
        # =================================================

        order, created = Order.objects.get_or_create(

            buyer=payment.buyer,

            seller=payment.gig.seller,

            gig=payment.gig,

            defaults={

                "amount": payment.amount,

                "status": "Pending"

            }

        )


        # =================================================
        # LINK PAYMENT TO ORDER
        # =================================================

        if payment.order_id != order.id:

            payment.order = order

            payment.save(
                update_fields=["order"]
            )


        # =================================================
        # SEND BUYER EMAIL ONLY FOR NEW ORDER
        # =================================================

        if created:

            print("NEW ORDER CREATED")

            # ---------------------------------------------
            # Seller notification inside website
            # ---------------------------------------------

            create_notification(

                user=order.seller,

                title="New Order Received",

                message=(
                    f"{order.buyer.username} "
                    f"placed an order for "
                    f"'{order.gig.title}'."
                ),

                link=f"/orders/{order.id}/"

            )


            # ---------------------------------------------
            # Generate invoice
            # ---------------------------------------------

            try:

                print("Generating invoice...")

                invoice_pdf = generate_invoice_pdf(
                    payment
                )

                print("Invoice generated successfully")


            except Exception as e:

                print("====================================")
                print("INVOICE GENERATION ERROR")
                print(repr(e))
                print("====================================")

                invoice_pdf = None


            # ---------------------------------------------
            # Send payment success email
            # ---------------------------------------------

            if invoice_pdf:

                try:

                    print("Sending payment success email...")

                    send_payment_success_email(

                        request=request,

                        payment=payment,

                        order=order,

                        invoice_pdf=invoice_pdf

                    )

                    print(
                        "PAYMENT SUCCESS EMAIL SENT"
                    )

                except Exception as e:

                    print("====================================")
                    print("PAYMENT EMAIL ERROR")
                    print(repr(e))
                    print("====================================")


        else:

            print(
                "Order already exists - "
                "email not sent again."
            )


        # =================================================
        # SUCCESS PAGE
        # =================================================

        return render(

            request,

            "payments/success.html",

            {
                "order_id": order.id,
            }

        )


    # =====================================================
    # PAYMENT NOT PAID
    # =====================================================

    print(
        "PAYMENT NOT PAID"
    )

    print(
        "Cashfree response:",
        response
    )


    payment.status = "FAILED"

    payment.save(
        update_fields=["status"]
    )


    return redirect(
        "payment_failed"
    )


def payment_failed(request):

    return render(

        request,

        "payments/failed.html"

    )


@csrf_exempt
def cashfree_webhook(request):

    if request.method != "POST":
        return HttpResponse(status=405)

    payload = json.loads(request.body)

    order_data = payload.get("data", {}).get("order", {})

    order_id = order_data.get("order_id")

    payment_status = order_data.get("order_status")

    try:

        payment = Payment.objects.get(

            cashfree_order_id=order_id

        )

    except Payment.DoesNotExist:

        return HttpResponse(status=404)

    if payment_status == "PAID":

        payment.status = "SUCCESS"

        payment.save()

        order, created = Order.objects.get_or_create(

            buyer=payment.buyer,

            seller=payment.gig.seller,

            gig=payment.gig,

            defaults={

                "amount": payment.amount,

                "status": "Pending"

            }

        )

        # Link payment to order
        payment.order = order
        payment.save(update_fields=["order"])

        if created:

            create_notification(

                user=order.seller,

                title="New Order Received",

                message=f"{order.buyer.username} placed an order for '{order.gig.title}'.",

                link=f"/orders/{order.id}/"

            )

    elif payment_status == "FAILED":

        payment.status = "FAILED"

        payment.save()

    return HttpResponse(status=200)



@login_required
def payment_history(request):

    if request.user.is_seller:

        payments = Payment.objects.filter(
            gig__seller=request.user,
            status="SUCCESS"
        ).select_related(
            "buyer",
            "gig",
            "order"
        )

        total_earnings = payments.aggregate(
            total=Sum("amount")
        )["total"] or 0

        context = {

            "payments": payments,

            "total_earnings": total_earnings,

            "is_seller": True,

        }

    else:

        payments = Payment.objects.filter(
            buyer=request.user,
            status="SUCCESS"
        ).select_related(
            "gig",
            "gig__seller",
            "order"
        )

        total_spent = payments.aggregate(
            total=Sum("amount")
        )["total"] or 0

        context = {

            "payments": payments,

            "total_spent": total_spent,

            "is_seller": False,

        }

    return render(
        request,
        "payments/payment_history.html",
        context
    )


@login_required
def download_invoice(request, payment_id):

    payment = get_object_or_404(
        Payment.objects.select_related(
            "buyer",
            "gig",
            "gig__seller",
            "order"
        ),
        id=payment_id,
        status="SUCCESS"
    )

    if payment.buyer != request.user:
        return HttpResponse(
            "Unauthorized",
            status=403
        )

    invoice_pdf = generate_invoice_pdf(
        payment
    )

    response = HttpResponse(
        invoice_pdf,
        content_type="application/pdf"
    )

    response["Content-Disposition"] = (
        f'attachment; '
        f'filename="CertiHire_INV-'
        f'{payment.id:06d}.pdf"'
    )

    return response