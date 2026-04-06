{{
    config(
        materialized='table',
        schema='mart',
        cluster_by=["country_code", "source_table"]
    )
}}

with base as (
    select
        country_code,
        country_name,
        series_name,
        series_code,
        source_table,
        extracted_at,
        q_2021q1,
        q_2021q2,
        q_2021q3,
        q_2021q4,
        q_2022q3
    from {{ ref('stg_qeds') }}
),

with_totals as (
    select
        country_code,
        country_name,
        series_name,
        series_code,
        source_table,
        extracted_at,
        q_2021q1,
        q_2021q2,
        q_2021q3,
        q_2021q4,
        q_2022q3,
        coalesce(q_2021q1, 0) +
        coalesce(q_2021q2, 0) +
        coalesce(q_2021q3, 0) +
        coalesce(q_2021q4, 0)               as total_2021_payments,
        safe_divide(
            coalesce(q_2021q1, 0) +
            coalesce(q_2021q2, 0) +
            coalesce(q_2021q3, 0) +
            coalesce(q_2021q4, 0),
            4
        )                                   as avg_quarterly_payment_2021
    from base
)

select * from with_totals