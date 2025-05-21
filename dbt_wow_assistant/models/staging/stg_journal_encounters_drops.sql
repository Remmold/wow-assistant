select
  d.item__id as item_id,
  d.item__name__en_us as item_name,
  e.id as encounter_id,
  e.name__en_us as encounter_name,
  d._dlt_parent_id,  -- optional
  d._dlt_id          -- optional
from raw.journal_encounters__items d
join raw.journal_encounters e
  on d._dlt_parent_id = e._dlt_id