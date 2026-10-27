from django.urls import path

from .views import (
    assessment_view,
    assessment_management,
    delete_question,
    add_question,
    edit_question,
    assessment_malpractice,
    terminate_assessment,
    assessment_disqualified,
    upload_questions_zip,
    approve_seller,
    reject_seller,
    assessment_failed,
)


urlpatterns = [

    path(
        "",
        assessment_view,
        name="assessment"
    ),

    path(
        "admin/",
        assessment_management,
        name="assessment_management"
    ),

    path(
        "admin/delete/<int:pk>/",
        delete_question,
        name="delete_question"
    ),
    path(
        "admin/add/",
        add_question,
        name="add_question"
    ),
    path(
        "admin/edit/<int:pk>/",
        edit_question,
        name="edit_question"
    ),
    path(
        "malpractice/",
        assessment_malpractice,
        name="assessment_malpractice"
    ),

    path(
        "terminate/",
        terminate_assessment,
        name="terminate_assessment"
    ),

    path(
        "disqualified/",
        assessment_disqualified,
        name="assessment_disqualified"
    ),
    path(
        "admin/upload-questions/",
        upload_questions_zip,
        name="upload_questions_zip"
    ),
    path(
        "admin/sellers/<int:pk>/approve/",
        approve_seller,
        name="approve_seller"
    ),

    path(
        "admin/sellers/<int:pk>/reject/",
        reject_seller,
        name="reject_seller"
    ),
    path(
        "failed/",
        assessment_failed,
        name="assessment_failed"
    ),
]