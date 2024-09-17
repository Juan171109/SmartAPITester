# SmartAPITester

SmartAPITester is an intelligent REST API testing tool that leverages AI to generate and execute test cases based on OpenAPI specifications. It uses machine learning techniques to analyze test results and improve test case generation over multiple iterations.

## Features

- Automatic test case generation from OpenAPI (Swagger) specifications
- AI-powered test case creation using OpenAI's GPT models
- Iterative learning process to improve test coverage and effectiveness
- Advanced analysis of test results using machine learning techniques
- Support for multiple HTTP methods (GET, POST, PUT, DELETE, PATCH)
- Detailed test results and analysis output

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/Juan171109/SmartAPITester.git
   cd SmartAPITester
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Set up your OpenAI API key:
   For powershell
   ```
   setx OPENAI_API_KEY='your-api-key-here'
   ```
   For bash
   ```
   export OPENAI_API_KEY='your-api-key-here'
   ```

## Usage

Run the SmartAPITester tool using the following command:

```
python smartapitester.py <openapi_spec_file> <base_url> [iterations]
```

- `<openapi_spec_file>`: Path to your OpenAPI specification file (YAML or JSON)
- `<base_url>`: Base URL of the API you're testing
- `[iterations]`: (Optional) Number of iterations for test case generation and execution (default is 1)

Example:
```
python .\smartapitester.py .\spec\petstore.yaml http://localhost:8080/v3 3
```

This command will run SmartAPITest for 3 iterations, generating and executing test cases based on the `api_spec.yaml` file against the API at `https://api.example.com`.

## Output

SmartAPITester generates two main output files in the `results` directory:

1. `test_cases.json`: Contains all generated test cases
2. `test_results.json`: Contains the results of all executed test cases

Additionally, the tool provides console output with information about test case generation, execution, and analysis.

## Test cases statistics

SmartAPITester generate test cases and saved in the `results` directory. Use below command to get test case statistics.

```
python .\testcase_analysis.py E:\Projects\PR60\SmartAPITester\results\test_cases.json
```

replace the test case path with your real test case path.

## Test Results Analysis

SmartAPITester provide test results analysis by following command:

```commandline
python data_analysis.py path_to_json_file
```

Example:
```
python data_analysis.py .\results\test_results.json
```
By the default, test results json file is saved in results folder under the project root.
The analysis results will be generated in the results folder with timestamp.

## Advanced Features

SmartAPITester includes advanced analysis features such as:

- Clustering of similar test cases
- Anomaly detection to identify unusual test results
- Association rule learning to uncover patterns in API behavior

These features help in generating more effective test cases in subsequent iterations.

## Contributing

Contributions to SmartAPITester are welcome! Please feel free to submit a Pull Request.

## Acknowledgments

- OpenAI for providing the GPT models used in test case generation
- The scikit-learn team for machine learning libraries used in advanced analysis