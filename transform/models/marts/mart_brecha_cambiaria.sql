with oficial as (
    select
        fecha,
        valor as tipo_cambio_oficial
    from {{ ref('stg_bcra_variables') }}
    where nombre_variable = 'tipo_cambio_minorista'
),

blue as (
    select
        fecha,
        valor as tipo_cambio_blue
    from {{ ref('stg_bcra_variables') }}
    where nombre_variable = 'dolar_blue'
),

joined as (
    select
        oficial.fecha,
        oficial.tipo_cambio_oficial,
        blue.tipo_cambio_blue,
        round(
            (blue.tipo_cambio_blue - oficial.tipo_cambio_oficial)
            / oficial.tipo_cambio_oficial * 100,
            2
        ) as brecha_pct
    from oficial
    inner join blue
        on oficial.fecha = blue.fecha
)

select * from joined
order by fecha