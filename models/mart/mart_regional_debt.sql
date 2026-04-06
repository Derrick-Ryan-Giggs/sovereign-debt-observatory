{{
    config(
        materialized='table',
        schema='mart',
        cluster_by=["region", "series_code"]
    )
}}

with base as (
    select
        country_code,
        country_name,
        series_code,
        series_description,
        year,
        debt_value_usd
    from {{ ref('stg_jedh') }}
),

with_regions as (
    select
        b.*,
        case
            when country_code in (
                'DZA','AGO','BEN','BWA','BFA','BDI','CMR','CPV','CAF','TCD',
                'COM','COD','COG','CIV','DJI','EGY','GNQ','ERI','ETH','GAB',
                'GMB','GHA','GIN','GNB','KEN','LSO','LBR','LBY','MDG','MWI',
                'MLI','MRT','MUS','MAR','MOZ','NAM','NER','NGA','RWA','STP',
                'SEN','SLE','SOM','ZAF','SSD','SDN','SWZ','TZA','TGO','TUN',
                'UGA','ZMB','ZWE'
            ) then 'Africa'
            when country_code in (
                'ARG','BOL','BRA','CHL','COL','CRI','CUB','DOM','ECU','SLV',
                'GTM','HTI','HND','JAM','MEX','NIC','PAN','PRY','PER','TTO',
                'URY','VEN'
            ) then 'Latin America and Caribbean'
            when country_code in (
                'CHN','IDN','KHM','LAO','MYS','MMR','PHL','THA','VNM','PNG',
                'FJI','MNG','PRK','KOR','JPN','HKG','SGP','BRN','TLS'
            ) then 'East Asia and Pacific'
            when country_code in (
                'AFG','BGD','BTN','IND','MDV','NPL','PAK','LKA'
            ) then 'South Asia'
            when country_code in (
                'ARM','AZE','BLR','GEO','KAZ','KGZ','MDA','RUS','TJK',
                'TKM','UKR','UZB','ALB','BIH','HRV','MKD','MNE','SRB','SVN',
                'POL','CZE','SVK','HUN','ROU','BGR','EST','LVA','LTU'
            ) then 'Europe and Central Asia'
            when country_code in (
                'DZA','BHR','DJI','EGY','IRN','IRQ','JOR','KWT','LBN','LBY',
                'MLT','MAR','OMN','QAT','SAU','SYR','TUN','ARE','YEM','PSE'
            ) then 'Middle East and North Africa'
            else 'Other'
        end as region
    from base b
),

aggregated as (
    select
        region,
        series_code,
        series_description,
        year,
        count(distinct country_code)        as country_count,
        sum(debt_value_usd)                 as total_debt_usd,
        avg(debt_value_usd)                 as avg_debt_usd,
        max(debt_value_usd)                 as max_debt_usd,
        min(debt_value_usd)                 as min_debt_usd
    from with_regions
    where region != 'Other'
    group by 1, 2, 3, 4
)

select * from aggregated