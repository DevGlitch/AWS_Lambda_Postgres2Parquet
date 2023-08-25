import json
import os

# library for database connection
import psycopg2

# library for writing parquet to s3
import awswrangler as wr

# pandas library for dataframe creation
import pandas as pd


# ------------------------------------------------------

def lambda_handler(event, context):
    # # connect to database - PROD
    # conn = psycopg2.connect(
    # database=os.environ['DB_NAME_PROD'],
    # user=os.environ['POSTGRES_USER'],
    # password=os.environ['POSTGRES_PASS_PROD'],
    # host=os.environ['DB_HOST_PROD'],
    # port='5432')

    # connect to database - STAGING
    conn = psycopg2.connect(
        database=os.environ['DB_NAME_STAGING'],
        user=os.environ['POSTGRES_USER'],
        password=os.environ['POSTGRES_PASS_STAGING'],
        host=os.environ['DB_HOST_STAGING'],
        port='5432')

    with conn.cursor() as curr:
        # define SQL Query
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

        # execute query using pandas
        query_result = pd.read_sql_query(sql_query, conn)
    # print(query_result)

    # write result to parquet and store it in S
    wr.s3.to_parquet(
        df=query_result,
        path='s3://wildtrack-platform-prod-metadata/query_reault.parquet',
        dataset=False,
        sanitize_columns=False
    )

    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
