examples = [
    {
        "endpoint": "/api/users",
        "method": "GET",
        "details": "Retrieve a list of users. Supports pagination.",
        "parameters": {"page": "integer", "limit": "integer"},
        "test_cases": """
1. Happy Path - Retrieve users successfully
   - Request: GET /api/users?page=1&limit=10
   - Expected: 200 OK, List of user objects
   - Assert: Response is a JSON array of 10 users, each object has id, name, email

2. Pagination - Retrieve second page of users
   - Request: GET /api/users?page=2&limit=20
   - Expected: 200 OK, List of user objects
   - Assert: Response contains 20 users, has correct page info

3. Error Case - Invalid pagination parameters
   - Request: GET /api/users?page=-1&limit=1000
   - Expected: 400 Bad Request
   - Assert: Error message indicates invalid page parameter
"""
    },
    {
        "endpoint": "/api/users",
        "method": "POST",
        "details": "Create a new user.",
        "body": {
            "name": "string",
            "email": "string",
            "age": "integer"
        },
        "test_cases": """
1. Happy Path - Create user successfully
   - Request: POST /api/users
     Body: {"name": "John Doe", "email": "john@example.com", "age": 30}
   - Expected: 201 Created, New user object
   - Assert: Response contains created user data, including a new ID

2. Validation Error - Missing required field
   - Request: POST /api/users
     Body: {"name": "John Doe", "age": 30}
   - Expected: 400 Bad Request
   - Assert: Error message indicates missing required field (email)

3. Validation Error - Invalid email format
   - Request: POST /api/users
     Body: {"name": "John Doe", "email": "not-an-email", "age": 30}
   - Expected: 400 Bad Request
   - Assert: Error message indicates invalid email format
"""
    },
    {
        "endpoint": "/api/users/{id}",
        "method": "PUT",
        "details": "Update all fields of an existing user.",
        "parameters": {"id": "integer"},
        "body": {
            "name": "string",
            "email": "string",
            "age": "integer"
        },
        "test_cases": """
1. Happy Path - Update user successfully
   - Request: PUT /api/users/123
     Body: {"name": "John Smith", "email": "john.smith@example.com", "age": 31}
   - Expected: 200 OK, Updated user object
   - Assert: Response reflects all updated fields

2. Error Case - User not found
   - Request: PUT /api/users/999
     Body: {"name": "John Smith", "email": "john.smith@example.com", "age": 31}
   - Expected: 404 Not Found
   - Assert: Error message indicates user not found
"""
    }
]