# Arquitectura operativa (versión inicial)

## Entradas físicas

- Botón `FULL`: seleccionar garrafón completo.
- Botón `HALF`: seleccionar medio garrafón.
- Botón `GALLON`: seleccionar galón.
- Botón `OK`: iniciar llenado cuando hay crédito suficiente.
- Botón `RINSE`: ciclo de enjuague.
- Botón `EMERGENCY_STOP`: corte inmediato.
- Monedero de pulso: monedas de 1, 2, 5 y 10.
- Sensor de flujo: conteo para control de volumen/tiempo.
- Sensor de puerta: luz interior automática.

## Salidas físicas

- Electroválvula de llenado.
- Electroválvula de enjuague.
- Luz interior (puerta abierta).
- Lámpara UV (activa durante llenado).
- Máquina de ozono (activa al finalizar llenado).

## Reglas de seguridad incluidas

1. El paro de emergencia desactiva válvulas, UV y ozono.
2. UV nunca activa en enjuague.
3. Ozono solo activa al finalizar llenado.
4. Luz interior depende del sensor de puerta.

## Modo kiosko (sin touch)

- La pantalla solo muestra estado/instrucciones.
- La interacción se realiza por botonera física.
- Recomendado en producción:
  - FastAPI + Chromium `--kiosk`.
  - Arranque por `systemd` con `Restart=always`.
