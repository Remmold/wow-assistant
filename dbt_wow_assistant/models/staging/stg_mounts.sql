with raw as (
    select * from {{ source('raw', 'mounts') }}
)

select
    id,
    name__en_us as name,
    description__en_us as description,
    source__type,
    source__name__en_us as source_name,
    faction__type,
    faction__name__en_us as faction_name,
    requirements__faction__type as faction_requirement,
    requirements__faction__name__en_us as faction_requirement_name,
    should_exclude_if_uncollected as is_unobtainable_or_faction_specific,
    _dlt_load_id,
    _dlt_id
from raw
