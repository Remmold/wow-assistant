-- models/marts/mart_market.sql


WITH mart_market AS (
    SELECT
		fm.auction_id,
		fm.realm_group_id,
		dr.realm_name,
		di.id as item_id,
		di.name AS item_name,
		da.bid,
		da.buyout,
		da.quantity,
		da.time_left,
		di.rarity_name,
		di.media_id,
		di.vendor_sell_price,
		di.vendor_purchase_price,
		di.item_class_name,
		di.item_subclass_name,
		di.item_type,
		di.item_level,
		di.required_level,
		da.battlepet_breed_id,
		da.battlepet_level,
		da.battlepet_quality_id,
		da.battlepet_species,
FROM {{ref('fct_market')}} AS fm

LEFT JOIN {{ref(('dim_auctions'))}} AS da
	ON da.id = fm.auction_id

LEFT JOIN {{ref('dim_items')}} AS di
	ON di.id = fm.item_id

LEFT JOIN {{ref('dim_realms')}} AS dr
	ON dr.realm_group_id = fm.realm_group_id
    )

SELECT * FROM mart_market