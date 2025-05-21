Select 
  id,
  name__en_us as name,
  map__name__en_us as map_name,
  map__id as map_id,
  description__en_us as description,
  expansion__id as expansion_id,
  expansion__name__en_us as expansion_name,
  location__name__en_us as location_name,
  location__id as location_id,
  media__id as media_id,
  minimum_level,
  category__type as category_type,
  order_index,
  area__name__en_us as area_name,
  area__id as area_id,
  _dlt_load_id,
  _dlt_id
From
  raw.journal_instances
  