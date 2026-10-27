from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from .forms import RegisterForm
from django.contrib.auth.decorators import login_required
import random
from django.core.mail import send_mail
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.conf import settings
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash

def register_view(request):

    if request.method == "POST":

        form = RegisterForm(request.POST)

        if form.is_valid():

            user = form.save(commit=False)

            # Get selected role
            role = request.POST.get("role")

            if role == "seller":
                user.is_seller = True
            else:
                user.is_seller = False

            user.save()

            login(request, user)

            # Seller → assessment
            if user.is_seller:
                return redirect("login")

            # Buyer → dashboard
            return redirect("login")

        else:
            print(form.errors)

    else:
        form = RegisterForm()

    return render(
        request,
        "accounts/register.html",
        {
            "form": form
        }
    )

def login_view(request):

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user:

            login(request, user)


            # ==========================
            # SELLER FLOW
            # ==========================

            if user.is_seller:


                # 1. APPROVED
                if user.is_approved:

                    return redirect(
                        "dashboard"
                    )


                # 2. REJECTED BY ADMIN
                if user.assessment_rejected:

                    return redirect(
                        "assessment_failed"
                    )


                # 3. ASSESSMENT SUBMITTED
                if user.assessment_submitted:

                    return redirect(
                        "assessment_pending"
                    )


                # 4. NEW SELLER
                return redirect(
                    "assessment_required"
                )


            # ==========================
            # BUYER FLOW
            # ==========================

            return redirect(
                "dashboard"
            )


        return render(
            request,
            "accounts/login.html",
            {
                "error":
                "Invalid username or password"
            }
        )


    return render(
        request,
        "accounts/login.html"
    )
def logout_view(request):

    logout(request)
    
    messages.success(
        request,
        "You have been logged out successfully."
    )

    return redirect("login")

def assessment_required(request):
    return render(
        request,
        "accounts/assessment_required.html"
    )
    
def assessment_pending(request):

    if not request.user.is_authenticated:
        return redirect("login")

    return render(
        request,
        "accounts/assessment_pending.html"
    )
    
def forgot_password(request):

    if request.method == "POST":

        email = request.POST.get("email", "").strip()

        User = get_user_model()

        try:
            user = User.objects.get(
                email__iexact=email
            )
        except User.DoesNotExist:

            messages.error(
                request,
                "No account found with this email address."
            )

            return redirect("forgot_password")

        # Generate 6 digit OTP
        otp = str(
            random.randint(100000, 999999)
        )

        # Store temporarily in session
        request.session["reset_user_id"] = user.id
        request.session["reset_otp"] = otp

        # OTP expiry: 5 minutes
        request.session["reset_otp_time"] = (
            __import__("time").time()
        )

        send_mail(

            subject="CertiHire Password Reset OTP",

            message=f"""
Hi {user.username},

We received a request to reset your CertiHire password.

Your OTP is:

{otp}

This OTP is valid for 5 minutes.

If you did not request a password reset, you can safely ignore this email.

Regards,
Lithish Kumar
Founder / Administrator
CertiHire
""",

            from_email=settings.DEFAULT_FROM_EMAIL,

            recipient_list=[
                user.email
            ],

            fail_silently=False
        )

        return redirect(
            "verify_reset_otp"
        )

    return render(
        request,
        "accounts/forgot_password.html"
    )


def verify_reset_otp(request):

    if "reset_user_id" not in request.session:

        return redirect(
            "forgot_password"
        )

    if request.method == "POST":

        entered_otp = request.POST.get(
            "otp",
            ""
        ).strip()

        saved_otp = request.session.get(
            "reset_otp"
        )

        otp_time = request.session.get(
            "reset_otp_time"
        )

        # Check 5 minute expiry
        import time

        if (
            not otp_time
            or time.time() - otp_time > 300
        ):

            request.session.pop(
                "reset_otp",
                None
            )

            request.session.pop(
                "reset_otp_time",
                None
            )

            messages.error(
                request,
                "OTP has expired. Please request a new OTP."
            )

            return redirect(
                "forgot_password"
            )

        if entered_otp != saved_otp:

            messages.error(
                request,
                "Invalid OTP. Please try again."
            )

            return render(
                request,
                "accounts/verify_reset_otp.html"
            )

        # OTP verified
        request.session["reset_verified"] = True

        request.session.pop(
            "reset_otp",
            None
        )

        request.session.pop(
            "reset_otp_time",
            None
        )

        return redirect(
            "reset_password"
        )

    return render(
        request,
        "accounts/verify_reset_otp.html"
    )


def reset_password(request):

    if not request.session.get(
        "reset_verified"
    ):

        return redirect(
            "forgot_password"
        )

    if request.method == "POST":

        password1 = request.POST.get(
            "password1"
        )

        password2 = request.POST.get(
            "password2"
        )

        if not password1 or not password2:

            messages.error(
                request,
                "Please fill in both password fields."
            )

            return redirect(
                "reset_password"
            )

        if password1 != password2:

            messages.error(
                request,
                "Passwords do not match."
            )

            return redirect(
                "reset_password"
            )

        if len(password1) < 8:

            messages.error(
                request,
                "Password must contain at least 8 characters."
            )

            return redirect(
                "reset_password"
            )

        User = get_user_model()

        try:

            user = User.objects.get(
                id=request.session[
                    "reset_user_id"
                ]
            )

        except User.DoesNotExist:

            return redirect(
                "forgot_password"
            )

        user.set_password(password1)

        user.save()

        # Clear reset session
        request.session.pop(
            "reset_user_id",
            None
        )

        request.session.pop(
            "reset_verified",
            None
        )

        messages.success(
            request,
            "Your password has been reset successfully. You can now login."
        )

        # return redirect(
        #     "login"
        # )

    return render(
        request,
        "accounts/reset_password.html"
    )
    
    

@login_required
def password_change(request):

    if request.method == "POST":

        form = PasswordChangeForm(
            request.user,
            request.POST
        )

        if form.is_valid():

            user = form.save()

            # Keep the user logged in
            update_session_auth_hash(
                request,
                user
            )

            messages.success(
                request,
                "Your password has been changed successfully."
            )

            return redirect("settings")

    else:

        form = PasswordChangeForm(
            request.user
        )

    return render(
        request,
        "profiles/change_password.html",
        {
            "form": form
        }
    )