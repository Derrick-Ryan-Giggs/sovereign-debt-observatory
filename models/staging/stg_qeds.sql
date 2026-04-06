{{
    config(
        materialized='view',
        schema='staging'
    )
}}

with source as (
    select *
    from {{ source('raw_qeds', 'qeds') }}
    where extracted_at = (
        select max(extracted_at)
        from {{ source('raw_qeds', 'qeds') }}
    )
),

cleaned as (
    select
        country_name,
        country_code,
        series_name,
        series_code,
        scale_precision,
        source_table,
        sheet_name,
        extracted_at,
        safe_cast(q_2021q1 as float64)    as q_2021q1,
        safe_cast(q_2021q2 as float64)    as q_2021q2,
        safe_cast(q_2021q3 as float64)    as q_2021q3,
        safe_cast(q_2021q4 as float64)    as q_2021q4,
        safe_cast(q_2022q3 as float64)    as q_2022q3
    from source
    where country_code is not null
        and country_name is not null
        and series_code is not null
)

select * from cleaned