import os
import requests
import yaml
import ollama
import json
import time


# Load the YAML OpenAPI specification file
def load_openapi_spec(file_path):
    with open(file_path, "r") as file:
        return yaml.safe_load(file)


# Generate an API test case using the LLM and the OpenAPI spec, with optional previous response feedback
def generate_api_test(operations, previous_response=None):
    prompt = f"""
    Generate a REST API test case based on the following OpenAPI specification and previous API response.
    OpenAPI Spec: {json.dumps(operations)}
    Previous Response: {previous_response}
    The goal is to maximize code coverage and test for different status codes.
    """

    response = ollama.generate(model="deepseek-coder-v2", prompt=prompt)

    return json.loads(response["content"])


# Execute the generated API test and return the response
def execute_api_test(api_test):
    # Print the generated test case details
    print(f"\nExecuting API Test:")
    print(f"Method: {api_test['method']}")
    print(f"Endpoint: {base_url}/{api_test['endpoint']}")

    if 'headers' in api_test:
        print(f"Headers: {json.dumps(api_test['headers'], indent=2)}")

    if 'body' in api_test:
        print(f"Body: {json.dumps(api_test['body'], indent=2)}")

    # Send the request
    response = requests.request(
        method=api_test['method'],
        url=f"{base_url}/{api_test['endpoint']}",
        headers=api_test.get('headers', {}),
        json=api_test.get('body', {})
    )

    # Print the response details
    print(f"\nResponse Status Code: {response.status_code}")
    print(f"Response Body: {response.text}")

    return response


# Use the response to refine the next API test case
def evaluate_and_provide_feedback(response, previous_test):
    feedback = {
        'status_code': response.status_code,
        'body': response.json() if response.headers.get('Content-Type') == 'application/json' else response.text
    }

    prompt = f"""
    Based on the feedback from the previous test and the OpenAPI spec, generate a refined test case.
    Feedback: {json.dumps(feedback)}
    Previous Test: {json.dumps(previous_test)}
    Focus on covering more code and testing different status codes.
    """

    response = ollama.generate(model="deepseek-coder-v2", prompt=prompt)

    return json.loads(response["content"])


# Main loop to generate, execute, and refine tests until a time limit is reached
def main():
    openapi_spec = load_openapi_spec("../spec/market.yaml")  # Load your OpenAPI spec file
    operations = openapi_spec.get('paths', {})

    start_time = time.time()
    time_limit = 3600  # 1 hour time limit

    previous_response = None
    iteration = 0

    while time.time() - start_time < time_limit:
        print(f"\nIteration {iteration + 1}:")
        api_test = generate_api_test(operations, previous_response)
        response = execute_api_test(api_test)
        api_test = evaluate_and_provide_feedback(response, api_test)
        previous_response = response.json() if response.headers.get(
            'Content-Type') == 'application/json' else response.text
        iteration += 1


if __name__ == "__main__":
    # Ensure the base URL is set according to the API you're testing
    base_url = "http://localhost:8081"  # Replace with your actual API base URL
    main()
