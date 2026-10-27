from django.urls import path

from . import views


urlpatterns = [

   

    path(
        "login/",
        views.admin_login,
        name="admin_login"
    ),
    path(
        "",
        views.admin_dashboard,
        name="admin_dashboard"
    ),
    path(
        "logout/",
        views.admin_logout,
        name="admin_logout"
    ),
    path(
        "users/",
        views.manage_users,
        name="manage_users"
    ),
    path(
        "sellers/<int:pk>/approve/",
        views.approve_seller,
        name="approve_seller"
    ),
    path(
        "assessments/",
        views.assessment_management,
        name="assessment_management"
    ),
    path(
        "assessments/add/",
        views.add_question,
        name="add_question"
    ),
    path(
        "assessments/edit/<int:pk>/",
        views.edit_question,
        name="edit_question"
    ),
    path(
        "assessments/delete/<int:pk>/",
        views.delete_question,
        name="delete_question"
    ),
  
    path(
        "gigs/",
        views.manage_gigs,
        name="manage_gigs"
    ),
    
    path(
        "orders/",
        views.manage_orders,
        name="manage_orders"
    ),
    path(
        "revenue/",
        views.revenue_management,
        name="revenue_management"
    ),
]