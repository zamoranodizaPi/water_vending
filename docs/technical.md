# Manual Técnico

## Arquitectura
- `main.py`: entrypoint de producción.
- `app/`: runtime, paths y metadatos de versión.
- `ui/`: pantallas PyQt5 y lógica de interacción.
- `hardware/`: GPIO, válvulas, monedero, LEDs, correo y sensores.
- `services/`: exportación operativa para auditoría y logs.
- `config/`: settings dinámicos y configuración persistente.
- `database/`: persistencia SQLite.

## GPIO
El mapa vigente está documentado en `README.md` y centralizado en `config/settings.py`.

## Flujo de Eventos
1. La UI arranca y configura hardware.
2. El monedero incrementa crédito.
3. El usuario selecciona producto.
4. La lógica valida crédito suficiente.
5. Se ejecuta enjuague si aplica.
6. Se abre válvula de llenado y se monitorea progreso.
7. Se registra venta, cambio y retorno a home.

## Integración de Hardware
- `gpiozero` abstrae pines de entrada/salida.
- `pigpio` mejora lectura del monedero cuando está disponible.
- `ValveController` y `AuxiliaryOutputs` coordinan llenado, UV, ozono y enjuague.

## Manejo de Errores
- Errores GPIO se registran por logger.
- El sistema mantiene trazabilidad semanal en `logs/ui-YYYY-Www.log`.
- El correo registra solicitudes, respuestas y estados de entrega.

## Exportación de Datos
- CSV:
  ```bash
  python main.py --export-audit-csv ./exports
  ```
- Logs:
  ```bash
  python main.py --export-logs ./exports/logs
  ```
