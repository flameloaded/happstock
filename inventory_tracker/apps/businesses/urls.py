from django.urls import path
from . import views


urlpatterns = [

    # ===============================
    # BRANCH
    # ===============================

    path(
        "business/<int:business_id>/branches/",
        views.list_branches,
        name="list_branches"
    ),

    # Assign Staff
    path(
        "business/<int:business_id>/branches/<int:branch_id>/staff/",
        views.assign_staff_branch,
        name="assign_staff_to_branch"
    ),
    # ===============================
    # BUSINESS
    # ===============================

    # Create Business
    path(
        "business/create/",
        views.create_business,
        name="create_business"
    ),

    # Update Business
    path(
        "business/<int:business_id>/update/",
        views.update_business,
        name="update_business"
    ),

    # Delete Business
    path(
        "business/<int:business_id>/delete/",
        views.delete_business,
        name="delete_business"
    ),

    # List businesses user belongs to
    path(
        "business/my/",
        views.list_my_businesses,
        name="my_businesses"
    ),

    # List Staff belonging to a business
    path(
        "business/<int:business_id>/staff/",
        views.list_business_staff,
        name="list_business_staff"
    ),


    # ===============================
    # BRANCH
    # ===============================

    # Create Branch
    path(
        "business/<int:business_id>/branches/create/",
        views.create_branch,
        name="create_branch"
    ),


    # ===============================
    # STAFF INVITATIONS
    # ===============================

    # Invite staff
    path(
        "business/<int:business_id>/invite/",
        views.invite_staff,
        name="invite_staff"
    ),

    # Accept invitation
    path(
        "invitations/accept/<uuid:token>/",
        views.accept_invitation,
        name="accept_invitation"
    ),


    # ===============================
    # STAFF MANAGEMENT
    # ===============================

    # Remove staff
    path(
        "business/<int:business_id>/staff/<int:user_id>/remove/",
        views.remove_staff,
        name="remove_staff"
    ),

    # Update staff role
    path(
        "business/<int:business_id>/staff/<int:user_id>/role/",
        views.update_staff_role,
        name="update_staff_role"
    ),

    # Update staff permissions
    path(
        "business/<int:business_id>/staff/<int:user_id>/permissions/",
        views.update_staff_permissions,
        name="update_staff_permissions"
    ),


    # ===============================
    # STAFF LISTING
    # ===============================

    # List managers
    path(
        "business/<int:business_id>/managers/",
        views.list_managers,
        name="list_managers"
    ),

]