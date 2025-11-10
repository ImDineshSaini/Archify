# API Error Contract Documentation

This document defines all error responses in the Archify API. All errors follow a consistent JSON structure with error codes, HTTP status codes, and detailed messages.

## Error Response Format

All error responses follow this structure:

```json
{
  "error": {
    "code": "ERR_DOMAIN_XXX",
    "message": "Human-readable error message",
    "details": {
      "additional": "context-specific information"
    }
  }
}
```

## HTTP Status Codes

| Status Code | Meaning | When Used |
|------------|---------|-----------|
| 400 | Bad Request | Invalid input format or validation error |
| 401 | Unauthorized | Missing or invalid authentication credentials |
| 403 | Forbidden | Valid credentials but insufficient permissions |
| 404 | Not Found | Resource doesn't exist |
| 409 | Conflict | Resource already exists (duplicate) |
| 422 | Unprocessable Entity | Validation error with specific field issues |
| 500 | Internal Server Error | Database or infrastructure errors |
| 502 | Bad Gateway | External service (GitHub, LLM) errors |

## Error Codes Reference

### Authentication Errors (ERR_AUTH_XXX)

#### ERR_AUTH_001: Invalid Credentials
**HTTP Status**: 401 Unauthorized

**When**: Login with wrong username or password

**Example**:
```json
{
  "error": {
    "code": "ERR_AUTH_001",
    "message": "Invalid username or password",
    "details": {
      "username": "john_doe"
    }
  }
}
```

**How to Handle**:
- Display "Invalid credentials" message to user
- Don't reveal whether username or password was wrong (security)
- Suggest password reset if available

---

#### ERR_AUTH_002: Invalid Token
**HTTP Status**: 401 Unauthorized

**When**: JWT token is expired, malformed, or invalid

**Example**:
```json
{
  "error": {
    "code": "ERR_AUTH_002",
    "message": "Invalid or expired token",
    "details": {}
  }
}
```

**How to Handle**:
- Clear stored token
- Redirect to login page
- Show "Session expired, please login again" message

---

#### ERR_AUTH_003: Insufficient Permissions
**HTTP Status**: 403 Forbidden

**When**: User authenticated but lacks required permission

**Example**:
```json
{
  "error": {
    "code": "ERR_AUTH_003",
    "message": "Insufficient permissions. Required: admin",
    "details": {
      "required_permission": "admin"
    }
  }
}
```

**How to Handle**:
- Show "You don't have permission to perform this action"
- Contact admin or upgrade plan if applicable

---

### User Errors (ERR_USER_XXX)

#### ERR_USER_001: User Not Found
**HTTP Status**: 404 Not Found

**When**: Requested user doesn't exist in database

**Example**:
```json
{
  "error": {
    "code": "ERR_USER_001",
    "message": "User not found: john_doe",
    "details": {
      "identifier": "john_doe"
    }
  }
}
```

**How to Handle**:
- Show "User not found" message
- Verify username spelling
- Suggest user registration if applicable

---

#### ERR_USER_002: User Already Exists
**HTTP Status**: 409 Conflict

**When**: Attempting to register with existing username or email

**Examples**:

Username conflict:
```json
{
  "error": {
    "code": "ERR_USER_002",
    "message": "User with username 'john_doe' already exists",
    "details": {
      "field": "username",
      "value": "john_doe"
    }
  }
}
```

Email conflict:
```json
{
  "error": {
    "code": "ERR_USER_002",
    "message": "User with email 'john@example.com' already exists",
    "details": {
      "field": "email",
      "value": "john@example.com"
    }
  }
}
```

**How to Handle**:
- Display field-specific error message
- Suggest login instead of registration
- Offer password reset if email exists

---

#### ERR_USER_003: User Inactive
**HTTP Status**: 403 Forbidden

**When**: User account is deactivated or suspended

**Example**:
```json
{
  "error": {
    "code": "ERR_USER_003",
    "message": "User account is inactive: john_doe",
    "details": {
      "username": "john_doe"
    }
  }
}
```

**How to Handle**:
- Show "Your account has been deactivated"
- Provide contact support information
- Don't allow login even with correct credentials

---

### Tenant Errors (ERR_TENANT_XXX)

#### ERR_TENANT_001: Tenant Not Found
**HTTP Status**: 404 Not Found

**When**: Requested tenant/organization doesn't exist

**Example**:
```json
{
  "error": {
    "code": "ERR_TENANT_001",
    "message": "Tenant not found: acme-corp",
    "details": {
      "identifier": "acme-corp"
    }
  }
}
```

**How to Handle**:
- Show "Organization not found" message
- Verify organization slug
- Redirect to organization selection page

---

#### ERR_TENANT_002: Tenant Already Exists
**HTTP Status**: 409 Conflict

**When**: Creating tenant with duplicate slug

**Example**:
```json
{
  "error": {
    "code": "ERR_TENANT_002",
    "message": "Tenant with slug 'acme-corp' already exists",
    "details": {
      "slug": "acme-corp"
    }
  }
}
```

**How to Handle**:
- Display "Organization name already taken"
- Suggest alternative slug
- Show available similar slugs

---

#### ERR_TENANT_003: Tenant Inactive
**HTTP Status**: 403 Forbidden

**When**: Tenant is suspended or deactivated

**Example**:
```json
{
  "error": {
    "code": "ERR_TENANT_003",
    "message": "Tenant is inactive: acme-corp",
    "details": {
      "slug": "acme-corp"
    }
  }
}
```

**How to Handle**:
- Show "Organization is suspended"
- Contact billing or support
- Don't allow access to tenant resources

---

### Repository Errors (ERR_REPO_XXX)

#### ERR_REPO_001: Repository Not Found
**HTTP Status**: 404 Not Found

**When**: Requested repository doesn't exist

**Example**:
```json
{
  "error": {
    "code": "ERR_REPO_001",
    "message": "Repository not found: 123",
    "details": {
      "repository_id": 123
    }
  }
}
```

**How to Handle**:
- Show "Repository not found"
- Return to repository list
- Suggest re-adding repository

---

#### ERR_REPO_002: Access Denied
**HTTP Status**: 403 Forbidden

**When**: User doesn't have access to repository

**Example**:
```json
{
  "error": {
    "code": "ERR_REPO_002",
    "message": "Access denied to repository: 123",
    "details": {
      "repository_id": 123
    }
  }
}
```

**How to Handle**:
- Show "You don't have access to this repository"
- Request access from owner
- Verify user is in correct organization

---

### Analysis Errors (ERR_ANALYSIS_XXX)

#### ERR_ANALYSIS_001: Analysis Not Found
**HTTP Status**: 404 Not Found

**When**: Requested analysis doesn't exist

**Example**:
```json
{
  "error": {
    "code": "ERR_ANALYSIS_001",
    "message": "Analysis not found: 456",
    "details": {
      "analysis_id": 456
    }
  }
}
```

**How to Handle**:
- Show "Analysis not found"
- Return to analysis list
- Suggest running new analysis

---

#### ERR_ANALYSIS_002: Analysis Failed
**HTTP Status**: 500 Internal Server Error

**When**: Analysis execution failed due to code scanning or LLM errors

**Example**:
```json
{
  "error": {
    "code": "ERR_ANALYSIS_002",
    "message": "Analysis failed: Unable to clone repository",
    "details": {
      "reason": "Unable to clone repository"
    }
  }
}
```

**How to Handle**:
- Show specific failure reason
- Retry analysis if transient error
- Check repository access permissions

---

### Validation Errors (ERR_VALIDATION_XXX)

#### ERR_VALIDATION_001: Validation Error
**HTTP Status**: 422 Unprocessable Entity

**When**: Pydantic validation fails on request body

**Example**:
```json
{
  "error": {
    "code": "ERR_VALIDATION_001",
    "message": "Validation error",
    "details": {
      "validation_errors": [
        {
          "field": "email",
          "message": "value is not a valid email address",
          "type": "value_error.email"
        },
        {
          "field": "password",
          "message": "ensure this value has at least 8 characters",
          "type": "value_error.any_str.min_length"
        }
      ]
    }
  }
}
```

**How to Handle**:
- Display field-specific error messages
- Highlight invalid fields in form
- Show validation requirements

---

### Infrastructure Errors (ERR_DB_XXX, ERR_EXTERNAL_XXX)

#### ERR_DB_001: Database Error
**HTTP Status**: 500 Internal Server Error

**When**: Database connection or query failure

**Example**:
```json
{
  "error": {
    "code": "ERR_DB_001",
    "message": "Database error: Connection timeout",
    "details": {}
  }
}
```

**How to Handle**:
- Show "Service temporarily unavailable"
- Retry after brief delay
- Contact support if persists

---

#### ERR_EXTERNAL_001: External Service Error
**HTTP Status**: 502 Bad Gateway

**When**: GitHub API, LLM API, or other external service fails

**Example**:
```json
{
  "error": {
    "code": "ERR_EXTERNAL_001",
    "message": "GitHub error: API rate limit exceeded",
    "details": {
      "service": "GitHub"
    }
  }
}
```

**How to Handle**:
- Show "External service unavailable"
- Wait for rate limit reset if applicable
- Retry later or contact support

---

## Common Error Scenarios by Endpoint

### POST /api/v2/auth/login

| Scenario | Status | Error Code | Message |
|----------|--------|------------|---------|
| Wrong password | 401 | ERR_AUTH_001 | Invalid username or password |
| User doesn't exist | 401 | ERR_AUTH_001 | Invalid username or password |
| Account inactive | 403 | ERR_USER_003 | User account is inactive: {username} |
| Invalid JSON | 422 | ERR_VALIDATION_001 | Validation error |
| Database down | 500 | ERR_DB_001 | Database error: {details} |

**Example Success Response** (200):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user_id": 1,
  "username": "john_doe"
}
```

---

### POST /api/v2/auth/register

| Scenario | Status | Error Code | Message |
|----------|--------|------------|---------|
| Username exists | 409 | ERR_USER_002 | User with username '{username}' already exists |
| Email exists | 409 | ERR_USER_002 | User with email '{email}' already exists |
| Invalid email format | 422 | ERR_VALIDATION_001 | Validation error |
| Password too short | 422 | ERR_VALIDATION_001 | Validation error |
| Database error | 500 | ERR_DB_001 | Database error: {details} |

**Example Success Response** (201):
```json
{
  "user_id": 1,
  "username": "john_doe",
  "email": "john@example.com",
  "message": "User registered successfully"
}
```

---

### GET /api/repositories/{repository_id}

| Scenario | Status | Error Code | Message |
|----------|--------|------------|---------|
| Not authenticated | 401 | ERR_AUTH_002 | Invalid or expired token |
| Repository not found | 404 | ERR_REPO_001 | Repository not found: {repo_id} |
| Access denied | 403 | ERR_REPO_002 | Access denied to repository: {repo_id} |
| Invalid repo ID | 422 | ERR_VALIDATION_001 | Validation error |

---

### POST /api/analyses

| Scenario | Status | Error Code | Message |
|----------|--------|------------|---------|
| Not authenticated | 401 | ERR_AUTH_002 | Invalid or expired token |
| Repository not found | 404 | ERR_REPO_001 | Repository not found: {repo_id} |
| GitHub API error | 502 | ERR_EXTERNAL_001 | GitHub error: {details} |
| LLM API error | 502 | ERR_EXTERNAL_001 | OpenAI error: {details} |
| Analysis failed | 500 | ERR_ANALYSIS_002 | Analysis failed: {reason} |

---

## Client Implementation Guide

### JavaScript/TypeScript Example

```typescript
interface ApiError {
  error: {
    code: string;
    message: string;
    details: Record<string, any>;
  };
}

async function login(username: string, password: string) {
  try {
    const response = await fetch('/api/v2/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password })
    });

    if (!response.ok) {
      const error: ApiError = await response.json();

      switch (error.error.code) {
        case 'ERR_AUTH_001':
          throw new Error('Invalid credentials');
        case 'ERR_USER_003':
          throw new Error('Account is inactive. Contact support.');
        case 'ERR_VALIDATION_001':
          throw new Error('Please check your input');
        default:
          throw new Error(error.error.message);
      }
    }

    return await response.json();
  } catch (err) {
    console.error('Login failed:', err);
    throw err;
  }
}
```

### Python Client Example

```python
import requests
from typing import Dict, Any

class ArchifyAPIError(Exception):
    def __init__(self, code: str, message: str, details: Dict[str, Any]):
        self.code = code
        self.message = message
        self.details = details
        super().__init__(self.message)

def login(username: str, password: str) -> Dict[str, Any]:
    response = requests.post(
        'http://localhost:8000/api/v2/auth/login',
        json={'username': username, 'password': password}
    )

    if not response.ok:
        error_data = response.json()['error']
        raise ArchifyAPIError(
            code=error_data['code'],
            message=error_data['message'],
            details=error_data['details']
        )

    return response.json()

try:
    result = login('john_doe', 'password123')
    print(f"Logged in as {result['username']}")
except ArchifyAPIError as e:
    if e.code == 'ERR_AUTH_001':
        print("Invalid credentials")
    elif e.code == 'ERR_USER_003':
        print(f"Account inactive: {e.details.get('username')}")
    else:
        print(f"Error: {e.message}")
```

---

## Testing Error Responses

### Using cURL

```bash
# Test invalid credentials
curl -X POST http://localhost:8000/api/v2/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"invalid","password":"wrong"}' \
  -v

# Expected: 401 with ERR_AUTH_001

# Test validation error
curl -X POST http://localhost:8000/api/v2/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"test","email":"invalid-email","password":"123"}' \
  -v

# Expected: 422 with ERR_VALIDATION_001

# Test expired token
curl -X GET http://localhost:8000/api/repositories \
  -H "Authorization: Bearer expired.token.here" \
  -v

# Expected: 401 with ERR_AUTH_002
```

---

## Error Handling Best Practices

### For Frontend Developers

1. **Always check HTTP status code first**
   ```typescript
   if (!response.ok) {
     // Handle error
   }
   ```

2. **Parse error code for specific handling**
   ```typescript
   const { error } = await response.json();
   switch (error.code) {
     case 'ERR_AUTH_001': // specific handling
     case 'ERR_AUTH_002': // specific handling
     default: // generic handling
   }
   ```

3. **Display user-friendly messages**
   - Don't show raw error codes to users
   - Map error codes to localized messages
   - Provide actionable suggestions

4. **Log errors for debugging**
   ```typescript
   console.error('API Error:', {
     code: error.code,
     message: error.message,
     details: error.details,
     endpoint: request.url
   });
   ```

5. **Handle network errors separately**
   ```typescript
   try {
     const response = await fetch(url);
   } catch (networkError) {
     // Handle network/CORS/timeout errors
     console.error('Network error:', networkError);
   }
   ```

### For Backend Developers

1. **Always use custom exceptions**
   ```python
   # DON'T
   raise HTTPException(status_code=404, detail="Not found")

   # DO
   raise UserNotFoundError(username)
   ```

2. **Include context in details**
   ```python
   raise InvalidCredentialsError(details={
       "username": username,
       "timestamp": datetime.now().isoformat(),
       "ip_address": request.client.host
   })
   ```

3. **Log errors before raising**
   ```python
   logger.error("authentication_failed",
                username=username,
                error_code="ERR_AUTH_001")
   raise InvalidCredentialsError()
   ```

4. **Never expose sensitive information**
   ```python
   # DON'T
   raise Exception(f"Database password incorrect: {password}")

   # DO
   raise DatabaseException("Connection failed")
   ```

---

## Monitoring and Alerting

### Error Metrics to Track

1. **Error Rate by Code**
   - Track frequency of each error code
   - Alert on unusual spikes
   - Example: ERR_AUTH_001 spike = potential brute force attack

2. **Error Rate by Endpoint**
   - Identify problematic endpoints
   - Monitor error percentage (errors/total requests)
   - Target: <1% error rate for most endpoints

3. **Response Time for Errors**
   - Errors should be fast (no slow timeouts)
   - Target: <100ms for authentication errors

4. **5xx Errors**
   - ERR_DB_001, ERR_EXTERNAL_001, ERR_ANALYSIS_002
   - Should be rare (<0.1%)
   - Require immediate investigation

### Example Logging Query (Structured Logs)

```python
# Find all authentication failures in last hour
SELECT * FROM logs
WHERE error_code = 'ERR_AUTH_001'
  AND timestamp > NOW() - INTERVAL '1 hour'
ORDER BY timestamp DESC;

# Find users with most failed logins
SELECT
  details->>'username' as username,
  COUNT(*) as failed_attempts
FROM logs
WHERE error_code = 'ERR_AUTH_001'
  AND timestamp > NOW() - INTERVAL '1 day'
GROUP BY details->>'username'
HAVING COUNT(*) > 5
ORDER BY failed_attempts DESC;
```

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2024-01-XX | Initial error contract documentation |

## Related Documentation

- [API Reference](./API_REFERENCE.md)
- [Architecture Overview](./ARCHITECTURE_REVIEW.md)
- [Logging Guide](./app/core/logging_config.py)
- [Exception Hierarchy](./app/core/exceptions.py)
