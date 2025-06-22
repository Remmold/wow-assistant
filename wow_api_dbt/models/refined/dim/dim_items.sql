-- models/refined/dim/dim_items.sql

SELECT
    id,
    name__en_us AS name,
    level as item_level,
    required_level,
    purchase_price as vendor_purchase_price,
    sell_price as vendor_sell_price,
    item_class__id AS item_class_id,
    item_class__name__en_us AS item_class_name,
    item_subclass__id AS item_subclass_id,
    item_subclass__name__en_us AS item_subclass_name,
    inventory_type__name__en_us AS item_type,
    quality__name__en_us AS rarity_name,
    is_equippable,
    is_stackable,
    max_count AS max_stack_size,
    media__id AS media_id,
FROM {{ source('raw', 'items') }}
