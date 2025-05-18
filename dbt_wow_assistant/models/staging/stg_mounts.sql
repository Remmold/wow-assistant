-- dbt_project/models/staging/stg_mounts.sql

with raw as (
    select * from {{ source('raw', 'mounts') }}
)

select
    id,
    name,
    creature_displays,
    requirements,
from raw