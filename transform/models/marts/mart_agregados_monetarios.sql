with base_monetaria as (
    select fecha, valor as base_monetaria
    from {{ ref('stg_bcra_variables') }}
    where nombre_variable = 'base_monetaria'
),

m2 as (
    select fecha, valor as m2
    from {{ ref('stg_bcra_variables') }}
    where nombre_variable = 'm2'
),

joined as (
    select
        bm.fecha,
        bm.base_monetaria,
        m2.m2,
        round(m2.m2 / bm.base_monetaria, 2)                          as multiplicador_monetario,
        round(
            (bm.base_monetaria - lag(bm.base_monetaria, 30)
                over (order by bm.fecha))
            / lag(bm.base_monetaria, 30) over (order by bm.fecha) * 100
        , 2)                                                           as var_bm_30d_pct,
        round(
            (m2.m2 - lag(m2.m2, 30) over (order by bm.fecha))
            / lag(m2.m2, 30) over (order by bm.fecha) * 100
        , 2)                                                           as var_m2_30d_pct
    from base_monetaria bm
    inner join m2
        on bm.fecha = m2.fecha
)

select * from joined
order by fecha