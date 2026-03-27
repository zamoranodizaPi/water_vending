# Water Vending

Sistema comercial para vending de agua purificada en Raspberry Pi con interfaz PyQt5, control GPIO, auditoría local y por email, trazabilidad semanal y build reproducible.

Versión estable actual: `v1.0.0`

## Estructura

```text
water_vending/
├── app/
├── hardware/
├── ui/
├── services/
├── config/
├── logs/
├── docs/
├── dist/
├── main.py
├── config.json
├── install.sh
└── systemd/vending.service
```

## Funciones
- Selección de producto por pantalla o botones físicos.
- Monedero por pulsos.
- Flujo de llenado con enjuague automático cuando aplica.
- Auditoría local protegida por código.
- Respuesta por correo para auditoría y logs.
- Alertas automáticas por falta de agua.
- Trazabilidad semanal en `logs/ui-YYYY-Www.log`.
- Exportación de auditorías CSV y logs desde línea de comandos.

## Mapa GPIO
- GPIO 12: pulsos del monedero
- GPIO 16: selección 1 galón
- GPIO 20: selección medio garrafón
- GPIO 21: selección garrafón completo
- GPIO 13: botón OK
- Pin físico 29 / GPIO 5: paro de emergencia
- GPIO 23: LED botón garrafón completo
- GPIO 24: LED botón medio garrafón
- GPIO 25: LED botón galón
- GPIO 8: LED botón OK
- GPIO 7: LED botón paro
- GPIO 17: válvula de llenado
- GPIO 22: válvula de enjuague
- GPIO 27: luz de cortesía
- GPIO 26: lámpara UV
- GPIO 6: ozono

## Comandos Rápidos
- Ejecutar UI:
  ```bash
  python main.py
  ```
- Exportar auditorías CSV:
  ```bash
  python main.py --export-audit-csv ./exports
  ```
- Exportar logs:
  ```bash
  python main.py --export-logs ./exports/logs
  ```
- Exportar todo:
  ```bash
  python main.py --export-all ./exports
  ```
- Ver versión:
  ```bash
  python main.py --version
  ```

## Instalación
Ver [install.md](/Users/diza/Documents/water_vending/docs/install.md).

## Manuales
- [user_manual.md](/Users/diza/Documents/water_vending/docs/user_manual.md)
- [technical.md](/Users/diza/Documents/water_vending/docs/technical.md)

## Contacto
- Correo configurado por defecto: `zamoranodiza@hotmail.com`
