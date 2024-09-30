import json
import sys

import numpy as np
import pandas as pd
import prance
import requests
from langchain_core.messages import HumanMessage
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from mlxtend.utils import Counter

from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import IsolationForest
from mlxtend.frequent_patterns import apriori
from mlxtend.frequent_patterns import association_rules


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


def extract_features(test_result):
    """Extract features from a test result."""
    return {
        'status_code': test_result['actual_status'],
        'response_time': test_result.get('response_time', 0),  # Assuming we add this to our test results
        'payload_size': len(json.dumps(test_result['actual_body'])) if test_result['actual_body'] else 0,
        'is_error': int(not test_result['passed']),
        'method': test_result['request']['method'],
        'path_depth': len(test_result['request']['path'].split('/')),
        'query_param_count': len(test_result['request'].get('query', {})),
        'header_count': len(test_result['request'].get('headers', {})),
        'body_complexity': json_complexity(test_result['request'].get('body', {}))
    }


def json_complexity(obj, level=0):
    """Recursively calculate the complexity of a JSON object."""
    if isinstance(obj, dict):
        return sum(json_complexity(v, level + 1) for v in obj.values()) + level
    elif isinstance(obj, list):
        return sum(json_complexity(item, level + 1) for item in obj) + level
    else:
        return 1


def vectorize_features(features_list):
    """Convert list of feature dictionaries to a numpy array."""
    return np.array([[
        f['status_code'], f['response_time'], f['payload_size'], f['is_error'],
        hash(f['method']), f['path_depth'], f['query_param_count'],
        f['header_count'], f['body_complexity']
    ] for f in features_list])


def cluster_test_cases(features):
    """Cluster test cases using DBSCAN."""
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(features)
    clustering = DBSCAN(eps=0.5, min_samples=2).fit(X_scaled)
    return clustering.labels_


def detect_anomalies(features):
    """Detect anomalies using Isolation Forest."""
    clf = IsolationForest(contamination=0.1, random_state=42)
    return clf.fit_predict(features)


def find_association_rules(features_list):
    """Find association rules in the features."""
    df = pd.DataFrame(features_list)
    frequent_itemsets = apriori(df, min_support=0.1, use_colnames=True)
    rules = association_rules(frequent_itemsets, metric="confidence", min_threshold=0.7)
    return rules


def advanced_analysis(test_results):
    features_list = [extract_features(result) for result in test_results]
    features_array = vectorize_features(features_list)

    clusters = cluster_test_cases(features_array)
    anomalies = detect_anomalies(features_array)
    rules = find_association_rules(features_list)

    analysis = {
        "clusters": dict(Counter(clusters)),
        "anomalies": sum(1 for a in anomalies if a == -1),
        "association_rules": rules.to_dict('records')
    }

    return analysis


def analyze_test_results(test_results):
    """Analyze test results to identify patterns and issues."""
    analysis = {
        "total_tests": len(test_results),
        "passed_tests": sum(1 for result in test_results if result['passed']),
        "failed_tests": sum(1 for result in test_results if not result['passed']),
        "common_errors": {},
        "unexpected_responses": []
    }

    for result in test_results:
        if not result['passed']:
            error = result.get(
                'error') or f"Status code mismatch: expected {result['expected_status']}, got {result['actual_status']}"
            analysis['common_errors'][error] = analysis['common_errors'].get(error, 0) + 1

        if result['actual_status'] != result['expected_status']:
            analysis['unexpected_responses'].append({
                "test_name": result['test_name'],
                "expected_status": result['expected_status'],
                "actual_status": result['actual_status'],
                "actual_body": result['actual_body']
            })

    return analysis


def generate_test_case(operation, previous_results=None):
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
    """

    if previous_results:
        basic_analysis = analyze_test_results(previous_results)
        adv_analysis = advanced_analysis(previous_results)

        prompt_text += f"""
            Consider the following advanced analysis from previous test runs:
            - Clusters of similar test cases: {adv_analysis['clusters']}
            - Number of anomalous test cases: {adv_analysis['anomalies']}
            - Top association rules: {adv_analysis['association_rules'][:5]}

            Based on this analysis:
            1. Generate test cases that explore underrepresented clusters
            2. Create test cases similar to the anomalous ones to further investigate edge cases
            3. Utilize the association rules to create test cases that combine features in ways likely to uncover issues
            """

    prompt_text += "\nGenerate an array of at least 3 test cases. Do not include any text outside the JSON array."

    model = ChatOpenAI(model="gpt-4o-mini")
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an API testing expert. Generate test cases in JSON format without any additional text."),
        MessagesPlaceholder("msgs")
    ])

    output_parser = JsonOutputParser()
    chain = prompt | model | output_parser

    try:
        test_cases = chain.invoke({"msgs": [HumanMessage(content=prompt_text)]})

        if not isinstance(test_cases, list):
            test_cases = [test_cases]

        validated_test_cases = [
            case for case in test_cases
            if all(key in case for key in ['test_name', 'request', 'expected_response'])
        ]

        return validated_test_cases
    except json.JSONDecodeError:
        print("Error: Generated content is not valid JSON")
        return []


def main():
    openapi_spec_file = sys.argv[1]
    base_url = sys.argv[2]
    iterations = int(sys.argv[3]) if len(sys.argv) > 3 else 1

    openapi_spec = prance.ResolvingParser(openapi_spec_file).specification
    operations = analyze_spec(openapi_spec)

    all_test_cases = []
    all_test_results = []

    for iteration in range(iterations):
        print(f"Iteration {iteration + 1}/{iterations}")

        for operation in operations:
            print(f"Generating test cases for: {operation['method']} {operation['path']}")
            previous_results = [r for r in all_test_results if
                                r['test_name'].startswith(f"{operation['method']}_{operation['path']}")]
            test_cases = generate_test_case(operation, previous_results if iteration > 0 else None)

            for test_case in test_cases:
                print(f"Running test case: {test_case['test_name']}")
                result = run_test_case(base_url, test_case, operation)
                all_test_cases.append(test_case)
                all_test_results.append(result)

                if not result['passed']:
                    print(f"Test failed: {result['test_name']}")
                    print(f"Expected status: {result.get('expected_status')}")
                    print(f"Actual status: {result.get('actual_status')}")
                    if 'error' in result:
                        print(f"Error: {result['error']}")
                print("---")

    # Save all test cases and results
    with open('results/archieved/test_cases.json', 'w') as f:
        json.dump(all_test_cases, f, indent=4)

    with open('results/archieved/test_results.json', 'w') as f:
        json.dump(all_test_results, f, indent=4)

    print(f"Generated and ran {len(all_test_cases)} test cases across {iterations} iterations.")
    print(f"Test cases saved to test_cases.json")
    print(f"Test results saved to test_results.json")


if __name__ == "__main__":
    main()
