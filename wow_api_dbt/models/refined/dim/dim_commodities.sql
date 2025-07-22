-- models/refined/dim/dim_commodities.sql
SELECT 
  id,
  item__id AS item_id,
  quantity,
  unit_price,
  time_left,
FROM {{ source('raw_auctions', 'commodities') }}