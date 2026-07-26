/*
Crédito al sector privado no financiero.

Fuentes:
  - total_mn_y_me (ID 26): préstamos en moneda nacional Y extranjera.
  - Componentes (IDs 110-116): solo moneda nacional.
  - La diferencia (~25%) corresponde a préstamos en moneda extranjera (USD)
    que el BCRA no publica desglosados por tipo en esta API.

Metodología verificada en: api.bcra.gob.ar/estadisticas/v4.0/metodologia/{id}
*/

with total_mn_y_me as (
    select fecha, valor as total_mn_y_me
    from {{ ref('stg_bcra_variables') }}
    where nombre_variable = 'prestamos_sector_privado'
),

desglose as (
    select
        fecha,
        max(case when nombre_variable = 'prestamos_adelantos_cuenta'  then valor end) as adelantos_cuenta,
        max(case when nombre_variable = 'prestamos_documentos'         then valor end) as documentos,
        max(case when nombre_variable = 'prestamos_hipotecarios'       then valor end) as hipotecarios,
        max(case when nombre_variable = 'prestamos_prendarios'         then valor end) as prendarios,
        max(case when nombre_variable = 'prestamos_personales'         then valor end) as personales,
        max(case when nombre_variable = 'prestamos_tarjeta_credito'    then valor end) as tarjeta_credito,
        max(case when nombre_variable = 'prestamos_otros'              then valor end) as otros
    from {{ ref('stg_bcra_variables') }}
    where nombre_variable in (
        'prestamos_adelantos_cuenta',
        'prestamos_documentos',
        'prestamos_hipotecarios',
        'prestamos_prendarios',
        'prestamos_personales',
        'prestamos_tarjeta_credito',
        'prestamos_otros'
    )
    group by fecha
),

joined as (
    select
        d.fecha,
        t.total_mn_y_me,
        d.adelantos_cuenta + d.documentos + d.hipotecarios
            + d.prendarios + d.personales + d.tarjeta_credito
            + d.otros                                                   as total_mn,
        t.total_mn_y_me - (
            d.adelantos_cuenta + d.documentos + d.hipotecarios
            + d.prendarios + d.personales + d.tarjeta_credito + d.otros
        )                                                               as estimado_me,
        d.adelantos_cuenta,
        d.documentos,
        d.hipotecarios,
        d.prendarios,
        d.personales,
        d.tarjeta_credito,
        d.otros,
        round(d.hipotecarios    / t.total_mn_y_me * 100, 2)            as pct_hipotecarios,
        round(d.personales      / t.total_mn_y_me * 100, 2)            as pct_personales,
        round(d.tarjeta_credito / t.total_mn_y_me * 100, 2)            as pct_tarjeta_credito,
        round(
            (t.total_mn_y_me - (
                d.adelantos_cuenta + d.documentos + d.hipotecarios
                + d.prendarios + d.personales + d.tarjeta_credito + d.otros
            )) / t.total_mn_y_me * 100
        , 2)                                                            as pct_estimado_me,
        round(
            (t.total_mn_y_me - lag(t.total_mn_y_me, 30) over (order by d.fecha))
            / lag(t.total_mn_y_me, 30) over (order by d.fecha) * 100
        , 2)                                                            as var_total_30d_pct
    from desglose d
    inner join total_mn_y_me t on d.fecha = t.fecha
)

select * from joined
order by fecha