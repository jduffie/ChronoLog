DROP VIEW IF EXISTS public.cartridge_details;

CREATE VIEW public.cartridge_details AS
SELECT
    f.id                                   AS spec_id,
    'factory'                              AS source,
    f.cartridge_type,
    f.make                                 AS manufacturer,      -- spec (factory)
    f.model                                AS model,             -- spec (factory)
    f.bullet_id,

    -- Bullet display label: "<manufacturer> <model> <weight> gr <bore_land> mm"
    CONCAT_WS(' ',
        COALESCE(NULLIF(TRIM(CONCAT_WS(' ', b.manufacturer, b.model)), ''), 'Unknown'),
        CONCAT_WS(' ', b.weight_grains::text, 'gr'),
        CONCAT_WS(' ', ROUND(b.bore_diameter_land_mm::numeric, 3)::text, 'mm')
    )                                      AS bullet_name,

    -- Bullet details (from public.bullets)
    b.manufacturer                         AS bullet_manufacturer,
    b.model                                AS bullet_model,
    b.weight_grains                        AS bullet_weight_grains,
    b.bullet_diameter_groove_mm,
    b.bore_diameter_land_mm,
    b.bullet_length_mm,
    b.ballistic_coefficient_g1,
    b.ballistic_coefficient_g7,
    b.sectional_density,
    b.min_req_twist_rate_in_per_rev,
    b.pref_twist_rate_in_per_rev

FROM public.factory_cartridge_specs f
LEFT JOIN public.bullets b ON b.id = f.bullet_id

UNION ALL

SELECT
    c.id                                   AS spec_id,
    'custom'                               AS source,
    c.cartridge_type,
    NULL                                   AS manufacturer,       -- no 'make' in custom spec
    c.name                                 AS model,              -- spec (custom)
    c.bullet_id,

    CONCAT_WS(' ',
        COALESCE(NULLIF(TRIM(CONCAT_WS(' ', b.manufacturer, b.model)), ''), 'Unknown'),
        CONCAT_WS(' ', b.weight_grains::text, 'gr'),
        CONCAT_WS(' ', ROUND(b.bore_diameter_land_mm::numeric, 3)::text, 'mm')
    )                                      AS bullet_name,

    b.manufacturer                         AS bullet_manufacturer,
    b.model                                AS bullet_model,
    b.weight_grains                        AS bullet_weight_grains,
    b.bullet_diameter_groove_mm,
    b.bore_diameter_land_mm,
    b.bullet_length_mm,
    b.ballistic_coefficient_g1,
    b.ballistic_coefficient_g7,
    b.sectional_density,
    b.min_req_twist_rate_in_per_rev,
    b.pref_twist_rate_in_per_rev

FROM public.custom_cartridge_specs c
LEFT JOIN public.bullets b ON b.id = c.bullet_id;