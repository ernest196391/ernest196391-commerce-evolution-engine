# Piloto: Casa Viva (18 de noviembre de 2026)

**Tipo:** revisión textual de páginas públicas. No es todavía una ejecución Playwright ni una certificación de diseño móvil.

## Alcance
- https://casaviva.company/
- https://casaviva.company/producto/ventilador-recargable-20000-mah/
- https://casaviva.company/producto/ventilador-recargable-de-pedestal-milexus/

## Observaciones verificables en el texto público

### Ventilador recargable 20000 mAh
El encabezado destaca 20.000 mAh, pero la ficha accesible pública solo incluye como características generales que es recargable, la capacidad de batería y que funciona durante cortes eléctricos; no especifica marca, modelo o autonomía por velocidad en la descripción publicada.

**Acción propuesta:** pedir datos auténticos de modelo, autonomía por velocidad, tamaño, voltaje y componentes. No inventar estos datos. Preparar una ficha mejorada solo cuando haya evidencia.

### Ventilador Milexus
La ficha incluye 8.000 mAh, hasta 20 horas, 3 velocidades, LED y USB; no explica condiciones de ensayo o velocidad de la autonomía declarada.

**Acción propuesta:** solicitar ficha original y contexto de la autonomía (velocidad, iluminación, carga); si no se conoce, etiquetar «anunciada, condiciones no verificadas» y no presentar horas como garantía.

### Portada
Hay nombres como «Depiladora portatil de cejas» y «Protector de colchón king», cuya ortografía, medidas o especificidad requieren revisión editorial.

**Acción propuesta:** normalizar nombre, marca/modelo/presentación cuando esté corroborado; no transformar cambios de título en atributos inventados.

## Conclusión
Rellenar campos no equivale a calidad. La heurística CSV actual no evalúa precisión técnica, promesas condicionadas, estética ni confianza. El siguiente sistema necesita distinguir verificación de datos, redacción y experiencia visual.

## Estado de la ejecución
- Lectura de páginas públicas: realizada.
- Pruebas unitarias de v0.1: ejecutadas localmente en el entorno de preparación (4 aprobadas).
- Capturas Playwright contra estas tres URLs: **pendientes**.
- Cambios en productos, precios, fichas o imágenes: **ninguno**.
