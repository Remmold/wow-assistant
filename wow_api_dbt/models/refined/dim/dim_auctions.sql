-- models/refined/dim/dim_auctions.sql

SELECT
  id,
  item__id AS item_id,
  bid,
  buyout,
  quantity,
  time_left,
  item__pet_breed_id AS battlepet_breed_id,
  item__pet_level AS battlepet_level,
  item__pet_quality_id AS battlepet_quality_id,
  item__pet_species_id AS battlepet_species,
  realm_id as realm_group_id,
FROM {{ source('raw_auctions', 'auctions') }}

