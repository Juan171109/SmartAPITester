import json
from collections import defaultdict
import sys


def calculate_test_statistics(test_cases):
    # 1. Calculate the number of test cases
    test_case_count = len(test_cases)
    print(f"Total number of test cases: {test_case_count}")

    # 2. Calculate the operations covered
    operations = defaultdict(set)
    for test in test_cases:
        method = test['request']['method']
        path = test['request']['path']
        operations[f"{method} {path}"].add(test['test_name'])

    print("\nOperations covered:")
    for operation, tests in operations.items():
        print(f"  {operation}: {len(tests)} test(s)")

    total_operations = len(operations)
    print(f"\nTotal unique operations: {total_operations}")

    # 3. Calculate the status code coverage
    status_codes = defaultdict(set)
    for test in test_cases:
        status = test['expected_response']['status_code']
        status_codes[status].add(test['test_name'])

    print("\nStatus code coverage:")
    for status, tests in sorted(status_codes.items()):
        print(f"  {status}: {len(tests)} test(s)")

    total_status_codes = len(status_codes)
    print(f"\nTotal unique status codes: {total_status_codes}")


def main():
    # Check if a file path is provided as a command-line argument
    if len(sys.argv) != 2:
        print("Usage: python script_name.py <path_to_test_cases.json>")
        sys.exit(1)

    test_cases_file = sys.argv[1]

    try:
        # Load the test cases from the JSON file
        with open(test_cases_file, 'r') as f:
            test_cases = json.load(f)

        # Calculate and print the statistics
        calculate_test_statistics(test_cases)
    except FileNotFoundError:
        print(f"Error: The file '{test_cases_file}' was not found.")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: The file '{test_cases_file}' is not a valid JSON file.")
        sys.exit(1)


if __name__ == "__main__":
    main()
