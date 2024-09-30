import json
import sys
import prance
import requests
from langchain_core.messages import HumanMessage
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI


def analyze_spec(spec):
    global_consumes = spec.get('consumes', ['application/json'])
    operations = []
    for path, path_item in spec['paths'].items():
        for method, operation in path_item.items():
            if method in ['get', 'post', 'put', 'delete', 'patch']:
                # Use operation-level 'consumes' if available, otherwise use global 'consumes'
                consumes = operation.get('consumes', global_consumes)
                operations.append({
                    'path': path,
                    'method': method,
                    'operation_id': operation.get('operationId', f"{method}_{path}"),
                    'parameters': operation.get('parameters', []),
                    'requestBody': operation.get('requestBody', {}),
                    'responses': operation.get('responses', {}),
                    'consumes': consumes
                })
    return operations


def generate_test_case(operation):
    operation_string = json.dumps(operation)
    prompt_text = f"""
    Generate API test cases for this operation in JSON format:
    {operation_string}

    Strictly adhere to the following format for each test case:
    {{
      "test_name": "Descriptive name for the test case",
      "request": {{
        "method": "HTTP method",
        "path": "API endpoint path",
        "headers": {{"header_name": "header_value"}},
        "body": {{"key": "value"}}
      }},
      "expected_response": {{
        "status_code": 200,
        "body": {{"key": "expected value"}}
      }}
    }}

    Generate an array of at least 3 test cases. Do not include any text outside the JSON array.
    """

    model = ChatOpenAI(model="gpt-4o-mini")
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an API testing expert. Generate test cases in JSON format without any additional text."),
        MessagesPlaceholder("msgs")
    ])

    output_parser = JsonOutputParser()
    chain = prompt | model | output_parser

    try:
        test_cases = chain.invoke({"msgs": [HumanMessage(content=prompt_text)]})

        # Ensure the output is a list of test cases
        if not isinstance(test_cases, list):
            test_cases = [test_cases]

        # Validate and clean each test case
        validated_test_cases = []
        for case in test_cases:
            if all(key in case for key in ['test_name', 'request', 'expected_response']):
                validated_test_cases.append(case)

        return validated_test_cases
    except json.JSONDecodeError:
        print("Error: Generated content is not valid JSON")
        return []


def run_test_case(base_url, test_case, operation):
    request = test_case['request']
    url = f"{base_url}{request['path']}"
    method = request['method'].lower()
    headers = request.get('headers', {})
    body = request.get('body')

    # Ensure the correct Content-Type is set based on the operation's 'consumes'
    if 'Content-Type' not in headers and operation['consumes']:
        headers['Content-Type'] = operation['consumes'][0]

    try:
        if headers.get('Content-Type') == 'application/x-www-form-urlencoded':
            response = requests.request(method, url, headers=headers, data=body)
        else:
            response = requests.request(method, url, headers=headers, json=body)

        actual_status = response.status_code
        actual_body = response.json() if response.text else None

        expected_status = test_case['expected_response']['status_code']
        expected_body = test_case['expected_response'].get('body')

        result = {
            'test_name': test_case['test_name'],
            'passed': actual_status == expected_status,
            'expected_status': expected_status,
            'actual_status': actual_status,
            'expected_body': expected_body,
            'actual_body': actual_body
        }

        return result

    except Exception as e:
        return {
            'test_name': test_case['test_name'],
            'passed': False,
            'error': str(e)
        }


def main():
    openapi_spec_file = sys.argv[1]
    base_url = sys.argv[2]
    openapi_spec = prance.ResolvingParser(openapi_spec_file).specification
    operations = analyze_spec(openapi_spec)

    all_test_cases = []
    operation_map = {}  # Map to store operation details for each test case

    for operation in operations:
        print(f"Generating test cases for: {operation['method']} {operation['path']}")
        test_cases = generate_test_case(operation)
        for test_case in test_cases:
            all_test_cases.append(test_case)
            operation_map[test_case['test_name']] = operation  # Store operation for each test case

    # Save all test cases to a JSON file
    with open('results/archieved/test_cases.json', 'w') as f:
        json.dump(all_test_cases, f, indent=4)

    print(f"Generated {len(all_test_cases)} test cases. Saved to test_cases.json")

    # Run the test cases
    test_results = []
    for test_case in all_test_cases:
        print(f"Running test case: {test_case['test_name']}")
        operation = operation_map[test_case['test_name']]
        result = run_test_case(base_url, test_case, operation)
        test_results.append(result)
        if not result['passed']:
            print(f"Test failed: {result['test_name']}")
            print(f"Expected status: {result.get('expected_status')}")
            print(f"Actual status: {result.get('actual_status')}")
            if 'error' in result:
                print(f"Error: {result['error']}")
        print("---")

    # Save test results
    with open('results/archieved/test_results.json', 'w') as f:
        json.dump(test_results, f, indent=4)

    print(f"Test results saved to test_results.json. Total tests run: {len(test_results)}")

if __name__ == "__main__":
    main()
