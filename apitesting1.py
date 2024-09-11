import prance
import requests
import json
import random
import string
from langchain.prompts import PromptTemplate, FewShotPromptTemplate
from langchain_openai import OpenAI
from langchain.chains import LLMChain
from input.example1 import examples


def generate_example_value(schema):
    if schema.get('type') == 'string':
        return ''.join(random.choices(string.ascii_letters, k=10))
    elif schema.get('type') == 'integer':
        return random.randint(1, 100)
    elif schema.get('type') == 'number':
        return round(random.uniform(1, 100), 2)
    elif schema.get('type') == 'boolean':
        return random.choice([True, False])
    elif schema.get('type') == 'array':
        return [generate_example_value(schema['items']) for _ in range(2)]
    elif schema.get('type') == 'object':
        return {k: generate_example_value(v) for k, v in schema.get('properties', {}).items()}
    return None

# Create a prompt template
example_template = """
Endpoint: {endpoint}
Method: {method}
Details: {details}
Parameters: {parameters}
Body: {body}

Test Cases:
{test_cases}
"""

example_prompt = PromptTemplate(
    input_variables=["endpoint", "method", "details", "parameters", "body", "test_cases"],
    template=example_template
)

# Create the few-shot prompt template
few_shot_prompt = FewShotPromptTemplate(
    examples=examples,
    example_prompt=example_prompt,
    prefix="Generate test cases for the following REST API endpoint:",
    suffix="Endpoint: {endpoint}\nMethod: {method}\nDetails: {details}\nParameters: {parameters}\nBody: {body}\n\nTest Cases:",
    input_variables=["endpoint", "method", "details", "parameters", "body"],
    example_separator="\n\n"
)


def generate_test_cases(llm_chain, path, method, operation, openapi_spec):
    parameters = operation.get('parameters', [])
    request_body = operation.get('requestBody', {}).get('content', {}).get('application/json', {}).get('schema', {})

    # Generate example values for parameters
    path_params = {p['name']: generate_example_value(p['schema']) for p in parameters if p['in'] == 'path'}
    query_params = {p['name']: generate_example_value(p['schema']) for p in parameters if p['in'] == 'query'}

    # Generate example request body
    example_body = generate_example_value(request_body) if request_body else None

    return llm_chain.run(
        endpoint=path,
        method=method,
        details=operation.get('summary', ''),
        parameters=json.dumps(parameters),
        body=json.dumps(request_body)
    )


def parse_test_cases(test_cases_str):
    test_cases = []
    current_test = {}
    for line in test_cases_str.split('\n'):
        line = line.strip()
        if line.startswith("Test case:"):
            if current_test:
                test_cases.append(current_test)
            current_test = {'name': line.split("Test case:")[1].strip()}
        elif line.startswith("Request:"):
            current_test['request'] = line.split("Request:")[1].strip()
        elif line.startswith("Expected:"):
            current_test['expected'] = line.split("Expected:")[1].strip()
        elif line.startswith("Assertions:"):
            current_test['assertions'] = line.split("Assertions:")[1].strip()
    if current_test:
        test_cases.append(current_test)
    return test_cases


def send_request(base_url, request_details):
    method, endpoint = request_details.split(' ', 1)
    url = base_url + endpoint.split(' ')[0]

    headers = {}
    body = None

    # Extract headers
    if "Headers:" in request_details:
        headers_str = request_details.split("Headers:")[1].split("Body:")[0]
        headers = dict(header.split(': ') for header in headers_str.strip().split(', '))

    # Extract body
    if "Body:" in request_details:
        body_str = request_details.split("Body:")[1].strip()
        body = json.loads(body_str)

    print(f"Sending request: {method} {url}")
    print(f"Headers: {headers}")
    if body:
        print(f"Body: {json.dumps(body, indent=2)}")

    response = requests.request(method, url, headers=headers, json=body)

    print(f"Response status: {response.status_code}")
    print(f"Response body: {response.text}\n")

    return response


def run_test(base_url, test_case):
    print(f"Running test: {test_case['name']}")
    response = send_request(base_url, test_case['request'])

    expected_status = int(test_case['expected'].split()[0])
    if response.status_code == expected_status:
        print("Status code matched")
    else:
        print(f"Status code mismatch. Expected: {expected_status}, Got: {response.status_code}")

    # Here you could add more detailed assertions based on the 'assertions' field
    # This would require parsing the assertions string and implementing each check

    print("Test completed\n")


def main():
    base_url = "http://localhost:8081"
    openapi_spec_file = "spec/market.yaml"
    openapi_spec = prance.ResolvingParser(openapi_spec_file).specification

    llm = OpenAI(model_name="gpt-4o-mini", temperature=0.7)
    llm_chain = LLMChain(llm=llm, prompt=few_shot_prompt)

    for path, path_item in openapi_spec['paths'].items():
        for method, operation in path_item.items():
            print(f"Generating and running tests for {method.upper()} {path}")

            test_cases_str = generate_test_cases(llm_chain, path, method.upper(), operation, openapi_spec)
            test_cases = parse_test_cases(test_cases_str)

            for test_case in test_cases:
                run_test(base_url, test_case)

            print("\n" + "=" * 50 + "\n")


if __name__ == "__main__":
    main()
