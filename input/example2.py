
def get_example_spec():
    return """
{
    "path": "/users",
    "method": "get",
    "operation_id": "listUsers",
    "parameters": [
        {
            "name": "limit",
            "in": "query",
            "schema": {
                "type": "integer",
                "default": 20
            }
        }
    ],
    "requestBody": {},
    "responses": {
        "200": {
            "description": "Successful response",
            "content": {
                "application/json": {
                    "schema": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "id": {
                                    "type": "integer"
                                },
                                "username": {
                                    "type": "string"
                                },
                                "email": {
                                    "type": "string"
                                },
                                "createdAt": {
                                    "type": "string",
                                    "format": "date-time"
                                }
                            }
                        }
                    }
                }
            }
        }
    }
},
{
    "path": "/users",
    "method": "post",
    "operation_id": "createUser",
    "parameters": [],
    "requestBody": {
        "required": true,
        "content": {
            "application/json": {
                "schema": {
                    "type": "object",
                    "required": [
                        "username",
                        "email"
                    ],
                    "properties": {
                        "username": {
                            "type": "string"
                        },
                        "email": {
                            "type": "string"
                        }
                    }
                }
            }
        }
    },
    "responses": {
        "201": {
            "description": "User created successfully",
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "id": {
                                "type": "integer"
                            },
                            "username": {
                                "type": "string"
                            },
                            "email": {
                                "type": "string"
                            },
                            "createdAt": {
                                "type": "string",
                                "format": "date-time"
                            }
                        }
                    }
                }
            }
        },
        "400": {
            "description": "Invalid input"
        }
    }
},
{
    "path": "/users/{userId}",
    "method": "get",
    "operation_id": "getUser",
    "parameters": [
        {
            "name": "userId",
            "in": "path",
            "required": true,
            "schema": {
                "type": "integer"
            }
        }
    ],
    "requestBody": {},
    "responses": {
        "200": {
            "description": "Successful response",
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "id": {
                                "type": "integer"
                            },
                            "username": {
                                "type": "string"
                            },
                            "email": {
                                "type": "string"
                            },
                            "createdAt": {
                                "type": "string",
                                "format": "date-time"
                            }
                        }
                    }
                }
            }
        },
        "404": {
            "description": "User not found"
        }
    }
},
{
    "path": "/users/{userId}",
    "method": "put",
    "operation_id": "updateUser",
    "parameters": [
        {
            "name": "userId",
            "in": "path",
            "required": true,
            "schema": {
                "type": "integer"
            }
        }
    ],
    "requestBody": {
        "required": true,
        "content": {
            "application/json": {
                "schema": {
                    "type": "object",
                    "required": [
                        "username",
                        "email"
                    ],
                    "properties": {
                        "username": {
                            "type": "string"
                        },
                        "email": {
                            "type": "string"
                        }
                    }
                }
            }
        }
    },
    "responses": {
        "200": {
            "description": "User updated successfully",
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "id": {
                                "type": "integer"
                            },
                            "username": {
                                "type": "string"
                            },
                            "email": {
                                "type": "string"
                            },
                            "createdAt": {
                                "type": "string",
                                "format": "date-time"
                            }
                        }
                    }
                }
            }
        },
        "400": {
            "description": "Invalid input"
        },
        "404": {
            "description": "User not found"
        }
    }
},
{
    "path": "/users/{userId}",
    "method": "delete",
    "operation_id": "deleteUser",
    "parameters": [
        {
            "name": "userId",
            "in": "path",
            "required": true,
            "schema": {
                "type": "integer"
            }
        }
    ],
    "requestBody": {},
    "responses": {
        "204": {
            "description": "User deleted successfully"
        },
        "404": {
            "description": "User not found"
        }
    }
}
"""

def get_example_test_cases():
    return """
[
  {
    "name": "List Users - Default Limit",
    "method": "GET",
    "path": "/users",
    "expected_status": 200,
    "expected_response": {
      "type": "array",
      "minItems": 1,
      "maxItems": 20,
      "items": {
        "type": "object",
        "required": ["id", "username", "email", "createdAt"]
      }
    }
  },
  {
    "name": "Create User - Valid Input",
    "method": "POST",
    "path": "/users",
    "headers": {"Content-Type": "application/json"},
    "data": {
      "username": "newuser",
      "email": "newuser@example.com"
    },
    "expected_status": 201,
    "expected_response": {
      "type": "object",
      "required": ["id", "username", "email", "createdAt"],
      "properties": {
        "username": {"const": "newuser"},
        "email": {"const": "newuser@example.com"}
      }
    }
  },
  {
    "name": "Get User - Existing User",
    "method": "GET",
    "path": "/users/{userId}",
    "params": {"userId": 1},
    "expected_status": 200,
    "expected_response": {
      "type": "object",
      "required": ["id", "username", "email", "createdAt"],
      "properties": {
        "id": {"const": 1}
      }
    }
  },
  {
    "name": "Update User - Valid Input",
    "method": "PUT",
    "path": "/users/{userId}",
    "params": {"userId": 1},
    "headers": {"Content-Type": "application/json"},
    "data": {
      "username": "updateduser",
      "email": "updated@example.com"
    },
    "expected_status": 200,
    "expected_response": {
      "type": "object",
      "required": ["id", "username", "email", "createdAt"],
      "properties": {
        "id": {"const": 1},
        "username": {"const": "updateduser"},
        "email": {"const": "updated@example.com"}
      }
    }
  },
  {
    "name": "Delete User - Existing User",
    "method": "DELETE",
    "path": "/users/{userId}",
    "params": {"userId": 1},
    "expected_status": 204
  }
]
"""


examples = [
    {
        "input": get_example_spec(),
        "output": get_example_test_cases()
    }
]
