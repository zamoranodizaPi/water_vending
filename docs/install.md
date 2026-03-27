# Instalación

## Requisitos
- Raspberry Pi 3B+ o superior
- Raspberry Pi OS actualizado
- Pantalla táctil compatible con PyQt5
- Conexión a red para correo y actualizaciones
- Sensor de nivel, monedero, válvulas, LEDs y botones conectados al header GPIO definido en `README.md`

## Instalación Paso a Paso
1. Clonar el proyecto:
   ```bash
   git clone https://github.com/zamoranodizaPi/water_vending.git
   cd water_vending
   ```
2. Ejecutar instalador:
   ```bash
   chmod +x install.sh
   ./install.sh
   ```
3. Verificar servicio:
   ```bash
   systemctl status vending.service
   ```
4. Verificar que `pigpiod` esté activo:
   ```bash
   systemctl status pigpiod
   ```

## Configuración Inicial
- Ajustar `config/runtime_settings.json` para precios, volúmenes, tema y datos de contacto.
- Ajustar `deploy/vending_email.env` para SMTP/IMAP.
- Reiniciar el servicio si cambia la configuración:
  ```bash
  sudo systemctl restart vending.service
  ```

## Solución de Problemas
- Si la UI no inicia, revisar:
  ```bash
  journalctl -u vending.service -n 200 --no-pager
  ```
- Si no hay GPIO reales, revisar que `pigpiod` esté activo.
- Si el correo no responde, validar `SMTP/IMAP` y conectividad de red.
- Si no hay audio o imágenes, revisar `assets/` y permisos en `/opt/water_vending`.
