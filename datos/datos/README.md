# Dataset: viajes en el Metro de Medellín

`viajes_metro.csv` tiene **3.264 viajes** calculados con el sistema de la actividad anterior (`ruta_metro.py`).

## Cómo se construyó

`generar_dataset.py` prueba **todas las combinaciones**:

> 17 estaciones de origen × 16 destinos × lluvia (sí/no) × hora pico (sí/no) × 3 perfiles = **3.264 viajes**

Para cada viaje, `ruta_metro.py` aplica sus reglas y la búsqueda A\* para decir qué ruta tomar, cuántas paradas hace, si transborda o camina y cuántos minutos tarda. Al tiempo se le aplica una variación de ±10 %, porque en la vida real ningún viaje dura exactamente lo mismo.

```bash
python generar_dataset.py
```

## Columnas

| Columna | Descripción |
|---|---|
| `origen`, `destino` | Estaciones de inicio y fin del viaje |
| `lluvia` | 1 = llueve, 0 = no llueve |
| `hora_pico` | 1 = hora pico, 0 = no |
| `perfil` | normal, pocos_transbordos o movilidad_reducida |
| `ruta` | Estaciones por las que pasa el viaje |
| `paradas` | Estaciones recorridas en metro |
| `transbordos` | Cambios de tren en San Antonio (0 o 1) |
| `camina` | 1 si camina de Alpujarra a Cisneros |
| `minutos` | Duración del viaje |
| `tipo_ruta` | directa, transbordo o caminata |
| `minutos_disponibles` | Tiempo que tenía el viajero para llegar (5 a 45 min, al azar) |
| `llega_a_tiempo` | 1 si `minutos` ≤ `minutos_disponibles`, 0 si no |
