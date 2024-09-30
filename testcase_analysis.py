import json
from collections import defaultdict
import sys
import csv
from datetime import datetime


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

    # print("\nOperations covered:")
    # for operation, tests in operations.items():
    #     print(f" {operation}: {len(tests)} test(s)")

    total_operations = len(operations)
    print(f"\nTotal unique operations: {total_operations}")

    # 3. Calculate the status code coverage
    status_codes = defaultdict(int)
    for test in test_cases:
        status = test['expected_response']['status_code']
        status_codes[status] += 1

    print("\nStatus code coverage:")
    for status, count in sorted(status_codes.items()):
        print(f" {status}: {count} test(s)")

    total_status_codes = len(status_codes)
    print(f"\nTotal unique status codes: {total_status_codes}")

    # 4. Verify that the total expected status codes match the test case count
    total_expected_status_codes = sum(status_codes.values())
    print(f"\nTotal expected status codes: {total_expected_status_codes}")

    if total_expected_status_codes != test_case_count:
        print(f"WARNING: Mismatch between test case count ({test_case_count}) and total expected status codes ({total_expected_status_codes})")
        print("Investigating discrepancy...")
        investigate_discrepancy(test_cases, status_codes)

    # Return the results for CSV writing
    return {
        'test_case_count': test_case_count,
        'operations': operations,
        'status_codes': status_codes,
        'total_operations': total_operations,
        'total_status_codes': total_status_codes,
        'total_expected_status_codes': total_expected_status_codes
    }


def investigate_discrepancy(test_cases, status_codes):
    expected_status_codes = sum(status_codes.values())
    for i, test in enumerate(test_cases):
        if 'expected_response' not in test or 'status_code' not in test['expected_response']:
            print(f"Test case {i} is missing expected status code:")
            print(json.dumps(test, indent=2))
            print()


def save_results_to_csv(results, output_file):
    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)

        # Write summary
        writer.writerow(['Summary'])
        writer.writerow(['Total number of test cases', results['test_case_count']])
        writer.writerow(['Total unique operations', results['total_operations']])
        writer.writerow(['Total unique status codes', results['total_status_codes']])
        # writer.writerow(['Total expected status codes', results['total_expected_status_codes']])
        writer.writerow([])

        # Write operations coverage
        # writer.writerow(['Operations Coverage'])
        # writer.writerow(['Operation', 'Number of Tests'])
        # for operation, tests in results['operations'].items():
        #     writer.writerow([operation, len(tests)])
        # writer.writerow([])

        # Write status code coverage
        writer.writerow(['Status Code Coverage'])
        writer.writerow(['Status Code', 'Number of Tests'])
        for status, count in sorted(results['status_codes'].items()):
            writer.writerow([status, count])


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

        # Calculate the statistics and get the results
        results = calculate_test_statistics(test_cases)

        # Save results to CSV
        # Generate CSV filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"./results/test_coverage_summary_{timestamp}.csv"
        save_results_to_csv(results, output_file)
        print(f"\nResults saved to {output_file}")

    except FileNotFoundError:
        print(f"Error: The file '{test_cases_file}' was not found.")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: The file '{test_cases_file}' is not a valid JSON file.")
        sys.exit(1)


if __name__ == "__main__":
    main()
