# 🐘 Postgres2Parquet Lambda Function

This repository contains Python code for an AWS Lambda function that connects to a PostgreSQL database, executes a SQL query, and writes the query result to either Amazon S3 or local storage in Parquet format. The function is designed to be triggered by an AWS Lambda event.

[![AWS](https://img.shields.io/badge/Cloud-AWS-232F3E?logo=amazon-aws&logoColor=white)](https://aws.amazon.com/)
[![AWS Lambda](https://img.shields.io/badge/Serverless-AWS%20Lambda-FD971F?logo=amazon-aws&logoColor=white)](https://aws.amazon.com/lambda/)
[![Amazon RDS PostgreSQL](https://img.shields.io/badge/Database-Amazon%20RDS%20PostgreSQL-232F3E?logo=amazon-rds&logoColor=white)](https://aws.amazon.com/rds/post)
[![Parquet](https://img.shields.io/badge/Data%20Format-Parquet-53A73E?logo=apache-parquet&logoColor=white)](https://parquet.apache.org/)
[![Amazon S3](https://img.shields.io/badge/Storage-Amazon%20S3-FF9900?logo=amazon-s3&logoColor=white)](https://aws.amazon.com/s3/)
[![Python](https://img.shields.io/badge/Code-Python-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Black](https://img.shields.io/badge/Code%20Style-Black-000000?logo=python&logoColor=white)](https://black.readthedocs.io/)
[![GitHub Actions](https://img.shields.io/badge/CI%2FCD-GitHub%20Actions-2088FF?logo=github-actions&logoColor=white)](https://github.com/features/actions)
[![License](https://img.shields.io/badge/License-MIT-brightgreen.svg)](LICENSE)

---

## 📂 Files

1. `lambda_function.py`: Contains the Lambda function's code.


2. `query.sql`: Contains the SQL query to be executed.


3. `local_lambda_runner.py`: Script for running the Lambda function locally.


4. `test_event.json`: Sample AWS Lambda event for running the Lambda function locally.


5. `test_lambda_function.py`: Unit tests for the Lambda function.


6. `Pipfile`: Dependency list for Pipenv.


7. `Pipfile.lock`: Dependency lock file for Pipenv.


8. `.github/workflows/deploy-to-lambda.yml`: GitHub Actions workflow for automating Lambda function deployment.

 
9. `.github/workflows/run-tests.yml`: GitHub Actions workflow for automating unit tests execution in PRs.


---

## 🚀 Deploy Parameters

In the GitHub repository Secrets, make sure to configure the following secret variables:

| Parameter           | Description                                      |
|---------------------|--------------------------------------------------|
| **AWS_ACCESS_KEY_ID**| AWS access key ID.                               |
| **AWS_SECRET_ACCESS_KEY**| AWS secret access key.                        |

These are used by the GitHub Actions deployment workflow to authenticate with AWS and deploy and publish the Lambda function.

In AWS, make sure to configure the following environment variables in your lambda function environment variables settings:

| Parameter               | Description                                          |
|-------------------------|------------------------------------------------------|
| **ENVIRONMENT**         | Name of the environment (`production` or `staging`). |
| **DB_NAME_PROD**        | Name of the production database.                     |
| **DB_NAME_STAGING**     | Name of the staging database.                        |
| **DB_USER**             | Database username.                                   |
| **DB_PASSWORD_PROD**    | Database password for production.                    |
| **DB_PASSWORD_STAGING** | Database password for staging.                       |
| **DB_HOST_PROD**        | Database host.                                       |
| **DB_HOST_STAGING**     | Database host for staging.                           |
| **DB_PORT_PROD**        | Database port.                                       |
| **DB_PORT_STAGING**     | Database port for staging.                           |
| **FILE_NAME**           | Name of the output file.                             |
| **S3_PATH**             | Storage path for Amazon S3 (production).             |
| **LOCAL_PATH**          | Storage path for local storage (staging).            |

---

## ⚙️ Setup

To use this Lambda function, follow these steps:

1. **Environment Variables**: Set required environment variables, including database connection details (e.g., `DB_NAME_PROD`, `DB_USER`, `DB_PASSWORD_PROD`, etc.), output file name (`FILE_NAME`), and storage paths (`S3_PATH` and/or `LOCAL_PATH`).


2. **AWS Lambda Configuration**: Create an AWS Lambda function and configure it to trigger based on your use case. Attach an execution role granting database access and S3 write permissions.


3. **AWS IAM User for Lambda Deployment**: Create an AWS IAM user with 3rd Party Access with the following inline policy. Make sure to replace the placeholders with your region, account number, and Lambda function name.     Make sure to create the user's access key ID and secret access key and add them to your GitHub repository Secrets.

```JSON
{
	"Version": "2012-10-17",
	"Statement": [
		{
			"Effect": "Allow",
			"Action": [
				"lambda:UpdateFunctionCode",
				"lambda:PublishVersion"
			],
			"Resource": "arn:aws:lambda:{REGION}:{ACCOUNT_NUMBER}:function:{LAMBDA_FUNCTION_NAME}"
		}
	]
}
```


4. **SQL Query**: Create your SQL query to be executed by the Lambda function and save it in `query.sql`.


5. **GitHub Actions Deployment**: Automate deployment using GitHub Actions. Push changes to the main branch or trigger events to execute the deployment workflow defined in `.github/workflows/deploy-to-lambda.yml`.

---

## 🛠 Usage

Once triggered, the Lambda function connects to the specified PostgreSQL database, executes the SQL query, and writes the result to the chosen storage location (S3 or local). Monitor execution and view errors in the AWS Lambda console.

---

## ❌ Error Handling

The Lambda function includes error handling, logging exceptions, and returning a 500 status code with an error message in the response if an error occurs.

---

## 📝 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## 🤝 Contributing

You are welcome to contribute to this project by submitting a pull request. If you have any suggestions or problems, please open an issue. Thank you!

---

## 💖 Support

Your support keeps this project going!

- ⭐️ **Star**: Show your appreciation by giving this project a star.
- ☕️ **[Buy Me a Coffee](https://github.com/sponsors/DevGlitch)**: Contribute by buying a virtual coffee.
- 💼 **[Sponsor This Project](https://github.com/sponsors/DevGlitch)**: Consider sponsoring for ongoing support.



Making a difference, one line of code at a time...
