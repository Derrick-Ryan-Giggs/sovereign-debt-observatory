{{
    config(
        materialized='view',
        schema='staging'
    )
}}

with source as (
    select *
    from {{ source('raw_jedh', 'jedh') }}
    where extracted_at = (
        select max(extracted_at)
        from {{ source('raw_jedh', 'jedh') }}
    )
),

unpivoted as (
    select
        economy                                      as country_code,
        Country                                      as country_name,
        series_code,
        extracted_at,
        year,
        cast(nullif(value, 'nan') as float64)        as debt_value_usd
    from source
    unpivot(
        value for year in (
            year_1998, year_1999, year_2000, year_2001, year_2002,
            year_2003, year_2004, year_2005, year_2006, year_2007,
            year_2008, year_2009, year_2010, year_2011, year_2012,
            year_2013, year_2014, year_2015, year_2016, year_2017,
            year_2018, year_2019, year_2020, year_2021, year_2022,
            year_2023, year_2024, year_2025
        )
    )
),

final as (
    select
        country_code,
        country_name,
        series_code,
        cast(replace(year, 'year_', '') as int64)    as year,
        debt_value_usd,
        extracted_at,
        case
            when series_code = 'DT.DOD.DECT.CD' then 'Total external debt stocks'
            when series_code = 'DT.DOD.DLXF.CD' then 'Long-term external debt'
            when series_code = 'DT.DOD.DPNG.CD' then 'Private nonguaranteed debt'
            when series_code = 'DT.DOD.MIBR.CD' then 'PPG IBRD loans'
            when series_code = 'DT.DOD.DPPG.CD' then 'Public and publicly guaranteed debt'
            when series_code = 'DT.DOD.DIMF.CD' then 'IMF credit'
            when series_code = 'DT.DOD.PVLX.CD' then 'Present value of external debt'
            when series_code = 'DT.DOD.MWBG.CD' then 'IBRD loans and IDA credits'
            when series_code = 'DT.DOD.MIDA.CD' then 'PPG IDA loans'
            else series_code
        end                                          as series_description
    from unpivoted
    where country_code is not null
        and country_code != 'nan'
        and debt_value_usd is not null
        and length(country_code) = 3
        and country_code not in (
            'LMY', 'MIC', 'UMC', 'LMC', 'LIC',
            'EAP', 'ECA', 'LAC', 'MNA', 'SAS',
            'SSA', 'SSF', 'HIC', 'OED', 'EMU',
            'ARB', 'CEB', 'EAR', 'ECS', 'HPC',
            'IBD', 'IBT', 'IDA', 'IDX', 'LDC',
            'PRE', 'PSS', 'PST', 'TEA', 'TEC',
            'TLA', 'TMN', 'TSA', 'TSS', 'WLD'
        )
)

select * from final