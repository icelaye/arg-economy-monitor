-- estimado_me nunca puede ser negativo.
-- Si lo es, la suma de componentes MN supera el total MN+ME, lo cual es imposible.
-- Nota: una diferencia de ~25% entre total y suma de componentes es esperada
-- porque el total (ID 26) incluye préstamos en moneda extranjera no publicados
-- por separado en esta API. Verificado en /metodologia/26.
select
    fecha,
    total_mn_y_me,
    total_mn,
    estimado_me
from {{ ref('mart_credito_sector_privado') }}
where estimado_me < 0