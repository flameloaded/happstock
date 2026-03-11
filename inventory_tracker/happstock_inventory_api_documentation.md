

# Happstock Inventory – Business & Staff API Documentation

This document describes the **Business Management API** used to manage:

- Businesses
- Branches
- Staff
- Invitations
- Roles
- Permissions

This documentation is intended for **frontend developers integrating the Happstock Inventory backend.**

---

# Base API URL

```
http://127.0.0.1:8000/api/
```

Example:

```
http://127.0.0.1:8000/api/business/create/
```

---

# Authentication

All endpoints require authentication.

Example header:

```
Authorization: Bearer <access_token>
```

---

# Business Management

## 1. Create Business

Creates a new business.

The authenticated user automatically becomes the **Owner**.

### Endpoint

```
POST /api/business/create/
```

### Request Body

```json
{
  "name": "Happstock Supermarket"
}
```

### Response

```json
{
  "message": "Business created",
  "business_id": 1
}
```

---

## 2. Update Business

Updates the business name.

Only the **owner** can perform this action.

### Endpoint

```
PUT /api/business/{business_id}/update/
```

### Request Body

```json
{
  "name": "New Business Name"
}
```

### Response

```json
{
  "message": "Business updated",
  "name": "New Business Name"
}
```

---

## 3. Delete Business

Deletes a business.

Only the **owner** can delete a business.

### Endpoint

```
DELETE /api/business/{business_id}/delete/
```

### Response

```json
{
  "message": "Business deleted"
}
```

---

## 4. List My Businesses

Returns all businesses the user belongs to.

### Endpoint

```
GET /api/business/my/
```

### Response

```json
{
  "businesses": [
    {
      "business_id": 1,
      "business_name": "Happstock Supermarket",
      "role": "owner"
    }
  ]
}
```

---

# Branch Management

## 5. Create Branch

Creates a new branch under a business.

Only the **owner** can create branches.

### Endpoint

```
POST /api/business/{business_id}/branches/create/
```

### Request Body

```json
{
  "name": "Lekki Branch",
  "location": "Lekki Phase 1"
}
```

### Response

```json
{
  "message": "Branch created",
  "branch_id": 2
}
```

---

## 6. List Branches

Returns branches visible to the logged-in user.

### Endpoint

```
GET /api/business/{business_id}/branches/
```

### Behavior

| Role | Branch Access |
|-----|---------------|
| Owner | Sees all branches |
| Manager | Sees only assigned branch |
| Attendant | Sees only assigned branch |

### Response

```json
{
  "business": "Happstock Supermarket",
  "branches": [
    {
      "branch_id": 2,
      "name": "Lekki Branch",
      "location": "Lekki Phase 1",
      "created_at": "2026-03-09T12:00:00Z"
    }
  ]
}
```

---

# Staff Invitations

## 7. Invite Staff

Invites a user to join a business.

Only the **owner** can invite staff.

### Endpoint

```
POST /api/business/{business_id}/invite/
```

### Request Body

```json
{
  "email": "manager@gmail.com",
  "role": "manager",
  "branch_id": 2
}
```

### Response

```json
{
  "message": "Invitation sent successfully"
}
```

---

## 8. Accept Invitation

Allows invited users to join a business.

### Endpoint

```
POST /api/invitations/accept/{token}/
```

### Response

```json
{
  "message": "You joined the business",
  "business": "Happstock Supermarket",
  "branch": "Lekki Branch",
  "role": "manager"
}
```

---

# Staff Management

## 9. List Business Staff

Lists staff belonging to a business.

### Endpoint

```
GET /api/business/{business_id}/staff/
```

### Response

```json
{
  "business": "Happstock Supermarket",
  "staff": [
    {
      "user_id": 12,
      "name": "John Doe",
      "email": "john@gmail.com",
      "role": "manager",
      "branch": "Lekki Branch"
    }
  ]
}
```

---

## 10. Remove Staff

Removes staff from a business.

Only the **owner** can remove staff.

### Endpoint

```
DELETE /api/business/{business_id}/staff/{user_id}/remove/
```

### Response

```json
{
  "message": "Staff removed"
}
```

---

## 11. Update Staff Role

### Endpoint

```
POST /api/business/{business_id}/staff/{user_id}/role/
```

### Request Body

```json
{
  "role": "manager"
}
```

### Response

```json
{
  "message": "Role updated",
  "role": "manager"
}
```

---

## 12. Assign Staff to Branch

### Endpoint

```
POST /api/business/{business_id}/branches/{branch_id}/staff/
```

### Request Body

```json
{
  "user_id": 10
}
```

### Response

```json
{
  "message": "Staff assigned to branch",
  "branch": "Lekki Branch",
  "user_id": 10
}
```

---

## 13. Update Staff Permissions

### Endpoint

```
POST /api/business/{business_id}/staff/{user_id}/permissions/
```

### Example Request

```json
{
  "can_create_product": true,
  "can_delete_product": false,
  "can_view_sales": true,
  "can_manage_inventory": true,
  "can_scan_stock": true
}
```

### Response

```json
{
  "message": "Permissions updated"
}
```

---

## 14. List Managers

### Endpoint

```
GET /api/business/{business_id}/managers/
```

### Response

```json
{
  "business": "Happstock Supermarket",
  "managers": [
    {
      "user_id": 12,
      "name": "John Doe",
      "email": "john@gmail.com",
      "role": "manager",
      "branch": "Lekki Branch"
    }
  ]
}
```

---

# Role Hierarchy

```
Owner
│
├── Manager
│
└── Attendant
```

| Role | Responsibility |
|------|---------------|
| Owner | Full system control |
| Manager | Manage branch operations |
| Attendant | Sales and POS |

---

# Invitation Workflow

```
Owner invites staff
        ↓
Email invitation sent
        ↓
Staff clicks invitation link
        ↓
Accept invitation
        ↓
BusinessMembership created
        ↓
Branch assigned (if provided)
```

---

# Data Model Overview

```
User
 │
 ├── Business (Owner)
 │
 └── BusinessMembership
        │
        ├── Business
        ├── Branch
        ├── Role
        └── Permissions
```
