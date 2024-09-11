import json

import requests
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import OpenAI
from langchain_core.prompts import FewShotPromptTemplate, PromptTemplate
from input.example2 import examples

import prance


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
    example_prompt = PromptTemplate(
        input_variables=["input", "output"],
        template="Input: {input}\nOutput: {output}"
    )

    few_shot_prompt = FewShotPromptTemplate(
        examples=examples,
        example_prompt=example_prompt,
        suffix="input: {input}",
        input_variables=["input"],
    )
    model = OpenAI(model="gpt-3.5-turbo-instruct",
                   temperature=0,
                   max_retries=2, )
    parser = StrOutputParser()
    chain = few_shot_prompt | model | parser
    test_cases = chain.invoke(input=operation_string)

    return test_cases


def execute_test_case(base_url, test_case):
    # Parse the test case and execute the API call
    # This is a simplified version and would need to be expanded based on your test case format
    method = test_case['method'].lower()
    url = base_url + test_case['path']
    headers = test_case.get('headers', {})
    params = test_case.get('params', {})
    data = test_case.get('data', {})

    response = requests.request(method, url, headers=headers, params=params, json=data)

    # Compare the response with expected results
    # This is a basic comparison and would need to be expanded based on your needs
    if response.status_code == test_case['expected_status']:
        print(f"Test case {test_case['name']} passed!")
    else:
        print(
            f"Test case {test_case['name']} failed. Expected status {test_case['expected_status']}, got {response.status_code}")


def main():
    openapi_spec_file = "spec/market.yaml"
    base_url = "http://localhost:8081"
    openapi_spec = prance.ResolvingParser(openapi_spec_file).specification
    operations = analyze_spec(openapi_spec)

    # Define the path where you want to save the operations file.
    operations_file_path = "results/operations.json"

    # Write the operations to a JSON file.
    with open(operations_file_path, 'w') as operations_file:
        json.dump(operations, operations_file, indent=4)

    print(f"Operations saved to {operations_file_path}")

    # print(operations[1])

    for operation in operations:

        test_case = generate_test_case(operation)
        print(f"Generated test case for {operation['operation_id']}:")
        print(test_case)
        print("\n")

        # Parse the generated test case and execute it
        # Note: This assumes a specific format for the generated test cases
        # You might need to adjust this based on the actual output from the OpenAI model
        try:
            parsed_test_case = json.loads(test_case)
            print(parsed_test_case)
            # execute_test_case(base_url, parsed_test_case)
        except json.JSONDecodeError:
            print("Failed to parse the generated test case. Skipping execution.")


if __name__ == "__main__":
    main()
