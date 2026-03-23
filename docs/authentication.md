# Authentication

## Flow

```
1. POST /api/v1/auth/login  →  { access_token, refresh_token, token_type }
2. Use access_token in Authorization header: Bearer <token>
3. When expired, POST /api/v1/auth/refresh  →  new token pair
```

## JWT Configuration

| Setting                     | Default    | Description            |
| --------------------------- | ---------- | ---------------------- |
| JWT_ALGORITHM               | HS256      | Signing algorithm      |
| ACCESS_TOKEN_EXPIRE_MINUTES | 30         | Access token lifetime  |
| REFRESH_TOKEN_EXPIRE_DAYS   | 7          | Refresh token lifetime |
| SECRET_KEY                  | (required) | HMAC secret, 64+ chars |

## Roles

| Role         | Permissions                                                |
| ------------ | ---------------------------------------------------------- |
| `admin`      | Full access: register users, all CRUD, document generation |
| `secretaria` | All CRUD, document generation, email sending               |
| `docente`    | Read-only access to all entities                           |

## Registration

Only admin users can register new accounts:

```json
POST /api/v1/auth/register
Authorization: Bearer <admin_token>
{
    "email": "new@school.edu",
    "password": "SecurePass123!",
    "nombre": "María",
    "apellidos": "García López",
    "rol": "secretaria"
}
```

## Token Refresh

```json
POST /api/v1/auth/refresh
{
    "refresh_token": "<refresh_token_from_login>"
}
```

## Dependencies

Use in router handlers:

- `user: CurrentUser` — Any authenticated user
- `user: AdminUser` — Admin only
- `user: AdminOrSecretaria` — Admin or secretaria
