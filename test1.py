import json
import prance
import requests
from langchain_core.messages import HumanMessage
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI


def analyze_spec(spec):
    operations = []
    for path, path_item in spec['paths'].items():
        for method, operation in path_item.items():
            if method in ['get', 'post', 'put', 'delete', 'patch']:
                operations.append({
                    'path': path,
                    'method': method,
                    'operation_id': operation.get('operationId', f"{method}_{path}"),
                    'parameters': operation.get('parameters', []),
                    'requestBody': operation.get('requestBody', {}),
                    'responses': operation.get('responses', {})
                })
    return operations


def generate_test_case(operation):
    operation_string = json.dumps(operation)

    prompt_text = f"""
    Here is the API operation data: {operation_string}
    Please generate API test cases for this operation in JSON format.
    No extra description before or after the json object should be added to the output.
    The JSON should include the following fields:
    - test_name: A descriptive name for the test case
    - request: An object containing 'method', 'path', 'headers', and 'body' (if applicable)
    - expected_response: An object containing 'status_code' and 'body' (sample expected response)
    """

    model = ChatOpenAI(model="gpt-4o-mini")
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an API testing expert. Generate test cases in JSON format."),
        MessagesPlaceholder("msgs")
    ])

    output_parser = JsonOutputParser()
    chain = prompt | model | output_parser

    test_case = chain.invoke({"msgs": [HumanMessage(content=prompt_text)]})
    return test_case


def run_test_case(base_url, test_case):
    request = test_case['request']
    url = f"{base_url}{request['path']}"
    method = request['method'].lower()
    headers = request.get('headers', {})
    body = request.get('body')

    try:
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
            'description': test_case['description'],
            'passed': False,
            'error': str(e)
        }


def main():
    openapi_spec_file = "spec/demo.yaml"
    base_url = "http://localhost:8081"
    openapi_spec = prance.ResolvingParser(openapi_spec_file).specification
    operations = analyze_spec(openapi_spec)

    # with open('operations.json', 'w') as f:
    #     json.dump(operations, f, indent=4)
    #
    # print("Operations saved to operations.json")

    all_test_cases = []
    for operation in operations:
        print(f"Generating test case for: {operation['method']} {operation['path']}")
        test_case = generate_test_case(operation)
        all_test_cases.extend(test_case)

    # Save all test cases to a JSON file
    with open('results/archieved/test_cases.json', 'w') as f:
        json.dump(all_test_cases, f, indent=4)

    print("Test cases saved to test_cases.json")

    # Run the test cases
    test_results = []
    for test_case in all_test_cases:
        result = run_test_case(base_url, test_case)
        test_results.append(result)
        # print(f"Test: {result['test_name']}")
        # print(f"Passed: {result['passed']}")
        if not result['passed']:
            print(f"Expected status: {result.get('expected_status')}")
            print(f"Actual status: {result.get('actual_status')}")
            if 'error' in result:
                print(f"Error: {result['error']}")
        print("---")

    # Save test results
    with open('results/archieved/test_results.json', 'w') as f:
        json.dump(test_results, f, indent=4)

    print("Test results saved to test_results.json")


if __name__ == "__main__":
    main()
