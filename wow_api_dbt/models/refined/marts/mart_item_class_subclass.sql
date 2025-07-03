SELECT DISTINCT
    item_class_name,
    item_subclass_name,
    item_type
FROM {{ ref('dim_items') }}
WHERE item_class_name IS NOT NULL
    AND item_subclass_name IS NOT NULL
ORDER BY item_class_name