# Recomendaciones técnicas para máquina de vending de agua (Raspberry Pi 3B+)

## 1) Lenguaje recomendado
Para tu caso (confiabilidad + GPIO nativo + interfaz kiosko), la opción más equilibrada es:

- **Backend y control de hardware: Python 3**
  - Muy buen soporte en Raspberry Pi OS Bookworm.
  - Acceso sencillo y nativo a GPIO con bibliotecas como `gpiozero` y `lgpio`.
  - Ecosistema maduro para UART/serial, MDB/ccTalk (según monedero) e integración de periféricos.

Si quieres máxima robustez en procesos críticos, puedes evolucionar luego a:

- **Servicio crítico en Rust** (dispensado/estado), y mantener Python para UI y configuración.

## 2) Arquitectura recomendada (confiable)
Separar responsabilidades en servicios independientes:

- **`vending-core`** (servicio systemd): lógica de estados de la máquina.
- **`io-gpio`**: control de bombas/válvulas/relevadores/sensores.
- **`coin-service`**: lectura y validación de monedero electrónico.
- **`ui-kiosk`**: interfaz táctil en pantalla HDMI de 7".
- **`config-service`**: ajustes guiados por botones físicos.

Patrones clave:

- Máquina de estados explícita (`IDLE`, `ESPERANDO_MONEDA`, `CREDITADO`, `DOSIFICANDO`, `ERROR`, `MANTENIMIENTO`).
- **Watchdog** de systemd y reintento automático.
- Registro de eventos (JSONL) + rotación de logs.
- Modo degradado seguro (si falla UI, no habilitar dispensado sin control).

## 3) Monedero electrónico
Primero identifica protocolo del equipo:

- **MDB** (común en vending profesional).
- **ccTalk** (común en validadores/aceptadores).
- **Pulso** (más simple, menos telemetría).

Recomendación:

- Integrar por **UART/USB-serial** con aislamiento eléctrico.
- Ejecutar parser/protocolo en proceso separado (`coin-service`).
- Publicar eventos de crédito por cola local (ej. `asyncio.Queue` o ZeroMQ local).
- Registrar cada inserción/aceptación/rechazo para auditoría.

## 4) Interfaz adaptativa + modo kiosko
Para una pantalla 7" HDMI:

- UI web local en **FastAPI + frontend responsivo** (o Flask + frontend simple).
- Ejecutar en Chromium en modo kiosko:
  - `--kiosk --incognito --noerrdialogs --disable-infobars`
- Arranque automático con `systemd` (sin depender de sesión manual).
- Diseño táctil:
  - Botones grandes, alto contraste, flujo corto, mensajes claros.

## 5) Configuración sencilla por botones
Implementar un "menú técnico" por botones físicos:

- Botón 1: subir
- Botón 2: bajar
- Botón 3: aceptar
- Botón 4: volver

Configurable:

- Precio por litro/servicio.
- Tiempo o volumen de dispensado.
- Calibración de flujo.
- Habilitar/deshabilitar monedero.
- Modo mantenimiento.

Guardar parámetros en:

- `config.yaml` con versión y validación de esquema.
- Backup automático al cambiar configuración.

## 6) Stack concreto sugerido (inicio rápido)

- **Lenguaje**: Python 3.11+
- **GPIO**: `gpiozero` + backend `lgpio`
- **Backend**: FastAPI
- **UI**: HTML/CSS/JS responsive (sin framework pesado al inicio)
- **Servicios**: `systemd`
- **Persistencia**: SQLite (ventas/eventos) + YAML (config)
- **Monedero**: servicio serial dedicado (MDB/ccTalk según hardware)

## 7) Buenas prácticas de confiabilidad para vending

- Fuente de poder industrial, protección contra ruido y rebotes.
- Relevadores/SSR con aislamiento y diodos de protección.
- `ReadOnly` parcial del sistema + partición de datos separada.
- Heartbeat entre servicios (UI/core/coin).
- Pruebas de corte eléctrico y recuperación automática.

## 8) Respuesta corta a tu pregunta principal

- **¿En qué lenguaje?** → **Python** (mejor equilibrio facilidad/tiempo/soporte GPIO en Raspberry Pi).
- **¿Confiable?** → Sí, si lo montas con **arquitectura por servicios + systemd + máquina de estados**.
- **¿GPIO fácil y nativo?** → Sí, con `gpiozero`/`lgpio`.
- **¿Monedero electrónico?** → Sí, integrando protocolo `MDB` o `ccTalk` en servicio dedicado.
- **¿Interfaz adaptativa y kiosko?** → Sí, UI web local + Chromium kiosko.
- **¿Configuración por botones?** → Sí, menú técnico en GPIO con guardado en YAML.
