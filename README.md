# Postgres2Parquet Lambda Function

This repository contains Python code for an AWS Lambda function that connects to a PostgreSQL database, executes a SQL query, and writes the query result to either Amazon S3 or local storage in Parquet format. The function is designed to be triggered by an AWS Lambda event.

## Files

1. **lambda_function.py**: Contains the Lambda function's code.
2. **query.sql**: Contains the SQL query to be executed.
3. **local_lambda_runner.py**: Script for running the Lambda function locally.
4. **test_event.json**: Sample AWS Lambda event for running the Lambda function locally.
5. **tests.py**: Unit tests for the Lambda function.
6. **Pipfile**: Dependency list for Pipenv.
7. **.github/workflows/deploy-to-lambda.yml**: GitHub Actions workflow for automating Lambda function deployment.
8. **.github/workflows/run-tests.yml**: GitHub Actions workflow for automating unit tests execution in PRs.

## Deploy Parameters

In the GitHub repository Secrets, make sure to configure the following secret variables:

| Parameter           | Description                                      |
|---------------------|--------------------------------------------------|
| **AWS_ACCESS_KEY_ID**| AWS access key ID.                               |
| **AWS_SECRET_ACCESS_KEY**| AWS secret access key.                        |

These are used by the GitHub Actions deployment workflow to authenticate with AWS and deploy and publish the Lambda function.

In AWS, make sure to configure the following environment variables in your lambda function environment variables settings:

| Parameter           | Description                                      |
|---------------------|--------------------------------------------------|
| **DB_NAME_PROD**    | Name of the production database.                |
| **DB_NAME_STAGING** | Name of the staging database.                   |
| **DB_USER**         | Database username.                               |
| **DB_PASSWORD_PROD**| Database password for production.               |
| **DB_PASSWORD_STAGING**| Database password for staging.               |
| **DB_HOST_PROD**    | Database host.                                   |
| **DB_HOST_STAGING** | Database host for staging.                      |
| **DB_PORT_PROD**    | Database port.                                   |
| **DB_PORT_STAGING** | Database port for staging.                      |
| **FILE_NAME**       | Name of the output file.                         |
| **S3_PATH**         | Storage path for Amazon S3 (production).        |
| **LOCAL_PATH**      | Storage path for local storage (staging).       |

## Setup

To use this Lambda function, follow these steps:

1. **Environment Variables**: Set required environment variables, including database connection details (e.g., `DB_NAME_PROD`, `DB_USER`, `DB_PASSWORD_PROD`, etc.), output file name (`FILE_NAME`), and storage paths (`S3_PATH` and/or `LOCAL_PATH`).

2. **AWS Lambda Configuration**: Create an AWS Lambda function and configure it to trigger based on your use case. Attach an execution role granting database access and S3 write permissions.

3. **GitHub Actions Deployment**: Automate deployment using GitHub Actions. Push changes to the main branch or trigger events to execute the deployment workflow defined in `.github/workflows/deploy.yml`.

## Usage

Once triggered, the Lambda function connects to the specified PostgreSQL database, executes the SQL query, and writes the result to the chosen storage location (S3 or local). Monitor execution and view errors in the AWS Lambda console.

## Error Handling

The Lambda function includes error handling, logging exceptions, and returning a 500 status code with an error message in the response if an error occurs.
