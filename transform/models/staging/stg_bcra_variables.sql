with source as (
    select
        variable,
        fecha,
        valor,
        ingested_at
    from raw_bcra
),

renamed as (
    select
        variable                       as nombre_variable,
        cast(fecha as date)            as fecha,
        cast(valor as double)          as valor,
        cast(ingested_at as timestamp) as cargado_en
    from source
)

select * from renamed