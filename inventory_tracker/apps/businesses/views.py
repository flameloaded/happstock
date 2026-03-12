from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import BusinessMembership, Business
from .permissions import is_owner, is_manager
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Business, BusinessMembership
from .models import BusinessInvitation
from apps.core.models import User
from sendgrid.helpers.mail import Mail
#from sendgrid import SendGridAPIClient
from django.template.loader import render_to_string
from happsaminventory import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Business, BusinessInvitation, Branch
from .permissions import is_owner
from django.urls import reverse



# Create a business
@permission_classes([IsAuthenticated])
@api_view(["POST"])
def create_business(request):

    name = request.data.get("name")

    if not name:
        return Response({"error": "Business name required"}, status=400)

    business = Business.objects.create(
        name=name,
        owner=request.user
    )

    # owner becomes a member automatically
    BusinessMembership.objects.create(
        user=request.user,
        business=business,
        role="owner"
    )

    return Response({
        "message": "Business created",
        "business_id": business.id
    }, status=status.HTTP_201_CREATED)


# Update Business
@permission_classes([IsAuthenticated])
@api_view(["PUT"])
def update_business(request, business_id):

    try:
        business = Business.objects.get(id=business_id)
    except Business.DoesNotExist:
        return Response({"error": "Business not found"}, status=404)

    # Only owner can update
    if not is_owner(request.user, business):
        return Response({"error": "Only owner can update business"}, status=403)

    name = request.data.get("name")

    if name:
        business.name = name
        business.save()

    return Response({
        "message": "Business updated",
        "name": business.name
    })


#Delete Business
@permission_classes([IsAuthenticated])
@api_view(["DELETE"])
def delete_business(request, business_id):

    try:
        business = Business.objects.get(id=business_id)
    except Business.DoesNotExist:
        return Response({"error": "Business not found"}, status=404)

    if not is_owner(request.user, business):
        return Response({"error": "Only owner can delete business"}, status=403)

    business.delete()

    return Response({
        "message": "Business deleted"
    })





# Create Branch

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_branch(request, business_id):

    try:
        business = Business.objects.get(id=business_id)
    except Business.DoesNotExist:
        return Response({"error": "Business not found"}, status=404)

    if not is_owner(request.user, business):
        return Response({"error": "Only owner can create branch"}, status=403)

    name = request.data.get("name")
    location = request.data.get("location")

    if not name or not location:
        return Response({"error": "Name and location required"}, status=400)

    branch = Branch.objects.create(
        business=business,
        name=name,
        location=location
    )

    return Response({
        "message": "Branch created",
        "branch_id": branch.id
    })


# Invite Staff



@api_view(["POST"])
@permission_classes([IsAuthenticated])
def invite_staff(request, business_id):

    # Check business exists
    try:
        business = Business.objects.get(id=business_id)
    except Business.DoesNotExist:
        return Response(
            {"error": "Business not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    # Only owner can invite
    if not is_owner(request.user, business):
        return Response(
            {"error": "Only the business owner can invite staff"},
            status=status.HTTP_403_FORBIDDEN
        )

    email = request.data.get("email")
    role = request.data.get("role")
    branch_id = request.data.get("branch_id")

    # Validate email
    if not email:
        return Response(
            {"error": "Email is required"},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Validate role
    if role not in ["manager", "attendant"]:
        return Response(
            {"error": "Role must be either 'manager' or 'attendant'"},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Validate branch if provided
    branch = None
    if branch_id:
        try:
            branch = Branch.objects.get(id=branch_id, business=business)
        except Branch.DoesNotExist:
            return Response(
                {"error": "Invalid branch"},
                status=status.HTTP_400_BAD_REQUEST
            )

    # Prevent duplicate invitations
    existing_invite = BusinessInvitation.objects.filter(
        email=email,
        business=business,
        accepted=False
    ).first()

    if existing_invite:
        return Response(
            {"error": "An invitation has already been sent to this email"},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Create invitation
    existing_invite = BusinessInvitation.objects.filter(
    email=email,
    business=business,
    accepted=False
    ).first()

    if existing_invite:
        invitation = existing_invite
    else:
        invitation = BusinessInvitation.objects.create(
            business=business,
            email=email,
            role=role,
            invited_by=request.user,
            branch=branch
        )

    invite_link = request.build_absolute_uri(
        reverse("accept_invitation", args=[invitation.token])
    )

    # Render email template
    html_content = render_to_string(
        "businesses/invite_email.html",
        {
            "invite_link": invite_link,
            "business": business,
            "role": role
        }
    )

    subject = "You've been invited to join a business"
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [email]

    # Send email
    try:
        email_message = EmailMultiAlternatives(
            subject,
            "You have been invited to join a business.",
            from_email,
            recipient_list
        )

        email_message.attach_alternative(html_content, "text/html")
        email_message.send()

    except Exception as e:
        print("Email sending failed:", str(e))

        return Response(
            {
                "message": "Invitation created but email could not be sent",
                "invite_link": invite_link
            },
            status=status.HTTP_201_CREATED
        )

    return Response(
        {
            "message": "Invitation sent successfully",
            "email": email
        },
        status=status.HTTP_201_CREATED
    )


# Accept invitation

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def accept_invitation(request, token):

    try:
        invitation = BusinessInvitation.objects.get(token=token, accepted=False)
    except BusinessInvitation.DoesNotExist:
        return Response({"error": "Invalid invitation"}, status=404)


    if invitation.is_expired():
        return Response({"error": "Invitation expired"}, status=400)

    user = request.user
    if user.email.strip().lower() != invitation.email.strip().lower():
        return Response(
            {"error": "This invitation was sent to another email"},
            status=403
        )
    
    
    BusinessMembership.objects.create(
        user=user,
        business=invitation.business,
        role=invitation.role,
        branch=invitation.branch
    )


    invitation.accepted = True
    invitation.save()

    return Response({
        "message": "You joined the business",
        "business": invitation.business.name,
        "branch": invitation.branch.name if invitation.branch else None,
        "role": invitation.role
    })



# Remove Staff

@permission_classes([IsAuthenticated])
@api_view(["DELETE"])
def remove_staff(request, business_id, user_id):

    try:
        business = Business.objects.get(id=business_id)
    except Business.DoesNotExist:
        return Response({"error": "Business not found"}, status=404)

    if not is_owner(request.user, business):
        return Response({"error": "Only owner can remove staff"}, status=403)

    try:
        membership = BusinessMembership.objects.get(
            business=business,
            user_id=user_id
        )
    except BusinessMembership.DoesNotExist:
        return Response({"error": "Staff not found"}, status=404)

    if membership.role == "owner":
        return Response({"error": "Cannot remove owner"}, status=400)

    membership.delete()

    return Response({
        "message": "Staff removed"
    })



# Update Staff Role

@permission_classes([IsAuthenticated])
@api_view(["POST"])
def update_staff_role(request, business_id, user_id):

    try:
        business = Business.objects.get(id=business_id)
    except Business.DoesNotExist:
        return Response({"error": "Business not found"}, status=404)

    if not is_owner(request.user, business):
        return Response({"error": "Only owner can change roles"}, status=403)

    role = request.data.get("role")

    if role not in ["manager", "attendant"]:
        return Response({"error": "Invalid role"}, status=400)

    try:
        membership = BusinessMembership.objects.get(
            business=business,
            user_id=user_id
        )
    except BusinessMembership.DoesNotExist:
        return Response({"error": "Staff not found"}, status=404)

    membership.role = role
    membership.save()

    return Response({
        "message": "Role updated",
        "role": membership.role
    })

# list branches

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def list_branches(request, business_id):

    try:
        business = Business.objects.get(id=business_id)
    except Business.DoesNotExist:
        return Response({"error": "Business not found"}, status=404)

    # Get membership instead of using exists()
    membership = BusinessMembership.objects.filter(
        user=request.user,
        business=business
    ).first()

    if not membership:
        return Response({"error": "You are not part of this business"}, status=403)

    # Owner sees all branches
    if membership.role == "owner":
        branches = Branch.objects.filter(business=business)

    # Manager & Attendant see only their branch
    else:
        branches = Branch.objects.filter(
            business=business,
            id=membership.branch.id if membership.branch else None
        )

    data = []

    for branch in branches:
        data.append({
            "branch_id": branch.id,
            "name": branch.name,
            "location": branch.location,
            "created_at": branch.created_at
        })

    return Response({
        "business": business.name,
        "branches": data
    })


# list business staff

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def list_business_staff(request, business_id):

    try:
        business = Business.objects.get(id=business_id)
    except Business.DoesNotExist:
        return Response({"error": "Business not found"}, status=404)

    # Get membership instead of exists()
    membership = BusinessMembership.objects.filter(
        user=request.user,
        business=business
    ).first()

    if not membership:
        return Response({"error": "Not part of this business"}, status=403)

    # Block attendants
    if membership.role == "attendant":
        return Response(
            {"error": "Only owners and managers can view staff"},
            status=403
        )

    # Exclude logged-in user
    staff = BusinessMembership.objects.filter(
        business=business
    ).exclude(
        user=request.user
    ).select_related("user", "branch")

    data = []

    for s in staff:
        data.append({
            "user_id": s.user.id,
            "name": f"{s.user.first_name} {s.user.last_name}".strip(),
            "email": s.user.email,
            "role": s.role,
            "branch": s.branch.name if s.branch else None
        })

    return Response({
        "business": business.name,
        "staff": data
    })


# Assign staff branch
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def assign_staff_branch(request, business_id, branch_id):

    try:
        business = Business.objects.get(id=business_id)
    except Business.DoesNotExist:
        return Response({"error": "Business not found"}, status=404)

    if not is_owner(request.user, business):
        return Response({"error": "Only owner can assign staff"}, status=403)

    try:
        branch = Branch.objects.get(id=branch_id, business=business)
    except Branch.DoesNotExist:
        return Response({"error": "Branch not found"}, status=404)

    user_id = request.data.get("user_id")

    if not user_id:
        return Response({"error": "user_id is required"}, status=400)

    try:
        membership = BusinessMembership.objects.get(
            user_id=user_id,
            business=business
        )
    except BusinessMembership.DoesNotExist:
        return Response({"error": "User is not part of this business"}, status=404)

    membership.branch = branch
    membership.save()

    return Response({
        "message": "Staff assigned to branch",
        "branch": branch.name,
        "user_id": membership.user.id
    })



# Update Staff Permissions
@permission_classes([IsAuthenticated])
@api_view(["POST"])
def update_staff_permissions(request, business_id, user_id):

    try:
        business = Business.objects.get(id=business_id)
    except Business.DoesNotExist:
        return Response({"error": "Business not found"}, status=404)

    # person making the request
    requester_membership = BusinessMembership.objects.filter(
        user=request.user,
        business=business
    ).first()

    if not requester_membership:
        return Response({"error": "Not part of this business"}, status=403)

    try:
        target_membership = BusinessMembership.objects.get(
            user_id=user_id,
            business=business
        )
    except BusinessMembership.DoesNotExist:
        return Response({"error": "Staff not found"}, status=404)

    # OWNER RULES
    if requester_membership.role == "owner":

        if target_membership.role == "owner":
            return Response({"error": "Cannot modify owner"}, status=403)

        allowed_permissions = [
            "can_create_product",
            "can_delete_product",
            "can_view_sales",
            "can_manage_staff",
            "can_manage_inventory",
            "can_scan_stock"
        ]

    # MANAGER RULES
    elif requester_membership.role == "manager":

        # manager cannot modify owner or other managers
        if target_membership.role in ["owner", "manager"]:
            return Response({"error": "Managers can only modify attendants"}, status=403)

        allowed_permissions = [
            "can_create_product",
            "can_delete_product",
            "can_view_sales",
            "can_manage_inventory",
            "can_scan_stock"
        ]

    else:
        return Response({"error": "Permission denied"}, status=403)

    for field in allowed_permissions:
        value = request.data.get(field)
        if value is not None:
            setattr(target_membership, field, value)

    target_membership.save()

    return Response({
        "message": "Permissions updated"
    })


# List Manager
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def list_managers(request, business_id):

    try:
        business = Business.objects.get(id=business_id)
    except Business.DoesNotExist:
        return Response({"error": "Business not found"}, status=404)

    membership = BusinessMembership.objects.filter(
        user=request.user,
        business=business
    ).first()

    if not membership:
        return Response({"error": "Not part of this business"}, status=403)

    # Only owner allowed
    if membership.role != "owner":
        return Response({"error": "Only the owner can view managers"}, status=403)

    managers = BusinessMembership.objects.filter(
        business=business,
        role="manager"
    ).select_related("user")

    data = []

    for m in managers:
        data.append({
            "user_id": m.user.id,
            "name": f"{m.user.first_name} {m.user.last_name}".strip(),
            "email": m.user.email,
            "role": m.role,
            "branch": m.branch.name if m.branch else None
        })

    return Response({
        "business": business.name,
        "managers": data
    })

# List my business

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def list_my_businesses(request):

    memberships = BusinessMembership.objects.filter(
        user=request.user
    ).select_related("business")

    data = []

    for m in memberships:
        data.append({
            "business_id": m.business.id,
            "business_name": m.business.name,
            "role": m.role
        })

    return Response({
        "businesses": data
    })