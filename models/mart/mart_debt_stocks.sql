{{
    config(
        materialized='table',
        schema='mart',
        partition_by={
            "field": "year",
            "data_type": "int64",
            "range": {
                "start": 1998,
                "end": 2026,
                "interval": 1
            }
        },
        cluster_by=["country_code", "series_code"]
    )
}}

with base as (
    select
        country_code,
        country_name,
        series_code,
        series_description,
        year,
        debt_value_usd,
        extracted_at
    from {{ ref('stg_jedh') }}
),

with_ratios as (
    select
        b.*,
        total.debt_value_usd                            as total_debt_usd,
        safe_divide(
            b.debt_value_usd,
            total.debt_value_usd
        ) * 100                                         as pct_of_total_debt,
        lag(b.debt_value_usd) over (
            partition by b.country_code, b.series_code
            order by b.year
        )                                               as prev_year_value,
        safe_divide(
            b.debt_value_usd - lag(b.debt_value_usd) over (
                partition by b.country_code, b.series_code
                order by b.year
            ),
            lag(b.debt_value_usd) over (
                partition by b.country_code, b.series_code
                order by b.year
            )
        ) * 100                                         as yoy_change_pct
    from base b
    left join base total
        on  b.country_code = total.country_code
        and b.year = total.year
        and total.series_code = 'DT.DOD.DECT.CD'
)

select * from with_ratios