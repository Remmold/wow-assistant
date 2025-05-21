SELECT
  c.id AS creature_id,
  c.name__en_us as name,
  c.creature_display__id,
  c.description__en_us AS description,
  e.id AS encounter_id,
  c._dlt_id,
  c._dlt_list_idx
FROM raw.journal_encounters__creatures c
JOIN raw.journal_encounters e
  ON c._dlt_parent_id = e._dlt_id