-- models/mrt/mart_markert.sql


WITH mart_markert AS (
    SELECT
	fm.connected_realm_id AS realm_group_id,
	fm.realm_id,
	dr.name,
	di.name,
	da.buyout,
	da.bid,
	da.quantity,
	da.time_left,
	di.quality_name,
	di.media_id,
    di.sell_price,
    di.item_class_name,
    di.item_subclass_name,
FROM {{ref('fct_market')}} AS fm

LEFT JOIN {{ref(('dim_auctions'))}} AS da
	ON da.id = fm.auction_id

LEFT JOIN {{ref('dim_items')}} AS di
	ON di.id = fm.item_id

LEFT JOIN {{ref('dim_realms')}} AS dr
	ON dr.id = fm.realm_id
    )

SELECT * FROM mart_markert