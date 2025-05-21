select
  id,
  name__en_us as name,
  description__en_us as description,
  instance__id as instance_id,
  instance__name__en_us as instance_name,
  category__type as instance_type,
  faction__type as faction_type,
  _dlt_load_id,
  _dlt_id,
from raw.journal_encounters