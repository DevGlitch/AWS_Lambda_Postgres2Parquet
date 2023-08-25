import json
import logging
import os
import psycopg2
import awswrangler as wr
import pandas as pd
from sqlalchemy import create_engine

# Configure logger(format: timestamp - log level - message)
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s: %(message)s"
)
logger = logging.getLogger()


def get_environment():
    """
    Get the staging flag based on the 'ENVIRONMENT' environment variable.

    This function reads the 'ENVIRONMENT' environment variable and returns a
    boolean flag indicating whether the application is in production or staging mode.

    Returns:
        bool: True if the environment is set to 'staging', False if set to 'production'.

    Raises:
        ValueError: If the 'ENVIRONMENT' environment variable is set to an invalid value.
        EnvironmentError: If the 'ENVIRONMENT' environment variable is missing.
    """
    try:
        environment = os.environ["ENVIRONMENT"]

        if environment == "production":
            testing = False
        elif environment == "staging":
            testing = True
        else:
            raise ValueError(f"Invalid environment: {environment}")
    except KeyError as e:
        raise EnvironmentError(f"Missing required environment variable: {e}")

    return testing


def load_environment_variables(staging):
    """
    Load environment variables from AWS Lambda or local environment.

    Returns:
        Tuple: A tuple containing the database connection parameters and file-related parameters.
    """
    try:
        logger.info("Loading environment variables...")
        db_name = (
            os.environ["DB_NAME_PROD"] if not staging else os.environ["DB_NAME_STAGING"]
        )
        db_user = os.environ["DB_USER"]
        db_password = (
            os.environ["DB_PASSWORD_PROD"]
            if not staging
            else os.environ["DB_PASSWORD_STAGING"]
        )
        db_host = (
            os.environ["DB_HOST_PROD"] if not staging else os.environ["DB_HOST_STAGING"]
        )
        db_port = (
            os.environ["DB_PORT_PROD"] if not staging else os.environ["DB_PORT_STAGING"]
        )
        file_name = os.environ["FILE_NAME"]
        path = os.environ["S3_PATH"] if not staging else os.environ["LOCAL_PATH"]
        logger.info("Environment variables loaded")
        return db_name, db_user, db_password, db_host, db_port, file_name, path
    except KeyError as e:
        raise EnvironmentError(f"Missing required environment variable: {e}")


def connect_to_db(db_name, db_user, db_password, db_host, db_port):
    """
    Connect to the PostgreSQL database.

    Args:
        db_name (str): Name of the database.
        db_user (str): Database username.
        db_password (str): Database password.
        db_host (str): Database host.
        db_port (str): Database port.

    Returns:
        psycopg2.extensions.connection: A PostgreSQL database connection.
    """
    try:
        logger.info("Connecting to DB...")
        conn = psycopg2.connect(
            database=db_name,
            user=db_user,
            password=db_password,
            host=db_host,
            port=db_port,
        )
        logger.info("Connected to DB")
        return conn
    except psycopg2.OperationalError as e:
        raise ConnectionError(f"Database connection error: {e}")


def query_database(conn, db_name, db_user, db_password, db_host, db_port):
    """
    Execute a SQL query against the PostgreSQL database.

    Args:
        conn (psycopg2.extensions.connection): A PostgreSQL database connection.
        db_name (str): Name of the database.
        db_user (str): Database username.
        db_password (str): Database password.
        db_host (str): Database host.
        db_port (str): Database port.

    Returns:
        pandas.DataFrame: Query result as a DataFrame.
    """

    # Define SQL Query
    sql_query = """SELECT artifacts.id
                ,   artifacts.obj_id
                ,   artifacts.artifact_type_id
                ,   artifacts.sighting_obj_id
                ,   artifacts.observation_id
                ,   artifacts.user_label_foot
                ,   artifacts.s3_image_name
                ,   artifacts.expert_label_rating
                ,   artifacts.expert_label_foot
                ,   artifacts.user_comments as artifact_user_comments
                ,   artifacts.expert_comments as artifact_expert_comments
                ,   artifacts.expert_reviewed_at
                ,   artifacts.expert_modified_at
                ,   artifacts.expert_reviewed
                ,   artifacts.taken_at
                ,   artifact_types.name
                ,   observations.uploaded_at
                ,   observations.location_latitude
                ,   observations.location_longitude
                ,   observations.location_name
                ,   observations.location_accuracy
                ,   observations.location_utm_northing
                ,   observations.location_utm_easting
                ,   observations.location_utm_zone
                ,   observations.user_label_animal_id
                ,   observations.user_label_animal_name
                ,   observations.user_label_captive_wild
                ,   observations.user_label_dob
                ,   observations.user_label_known_individual
                ,   observations.user_label_sex
                ,   observations.user_label_species_name
                ,   observations.user_label_species_id
                ,   observations.source
                ,   observations.expert_label_animal_name
                ,   observations.expert_label_sex
                ,   observations.expert_label_species_name
                ,   observations.expert_label_species_id
                ,   observations.captive_wild
                ,   observations.known_individual
                ,   observations.individual_multiple
                ,   observations.potential_individuals
                ,   observations.user_comments
                ,   observations.expert_comments
                ,   users.first_name
                ,   users.last_name
                ,   users.email
                ,   users.organization
                ,   users.academic_affiliation
                FROM artifacts
                INNER JOIN artifact_types ON artifacts.artifact_type_id = artifact_types.id
                INNER JOIN observations ON artifacts.observation_id = observations.id
                INNER JOIN users ON observations.user_id = users.id;   """

    engine = create_engine(
        f"postgresql+psycopg2://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    )

    try:
        logger.info("Querying DB...")
        with conn.cursor() as curr:
            logger.info("Executing query...")
            query_result = pd.read_sql_query(sql_query, engine)
        return query_result
    except Exception as e:
        raise RuntimeError(f"Database query error: {e}")


def write_to_s3_or_local(data, staging, file_name, path):
    """
    Write data to either Amazon S3 or local storage based on the testing flag.

    Args:
        data (pandas.DataFrame): Data to be written.
        staging (bool): True if the application is in staging mode, False if in production mode.
        file_name (str): Name of the output file.
        path (str): Storage path.

    Returns:
        None
    """
    logger.info("Writing result to S3 or local...")

    if not staging:
        # Write result to S3 when not in testing mode
        wr.s3.to_parquet(
            df=data,
            path=path + file_name,
            dataset=False,
            sanitize_columns=False,
            overwrite=True,
            storage_class="INTELLIGENT_TIERING",
        )
    else:
        # Save the DataFrame to Parquet for local storage
        data.to_parquet(path + file_name, index=False)

    logger.info(f"Result written to {path + file_name}")


def handle_error(error):
    """
    Handle and log an error.

    Parameters:
    - error (str or Exception): The error message or exception to be logged.

    Returns:
    - dict: A dictionary containing an error response with a status code and error message.

    This function logs the provided error message using the logger's error level
    and returns an HTTP-like error response as a dictionary. It is typically used
    in Lambda functions to handle and report errors.

    Example:
    If you call handle_error("An error occurred."), it logs the error and returns:
    {"statusCode": 500, "body": "Error: An error occurred."}
    """
    logger.error(f"Error: {str(error)}")
    return {"statusCode": 500, "body": f"Error: {str(error)}"}


def lambda_handler(event, context):
    """
    AWS Lambda entry point.

    Args:
        event: AWS Lambda event.
        context: AWS Lambda context.

    Returns:
        dict: AWS Lambda response.
    """
    logger.info("Starting Postgres2Parquet Lambda Function...")

    try:
        staging = get_environment()
        (
            db_name,
            db_user,
            db_password,
            db_host,
            db_port,
            file_name,
            path,
        ) = load_environment_variables(staging)
        conn = connect_to_db(db_name, db_user, db_password, db_host, db_port)

        try:
            query_result = query_database(
                conn, db_name, db_user, db_password, db_host, db_port
            )
            write_to_s3_or_local(query_result, staging, file_name, path)
        finally:
            conn.close()
            logger.info("DB connection closed")

        logger.info("Postgres2Parquet Lambda Function complete")
        return {"statusCode": 200, "body": json.dumps("Success")}

    except Exception as e:
        return handle_error(e)
