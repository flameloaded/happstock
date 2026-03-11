from .models import BusinessMembership


def get_membership(user, business):
    return BusinessMembership.objects.filter(
        user=user,
        business=business
    ).first()


def is_owner(user, business):
    membership = get_membership(user, business)
    return membership and membership.role == "owner"


def is_manager(user, business):
    membership = get_membership(user, business)
    return membership and membership.role == "manager"


# ------------------------
# PRODUCT PERMISSIONS
# ------------------------

def can_create_product(user, business):

    membership = get_membership(user, business)

    if not membership:
        return False

    if membership.role in ["owner", "manager"]:
        return True

    return membership.can_create_product


def can_delete_product(user, business):

    membership = get_membership(user, business)

    if not membership:
        return False

    if membership.role == "owner":
        return True

    return membership.can_delete_product


# ------------------------
# SALES PERMISSIONS
# ------------------------

def can_view_sales(user, business):

    membership = get_membership(user, business)

    if not membership:
        return False

    if membership.role in ["owner", "manager"]:
        return True

    return membership.can_view_sales


# ------------------------
# STAFF MANAGEMENT
# ------------------------

def can_manage_staff(user, business):

    membership = get_membership(user, business)

    if not membership:
        return False

    if membership.role == "owner":
        return True

    return membership.can_manage_staff