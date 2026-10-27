import uuid
import requests

from django.conf import settings


# =========================================================
# CREATE CASHFREE ORDER
# =========================================================

def create_cashfree_order(request, gig):

    order_id = (
        f"CERTIHIRE_{uuid.uuid4().hex[:12]}"
    )

    payload = {

        "order_id": order_id,

        "order_amount": float(
            gig.price
        ),

        "order_currency": "INR",

        "customer_details": {

            "customer_id": str(
                request.user.id
            ),

            "customer_name": (
                request.user.username
            ),

            "customer_email": (
                request.user.email
            ),

            # Sandbox testing phone number
            "customer_phone": "9876543210",

        },

        "order_meta": {

            "return_url": (
                request.build_absolute_uri(
                    f"/payments/success/{order_id}/"
                )
            )

        }

    }


    headers = {

        "accept":
            "application/json",

        "content-type":
            "application/json",

        "x-client-id":
            settings.CASHFREE_CLIENT_ID,

        "x-client-secret":
            settings.CASHFREE_CLIENT_SECRET,

        # Current Cashfree API version
        "x-api-version":
            "2025-01-01",

    }


    url = (
        f"{settings.CASHFREE_BASE_URL}"
        "/orders"
    )


    try:

        response = requests.post(

            url,

            json=payload,

            headers=headers,

            timeout=30

        )

        print("===================================")
        print("CASHFREE CREATE ORDER")
        print("STATUS:", response.status_code)
        print("RESPONSE:", response.text)
        print("===================================")


        response.raise_for_status()

        return response.json()


    except requests.RequestException as e:

        print("===================================")
        print("CASHFREE CREATE ORDER ERROR")
        print(repr(e))
        print("===================================")

        return {
            "error": str(e)
        }


# =========================================================
# VERIFY CASHFREE PAYMENT
# =========================================================

def verify_cashfree_payment(order_id):

    headers = {

        "accept":
            "application/json",

        "x-client-id":
            settings.CASHFREE_CLIENT_ID,

        "x-client-secret":
            settings.CASHFREE_CLIENT_SECRET,

        "x-api-version":
            "2025-01-01",

    }


    url = (
        f"{settings.CASHFREE_BASE_URL}"
        f"/orders/{order_id}/payments"
    )


    try:

        response = requests.get(

            url,

            headers=headers,

            timeout=30

        )


        print("===================================")
        print("CASHFREE PAYMENT VERIFICATION")
        print("STATUS:", response.status_code)
        print("RESPONSE:", response.text)
        print("===================================")


        response.raise_for_status()

        payments = response.json()


        # Cashfree returns a list of transactions
        if not isinstance(
            payments,
            list
        ):

            return {
                "payment_status":
                    "FAILED",

                "payments":
                    payments
            }


        # ---------------------------------------------
        # SUCCESS
        # ---------------------------------------------

        for payment in payments:

            if (
                payment.get(
                    "payment_status"
                )
                == "SUCCESS"
            ):

                return {

                    "payment_status":
                        "SUCCESS",

                    "payment":
                        payment,

                    "payments":
                        payments

                }


        # ---------------------------------------------
        # PENDING
        # ---------------------------------------------

        for payment in payments:

            if (
                payment.get(
                    "payment_status"
                )
                == "PENDING"
            ):

                return {

                    "payment_status":
                        "PENDING",

                    "payment":
                        payment,

                    "payments":
                        payments

                }


        # ---------------------------------------------
        # FAILED
        # ---------------------------------------------

        return {

            "payment_status":
                "FAILED",

            "payments":
                payments

        }


    except requests.RequestException as e:

        print("===================================")
        print("CASHFREE VERIFICATION ERROR")
        print(repr(e))
        print("===================================")

        return {

            "payment_status":
                "FAILED",

            "error":
                str(e)

        }