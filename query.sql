-- This SQL query retrieves data from multiple tables: artifacts, artifact_types, observations, and users.
-- It joins these tables to gather comprehensive information about artifacts and related observations.
-- The query selects various columns from these tables, such as artifact properties, observation details,
-- and user information, and aliases some columns for clarity.
-- This query is used to collect data for further processing in the Postgres2Parquet Lambda Function (lambda_function.py).

SELECT
    artifacts.id,
    artifacts.obj_id,
    artifacts.artifact_type_id,
    artifacts.sighting_obj_id,
    artifacts.observation_id,
    artifacts.user_label_foot,
    artifacts.s3_image_name,
    artifacts.expert_label_rating,
    artifacts.expert_label_foot,
    artifacts.user_comments AS artifact_user_comments,
    artifacts.expert_comments AS artifact_expert_comments,
    artifacts.expert_reviewed_at,
    artifacts.expert_modified_at,
    artifacts.expert_reviewed,
    artifacts.taken_at,
    artifact_types.name,
    observations.uploaded_at,
    observations.location_latitude,
    observations.location_longitude,
    observations.location_name,
    observations.location_accuracy,
    observations.location_utm_northing,
    observations.location_utm_easting,
    observations.location_utm_zone,
    observations.user_label_animal_id,
    observations.user_label_animal_name,
    observations.user_label_captive_wild,
    observations.user_label_dob,
    observations.user_label_known_individual,
    observations.user_label_sex,
    observations.user_label_species_name,
    observations.user_label_species_id,
    observations.source,
    observations.expert_label_animal_name,
    observations.expert_label_sex,
    observations.expert_label_species_name,
    observations.expert_label_species_id,
    observations.captive_wild,
    observations.known_individual,
    observations.individual_multiple,
    observations.potential_individuals,
    observations.user_comments,
    observations.expert_comments,
    users.first_name,
    users.last_name,
    users.email,
    users.organization,
    users.academic_affiliation
FROM
    artifacts
INNER JOIN
    artifact_types ON artifacts.artifact_type_id = artifact_types.id
INNER JOIN
    observations ON artifacts.observation_id = observations.id
INNER JOIN
    users ON observations.user_id = users.id
INNER JOIN
    species ON observations.user_label_species_id = species.id;
