-- models/marts/mart_items.sql


WITH mart_items AS (
    SELECT
		di.id,
        di.name AS item_name,
        di.item_level,
        di.required_level,
        di.vendor_purchase_price,
        di.vendor_sell_price,
        di.item_class_id,
        di.item_class_name,
        di.item_subclass_id,
        di.item_subclass_name,
        di.item_type,
        di.rarity_name,
        di.is_equippable,
        di.is_stackable,
        di.max_stack_size,
        di.icon_hrf AS icon_href
FROM {{ ref('dim_items') }} AS di
    )

SELECT * FROM mart_items