import os
import psycopg2
import unittest
import pandas as pd
from unittest.mock import MagicMock, Mock, patch, ANY, mock_open
from local_lambda_runner import lambda_handler
from lambda_function import (
    get_environment,
    load_environment_variables,
    connect_to_db,
    read_sql_query_from_file,
    query_database,
    write_to_s3_or_local,
    handle_error,
)


class TestPostgres2ParquetLambdaFunction(unittest.TestCase):

    def setUp(self):
        # Mocking environment variables
        self.original_environ = dict(os.environ)
        os.environ["ENVIRONMENT"] = "staging"
        os.environ["DB_NAME_STAGING"] = "staging_db"
        os.environ["DB_NAME_PROD"] = "production_db"
        os.environ["DB_USER"] = "test_user"
        os.environ["DB_PASSWORD_STAGING"] = "test_staging_password"
        os.environ["DB_PASSWORD_PROD"] = "test_prod_password"
        os.environ["DB_HOST_STAGING"] = "test_staging_host"
        os.environ["DB_HOST_PROD"] = "test_prod_host"
        os.environ["DB_PORT_STAGING"] = "9876"
        os.environ["DB_PORT_PROD"] = "1234"
        os.environ["FILE_NAME"] = "test.parquet"
        os.environ["S3_PATH"] = "s3://bucket/"
        os.environ["LOCAL_PATH"] = "/local/path/"

    def tearDown(self):
        # Restore original environment variables
        os.environ.clear()
        os.environ.update(self.original_environ)

    def test_get_environment_staging(self):
        # Test get_environment function
        self.assertTrue(get_environment())  # Environment is set to 'staging'

    def test_get_environment_production(self):
        os.environ["ENVIRONMENT"] = "production"
        self.assertFalse(get_environment())  # Environment is set to 'production'

    def test_get_environment_missing_var(self):
        del os.environ["ENVIRONMENT"]
        response = get_environment()
        self.assertEqual(response,
                         {"statusCode": 500, "body": "Error: Missing required environment variable: 'ENVIRONMENT'"})

    def test_get_environment_invalid_value(self):
        os.environ["ENVIRONMENT"] = "invalid"
        response = get_environment()
        self.assertEqual(response, {"statusCode": 500, "body": "Error: Invalid environment variable: Invalid environment: invalid"})

    def test_load_environment_variables_missing_var(self):
        del os.environ["DB_NAME_STAGING"]
        response = load_environment_variables(staging=True)
        self.assertEqual(response, {"statusCode": 500, "body": "Error: Missing required environment variable: 'DB_NAME_STAGING'"})

    def test_load_environment_variables(self):
        # Test load_environment_variables function
        result = load_environment_variables(staging=True)
        self.assertEqual(result[0], "staging_db")  # Check if the staging database name is correct
        result = load_environment_variables(staging=False)
        self.assertEqual(result[0], "production_db")  # Check if the production database name is correct

    def test_connect_to_db(self):
        # Test connect_to_db function
        mock_psycopg2 = MagicMock()
        with patch("psycopg2.connect", new=mock_psycopg2):
            connect_to_db("db_name", "user", "password", "host", "port")
            mock_psycopg2.assert_called_with(
                database="db_name",
                user="user",
                password="password",
                host="host",
                port="port",
            )

    def test_connect_to_db_error(self):
        with patch("psycopg2.connect", side_effect=psycopg2.OperationalError("DB Error")):
            response = connect_to_db("db_name", "user", "password", "host", "port")
            self.assertEqual(response, {"statusCode": 500, "body": "Error: Database connection error: DB Error"})

    def test_query_database_exception(self):
        # Test query_database function with an expected exception
        with self.assertRaises(Exception):  # Replace 'Exception' with the actual exception type you expect
            query_result = query_database(None, "SELECT *", "db_name", "user", "password", "host", "port")

    def test_read_sql_query_from_file_successful(self):
        with patch("builtins.open", mock_open(read_data="SELECT * FROM test;")):
            query = read_sql_query_from_file("query.sql")
            self.assertEqual(query, "SELECT * FROM test;")

    def test_read_sql_query_from_file_not_found(self):
        with patch("builtins.open", mock_open()) as m:
            m.side_effect = FileNotFoundError("File not found")
            response = read_sql_query_from_file("query.sql")
            self.assertEqual(response, {"statusCode": 500, "body": "Error: SQL query file not found: File not found"})

    def test_read_sql_query_from_file_ioerror(self):
        m = mock_open()
        with patch('builtins.open', m):
            m.side_effect = IOError("Mocked IOError")

            result = read_sql_query_from_file("query.sql")

            assert result == {
                "statusCode": 500,
                "body": "Error: Error reading SQL query file: Mocked IOError"
            }

    def test_query_database_successful(self):
        # Test database query success
        mock_cursor = Mock()
        mock_cursor.__enter__ = lambda x: mock_cursor
        mock_cursor.__exit__ = lambda x, y, z, w: None

        mock_conn = Mock()
        mock_conn.cursor.return_value = mock_cursor

        with patch("sqlalchemy.create_engine", return_value=mock_conn) as mock_create_engine, \
                patch("pandas.read_sql_query", return_value=pd.DataFrame()):
            response = query_database(mock_conn, "SELECT * FROM test;", "db_name", "user", "password", "host", "1234")
            self.assertIsInstance(response, pd.DataFrame)

    def test_query_database_failure(self):
        # Test database query failure
        with patch("sqlalchemy.create_engine") as mock_create_engine, \
                patch("pandas.read_sql_query") as mock_read_sql_query:
            engine = Mock()
            mock_create_engine.return_value = engine
            mock_read_sql_query.side_effect = Exception("Database query error")

            conn = Mock()
            with self.assertRaises(Exception):
                query_database(
                    conn, "SELECT * FROM table", "db_name", "user", "password", "host", "port"
                )

    def test_write_to_s3(self):
        # Mock the wr.s3.to_parquet method for S3 storage
        mock_wr_s3 = MagicMock()
        with patch("lambda_function.wr.s3.to_parquet", new=mock_wr_s3):
            write_to_s3_or_local(data=None, staging=False, file_name="test.parquet", path="s3://bucket/")

            # Assert that the wr.s3.to_parquet method was called with the correct arguments
            mock_wr_s3.assert_called_once_with(
                df=None,
                path="s3://bucket/test.parquet",
                s3_additional_kwargs={"StorageClass": "INTELLIGENT_TIERING"},
            )

    def test_write_to_local(self):
        with patch("pandas.DataFrame.to_parquet") as mock_to_parquet:
            data = pd.DataFrame({"A": [1, 2]})
            write_to_s3_or_local(data, staging=True, file_name="test.parquet", path="/local/")
            mock_to_parquet.assert_called_once()

    def test_handle_error(self):
        error_message = "Test Error"
        with self.assertLogs(level="ERROR") as log:
            response = handle_error(error_message)

        # Check if the error message is logged
        self.assertTrue(any(f"Error: {error_message}" in log_message for log_message in log.output))

        # Check if the response is as expected
        expected_response = {"statusCode": 500, "body": f"Error: {error_message}"}
        self.assertEqual(response, expected_response)

    def test_lambda_handler(self):
        # Test lambda_handler function

        # Mock the necessary functions
        mock_get_environment = MagicMock(return_value=True)  # Set the environment to staging
        mock_load_environment_variables = MagicMock(
            return_value=("staging_db", "user", "password", "host", "port", "test.parquet", "s3://bucket/")
        )
        mock_connect_to_db = MagicMock()
        mock_query_database = MagicMock()
        mock_write_to_s3_or_local = MagicMock()
        mock_handle_error = MagicMock()

        # Use patch to replace the actual functions with mocks
        with patch("lambda_function.get_environment", new=mock_get_environment):
            with patch("lambda_function.load_environment_variables", new=mock_load_environment_variables):
                with patch("lambda_function.connect_to_db", new=mock_connect_to_db):
                    with patch("lambda_function.query_database", new=mock_query_database):
                        with patch("lambda_function.write_to_s3_or_local", new=mock_write_to_s3_or_local):
                            with patch("lambda_function.handle_error", new=mock_handle_error):
                                response = lambda_handler(event=None, context=None)

        # Perform assertions
        mock_get_environment.assert_called_once()
        mock_load_environment_variables.assert_called_once_with(True)  # Staging environment
        mock_connect_to_db.assert_called_once_with("staging_db", "user", "password", "host", "port")
        mock_query_database.assert_called_once()
        mock_write_to_s3_or_local.assert_called_once()
        mock_handle_error.assert_not_called()  # Ensure handle_error is not called if there are no exceptions

        # Verify the response
        self.assertEqual(response, {"statusCode": 200, "body": '"Success"'})

    def test_lambda_handler_error(self):
        with patch("lambda_function.get_environment", side_effect=Exception("General Error")):
            response = lambda_handler(None, None)
            self.assertEqual(response, {"statusCode": 500, "body": "Error: Lambda handler error: General Error"})

    def test_query_database_exception_message(self):
        with patch("psycopg2.connect") as mock_connect, \
                patch("pandas.read_sql_query") as mock_read_sql_query:
            mock_conn = mock_connect.return_value
            mock_read_sql_query.side_effect = psycopg2.OperationalError("Operational Error")

            response = query_database(
                mock_conn, "SELECT *", "db_name", "user", "password", "host", "1234"
            )

            self.assertEqual(response, {
                "statusCode": 500,
                "body": "Error: Database query error: Operational Error"
            })

    @patch("lambda_function.wr.s3.to_parquet")
    @patch("lambda_function.os.path.join")
    def test_write_to_s3_exception(self, mock_join, mock_wr_s3):
        mock_data = Mock(spec=pd.DataFrame)
        mock_join.return_value = "s3_path/test.parquet"
        mock_wr_s3.side_effect = Exception("S3 Write Error")

        response = write_to_s3_or_local(
            mock_data, False, "test.parquet", "s3_path/"
        )

        self.assertEqual(response, {
            "statusCode": 500,
            "body": "Error: Error writing data: S3 Write Error"
        })


if __name__ == "__main__":
    unittest.main()
