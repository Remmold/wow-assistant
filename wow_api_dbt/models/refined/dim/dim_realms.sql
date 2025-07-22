-- models/dim/dim_realms.sql

WITH connected_realms AS (
  SELECT 
    realm_data.id AS realm_group_id,
    rdr.id AS realm_id,
    rdr.name__en_us AS realm_name,
    rdr.region__id AS region_id,
    rdr.region__name__en_us AS region_name,
    rdr.category__en_us AS language,
    rdr.timezone,
    rdr.type__name__en_us AS type,
    realm_data.population__name__en_us AS population_status,
    realm_data.status__name__en_us AS server_status,
    realm_data.has_queue,
    realm_data.mythic_leaderboards__href,
    rdr.is_tournament
  FROM {{ source('raw_misc', 'realm_data') }} AS realm_data
  JOIN {{ source('raw_misc', 'realm_data__realms') }} AS rdr
    ON rdr._dlt_parent_id = realm_data._dlt_id
)

SELECT *
FROM connected_realms
