import json
from accounts.models import User
import csv
import io
import zipfile
import random
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from .models import Question

# =========================================================
# SELLER ASSESSMENT
# =========================================================

@login_required
def assessment_view(request):

    user = request.user


    # Not a seller
    if not user.is_seller:

        return redirect("dashboard")


    # Already approved
    if user.is_approved:

        return redirect("dashboard")


    # Admin rejected seller
    if user.assessment_rejected:

        return redirect("assessment_failed")


    # Already submitted
    if user.assessment_submitted:

        return redirect("assessment_pending")


    # -------------------------------------------------
    # GET - START ASSESSMENT
    # -------------------------------------------------

    if request.method == "GET":

        total_questions = Question.objects.count()

        # Need at least 50 questions
        if total_questions < 50:

            messages.error(
                request,
                "The assessment is not available yet. "
                "The company must add at least 50 questions."
            )

            return redirect(
                "assessment_required"
            )


        # Randomly select 50 questions
        question_ids = list(
            Question.objects
            .order_by("?")
            .values_list("id", flat=True)[:50]
        )


        # Store selected questions in session
        request.session[
            "assessment_question_ids"
        ] = question_ids


        questions = Question.objects.filter(
            id__in=question_ids
        )


        # Preserve random order
        question_map = {
            q.id: q
            for q in questions
        }

        questions = [
            question_map[qid]
            for qid in question_ids
            if qid in question_map
        ]


        return render(
            request,
            "assessment/assessment.html",
            {
                "questions": questions,
            }
        )


    # -------------------------------------------------
    # POST - SUBMIT ASSESSMENT
    # -------------------------------------------------

    if request.method == "POST":

        question_ids = request.session.get(
            "assessment_question_ids"
        )


        if not question_ids:

            messages.error(
                request,
                "Assessment session expired. Please start again."
            )

            return redirect(
                "assessment_required"
            )


        questions = Question.objects.filter(
            id__in=question_ids
        )


        question_map = {
            q.id: q
            for q in questions
        }


        # Keep same order used during GET
        questions = [
            question_map[qid]
            for qid in question_ids
            if qid in question_map
        ]


        score = 0

        total_questions = len(questions)


        for question in questions:

            selected_answer = request.POST.get(
                str(question.id)
            )


            if (
                selected_answer
                == question.correct_answer
            ):

                score += 1


        # Calculate percentage

        if total_questions > 0:

            percentage = (
                score / total_questions
            ) * 100

        else:

            percentage = 0


        user.assessment_score = score

        user.assessment_percentage = int(
            percentage
        )


        # Real assessment:
        # 35 / 50 required

        user.assessment_passed = (
            score >= 35
        )


        # Mark submitted

        user.assessment_submitted = True


        # New submission is not rejected

        user.assessment_rejected = False


        user.save(
            update_fields=[
                "assessment_score",
                "assessment_percentage",
                "assessment_passed",
                "assessment_submitted",
                "assessment_rejected",
            ]
        )


        # Remove selected questions
        # from session

        request.session.pop(
            "assessment_question_ids",
            None
        )


        # Seller always goes to pending

        return redirect(
            "assessment_pending"
        )

@staff_member_required
def upload_questions_zip(request):

    if request.method != "POST":

        return redirect(
            "assessment_management"
        )


    uploaded_file = request.FILES.get(
        "questions_zip"
    )


    if not uploaded_file:

        messages.error(
            request,
            "Please select a ZIP file."
        )

        return redirect(
            "assessment_management"
        )


    # Check extension

    if not uploaded_file.name.lower().endswith(
        ".zip"
    ):

        messages.error(
            request,
            "Please upload a ZIP file."
        )

        return redirect(
            "assessment_management"
        )


    try:

        with zipfile.ZipFile(
            uploaded_file,
            "r"
        ) as zip_file:


            csv_files = [
                name
                for name in zip_file.namelist()
                if name.lower().endswith(".csv")
            ]


            if not csv_files:

                messages.error(
                    request,
                    "ZIP file must contain a CSV file."
                )

                return redirect(
                    "assessment_management"
                )


            total_added = 0


            for csv_name in csv_files:

                # Prevent unsafe paths
                if (
                    csv_name.startswith("/")
                    or ".." in csv_name.split("/")
                ):

                    messages.error(
                        request,
                        "Invalid file path inside ZIP."
                    )

                    return redirect(
                        "assessment_management"
                    )


                csv_data = zip_file.read(
                    csv_name
                )


                try:

                    csv_text = csv_data.decode(
                        "utf-8-sig"
                    )

                except UnicodeDecodeError:

                    messages.error(
                        request,
                        f"{csv_name} must be UTF-8 encoded."
                    )

                    return redirect(
                        "assessment_management"
                    )


                reader = csv.DictReader(
                    io.StringIO(csv_text)
                )


                required_columns = {
                    "question",
                    "option_a",
                    "option_b",
                    "option_c",
                    "option_d",
                    "correct_answer",
                }


                if not required_columns.issubset(
                    set(reader.fieldnames or [])
                ):

                    messages.error(
                        request,
                        f"{csv_name} has invalid columns."
                    )

                    return redirect(
                        "assessment_management"
                    )


                for row_number, row in enumerate(
                    reader,
                    start=2
                ):

                    question_text = (
                        row.get("question") or ""
                    ).strip()


                    option_a = (
                        row.get("option_a") or ""
                    ).strip()


                    option_b = (
                        row.get("option_b") or ""
                    ).strip()


                    option_c = (
                        row.get("option_c") or ""
                    ).strip()


                    option_d = (
                        row.get("option_d") or ""
                    ).strip()


                    correct_answer = (
                        row.get("correct_answer") or ""
                    ).strip().upper()


                    if not all([
                        question_text,
                        option_a,
                        option_b,
                        option_c,
                        option_d,
                        correct_answer,
                    ]):

                        messages.warning(
                            request,
                            f"Skipped row {row_number} "
                            f"in {csv_name}: empty field."
                        )

                        continue


                    if correct_answer not in [
                        "A",
                        "B",
                        "C",
                        "D",
                    ]:

                        messages.warning(
                            request,
                            f"Skipped row {row_number} "
                            f"in {csv_name}: "
                            f"invalid correct answer."
                        )

                        continue


                    Question.objects.create(

                        question=question_text,

                        option_a=option_a,

                        option_b=option_b,

                        option_c=option_c,

                        option_d=option_d,

                        correct_answer=correct_answer,

                    )


                    total_added += 1


        messages.success(
            request,
            f"{total_added} questions imported successfully."
        )


    except zipfile.BadZipFile:

        messages.error(
            request,
            "The uploaded file is not a valid ZIP file."
        )


    except Exception as e:

        messages.error(
            request,
            f"Could not import questions: {str(e)}"
        )


    return redirect(
        "assessment_management"
    )
# =========================================================
# MALPRACTICE WARNING
# =========================================================

@login_required
def assessment_malpractice(request):

    if request.method != "POST":

        return JsonResponse(
            {
                "error": "Invalid request"
            },
            status=405
        )


    user = request.user


    # Only sellers taking assessment
    if not user.is_seller:

        return JsonResponse(
            {
                "error": "Not eligible"
            },
            status=403
        )


    # Already disqualified
    if user.seller_disqualified:

        return JsonResponse(
            {
                "status": "terminated"
            }
        )


    try:

        data = json.loads(
            request.body
        )

        reason = data.get(
            "reason",
            "Assessment malpractice"
        )

    except json.JSONDecodeError:

        reason = "Assessment malpractice"


    # Add one warning
    user.malpractice_warnings += 1


    # -----------------------------------------------------
    # THIRD WARNING = DISQUALIFICATION
    # -----------------------------------------------------

    if user.malpractice_warnings > 2:

        user.seller_disqualified = True

        user.is_seller = False

        user.assessment_passed = False

        user.is_approved = False


        user.save(
            update_fields=[
                "malpractice_warnings",
                "seller_disqualified",
                "is_seller",
                "assessment_passed",
                "is_approved",
            ]
        )


        return JsonResponse(
            {
                "status": "terminated",
                "reason": reason,
            }
        )


    user.save(
        update_fields=[
            "malpractice_warnings"
        ]
    )


    return JsonResponse(
        {
            "status": "warning",

            "warnings":
                user.malpractice_warnings,

            "remaining":
                2 - user.malpractice_warnings,
        }
    )


# =========================================================
# TERMINATE ASSESSMENT
# =========================================================

@login_required
def terminate_assessment(request):

    if request.method != "POST":

        return JsonResponse(
            {
                "error": "Invalid request"
            },
            status=405
        )


    user = request.user


    if not user.is_seller:

        return JsonResponse(
            {
                "error": "Not eligible"
            },
            status=403
        )


    user.seller_disqualified = True

    user.is_seller = False

    user.assessment_passed = False

    user.is_approved = False


    user.save(
        update_fields=[
            "seller_disqualified",
            "is_seller",
            "assessment_passed",
            "is_approved",
        ]
    )


    return JsonResponse(
        {
            "status": "terminated"
        }
    )


# =========================================================
# DISQUALIFIED PAGE
# =========================================================

@login_required
def assessment_disqualified(request):

    return render(
        request,
        "assessment/disqualified.html"
    )


# =========================================================
# FAILED ASSESSMENT PAGE
# =========================================================

@login_required
def assessment_failed(request):

    return render(
        request,
        "assessment/assessment_failed.html"
    )


# =========================================================
# ADMIN - ASSESSMENT MANAGEMENT
# =========================================================

@staff_member_required
def assessment_management(request):

    questions = Question.objects.all().order_by("id")

    total_questions = questions.count()

    return render(
        request,
        "adminpanel/assessment.html",
        {
            "questions": questions,
            "total_questions": total_questions,
        }
    )

# =========================================================
# ADMIN - DELETE QUESTION
# =========================================================

@staff_member_required
def delete_question(request, pk):

    question = get_object_or_404(
        Question,
        pk=pk
    )


    question.delete()


    messages.success(
        request,
        "Question deleted successfully."
    )


    return redirect(
        "assessment_management"
    )


# =========================================================
# ADMIN - ADD QUESTION
# =========================================================

@staff_member_required
def add_question(request):

    if request.method == "POST":

        question = request.POST.get(
            "question"
        )

        option_a = request.POST.get(
            "option_a"
        )

        option_b = request.POST.get(
            "option_b"
        )

        option_c = request.POST.get(
            "option_c"
        )

        option_d = request.POST.get(
            "option_d"
        )

        correct_answer = request.POST.get(
            "correct_answer"
        )


        if not all([
            question,
            option_a,
            option_b,
            option_c,
            option_d,
            correct_answer
        ]):

            messages.error(
                request,
                "Please fill in all fields."
            )

            return redirect(
                "add_question"
            )


        Question.objects.create(

            question=question,

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


        return redirect(
            "assessment_management"
        )


    return render(
        request,
        "adminpanel/add_question.html"
    )


# =========================================================
# ADMIN - EDIT QUESTION
# =========================================================

@staff_member_required
def edit_question(request, pk):

    question = get_object_or_404(
        Question,
        pk=pk
    )


    if request.method == "POST":

        question.question = request.POST.get(
            "question"
        )

        question.option_a = request.POST.get(
            "option_a"
        )

        question.option_b = request.POST.get(
            "option_b"
        )

        question.option_c = request.POST.get(
            "option_c"
        )

        question.option_d = request.POST.get(
            "option_d"
        )

        question.correct_answer = request.POST.get(
            "correct_answer"
        )


        question.save()


        messages.success(
            request,
            "Question updated successfully."
        )


        return redirect(
            "assessment_management"
        )


    return render(
        request,
        "adminpanel/edit_question.html",
        {
            "question": question,
        }
    )

@staff_member_required
def approve_seller(request, pk):

    seller = get_object_or_404(
        User,
        pk=pk,
        is_seller=True
    )

    seller.is_approved = True
    seller.assessment_rejected = False

    seller.save(
        update_fields=[
            "is_approved",
            "assessment_rejected",
        ]
    )


    # ==============================
    # APPROVAL EMAIL
    # ==============================

    subject = (
        "Your CertiHire Seller Application "
        "Has Been Approved"
    )


    context = {
        "username": seller.username,
        "dashboard_url": (
            request.build_absolute_uri(
                "/dashboard/"
            )
        ),
    }


    html_message = render_to_string(
        "emails/seller_approved.html",
        context
    )


    email = EmailMultiAlternatives(

        subject=subject,

        body=(
            f"Hi {seller.username},\n\n"
            "Your CertiHire seller application "
            "has been approved."
        ),

        from_email=settings.DEFAULT_FROM_EMAIL,

        to=[seller.email],

    )


    email.attach_alternative(
        html_message,
        "text/html"
    )


    try:

        email.send(fail_silently=False)

        messages.success(
            request,
            f"{seller.username} approved and email sent."
        )

    except Exception as e:

        messages.warning(
            request,
            f"{seller.username} approved, "
            f"but email could not be sent."
        )

        print("Approval email error:", e)


    return redirect(
        "manage_users"
    )

@staff_member_required
def reject_seller(request, pk):

    seller = get_object_or_404(
        User,
        pk=pk,
        is_seller=True
    )


    seller.is_approved = False

    seller.assessment_rejected = True

    seller.save(
        update_fields=[
            "is_approved",
            "assessment_rejected",
        ]
    )


    # ==============================
    # REJECTION EMAIL
    # ==============================

    subject = (
        "Update on Your CertiHire "
        "Seller Application"
    )


    context = {
        "username": seller.username,
    }


    html_message = render_to_string(
        "emails/seller_rejected.html",
        context
    )


    email = EmailMultiAlternatives(

        subject=subject,

        body=(
            f"Hi {seller.username},\n\n"
            "Your CertiHire seller application "
            "has not been approved at this time."
        ),

        from_email=settings.DEFAULT_FROM_EMAIL,

        to=[seller.email],

    )


    email.attach_alternative(
        html_message,
        "text/html"
    )


    try:

        email.send(fail_silently=False)

        messages.success(
            request,
            f"{seller.username} rejected and email sent."
        )

    except Exception as e:

        messages.warning(
            request,
            f"{seller.username} rejected, "
            f"but email could not be sent."
        )

        print("Rejection email error:", e)


    return redirect(
        "manage_users"
    )