import json
import sys
import csv
from collections import Counter
from datetime import datetime


def analyze_test_results(file_path):
    # Read the JSON file
    with open(file_path, 'r') as file:
        data = json.load(file)

    # Initialize counters
    total_tests = len(data)
    passed = 0
    failed = 0
    errors = 0
    status_codes = Counter()
    failure_reasons = Counter()

    # Analyze each test result
    for test in data:
        if 'error' in test:
            errors += 1
            failure_reasons['parsing_error'] += 1
        elif test['passed']:
            passed += 1
            status_codes[test['actual_status']] += 1
        else:
            failed += 1
            status_codes[test['actual_status']] += 1

            if test['expected_status'] != test['actual_status']:
                failure_reasons['status_code_mismatch'] += 1
            elif test['expected_body'] != test['actual_body']:
                failure_reasons['body_mismatch'] += 1
            elif test['actual_status'] == 200 and test['expected_status'] != 200:
                failure_reasons['unexpected_success'] += 1
            else:
                failure_reasons['other'] += 1

    # Calculate percentages
    pass_rate = (passed / total_tests) * 100
    fail_rate = (failed / total_tests) * 100
    error_rate = (errors / total_tests) * 100

    # Prepare the results
    results = {
        "total_tests": total_tests,
        "passed": passed,
        "failed": failed,
        "errors": errors,
        "pass_rate": pass_rate,
        "fail_rate": fail_rate,
        "error_rate": error_rate,
        "status_codes": dict(status_codes),
        "failure_reasons": dict(failure_reasons)
    }

    return results


def print_results(results):
    print("REST API Test Results Summary")
    print("=============================")
    print(f"Total Tests: {results['total_tests']}")
    print(f"Passed: {results['passed']} ({results['pass_rate']:.2f}%)")
    print(f"Failed: {results['failed']} ({results['fail_rate']:.2f}%)")
    print(f"Errors: {results['errors']} ({results['error_rate']:.2f}%)")

    print("\nStatus Code Distribution:")
    for status, count in results['status_codes'].items():
        print(f"  {status}: {count}")

    print("\nFailure Reasons:")
    for reason, count in results['failure_reasons'].items():
        print(f"  {reason}: {count}")


def save_to_csv(results, filename):
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Metric', 'Value'])
        writer.writerow(['Total Tests', results['total_tests']])
        writer.writerow(['Passed', results['passed']])
        writer.writerow(['Failed', results['failed']])
        writer.writerow(['Errors', results['errors']])
        writer.writerow(['Pass Rate', f"{results['pass_rate']:.2f}%"])
        writer.writerow(['Fail Rate', f"{results['fail_rate']:.2f}%"])
        writer.writerow(['Error Rate', f"{results['error_rate']:.2f}%"])

        writer.writerow([])
        writer.writerow(['Status Code', 'Count'])
        for status, count in results['status_codes'].items():
            writer.writerow([status, count])

        writer.writerow([])
        writer.writerow(['Failure Reason', 'Count'])
        for reason, count in results['failure_reasons'].items():
            writer.writerow([reason, count])


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python data_analysis.py <path_to_json_file>")
        sys.exit(1)

    file_path = sys.argv[1]
    results = analyze_test_results(file_path)
    print_results(results)

    # Generate CSV filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_filename = f"./results/test_results_summary_{timestamp}.csv"

    save_to_csv(results, csv_filename)
    print(f"\nResults saved to {csv_filename}")