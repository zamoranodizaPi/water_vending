# Layout de interfaces

Base actual de la aplicacion: `1024 x 600 px`

Pantallas activas registradas en `ui/main_window.py`:
- `ProductScreen`
- `PromptScreen`
- `DispensingScreen`
- `MessageScreen`

Nota: `ui/screens.py` contiene pantallas simples de apoyo, pero no se agregan al `QStackedWidget` actual.

## 1. ProductScreen

### Estructura general
- Margen exterior: `18 px` izquierda y derecha, `12 px` arriba y `10 px` abajo
- Espaciado vertical principal: `8 px`
- Logo flotante superior derecha: contenedor `252 x 189 px`, imagen escalada a `231 x 174 px`
- Franja superior de titulo: `189 px` de alto, alineada verticalmente con el logo

### Zonas
- Encabezado principal centrado: texto a `38 px`
- Caja de credito:
  - Posicion Y efectiva: inicia inmediatamente despues del logo
  - Ancho fijo: `368 px`
  - Radio: `20 px`
  - Padding interno: `16 px` horizontal, `8 px` vertical
  - Icono moneda: `32 x 32 px`
  - Imagen moneda: `28 x 28 px`
  - Texto credito: `24 px`
- Alerta superior: `24 px`
- Titulo de seccion: `31 px`
- Grid de productos:
  - Columnas: `3`
  - Espaciado horizontal: `14 px`
  - Espaciado vertical: `10 px`
- Boton OK:
  - `420 x 67 px`
  - Texto: `30 px`
  - Radio: `12 px`

### Medidas por tarjeta de producto
- Padding interno: `13 px`
- Espaciado interno: `7 px`
- Estado normal o bloqueado:
  - Alto minimo: `170 px`
  - Imagen: `96 x 96 px`
  - Nombre: `19 px`
  - Volumen: `15 px`
  - Precio: `26 px`
  - Radio: `20 px`
  - Borde: `3 px`
- Estado seleccionado:
  - Alto minimo: `220 px`
  - Imagen: `124 x 124 px`
  - Nombre: `22 px`
  - Volumen: `17 px`
  - Precio: `32 px`
  - Radio: `24 px`
  - Borde: `4 px`

### Wireframe
```text
1024
+----------------------------------------------------------------------------------+
|                           Agua Purificada Lupita                 [Logo 252x189] |
|                                                                                  |
| [Credito 368x~48]                                                                |
|                              [Alerta opcional]                                   |
|                            [Seleccione producto]                                 |
|                                                                                  |
| [Tarjeta 1 ~316w] [14] [Tarjeta 2 ~316w] [14] [Tarjeta 3 ~316w]                 |
|                                                                                  |
|                                 [ OK 420x67 ]                                   |
+----------------------------------------------------------------------------------+
600
```

## 2. PromptScreen

### Estructura general
- Margen exterior: `12 px` izquierda y derecha, `12 px` arriba y `6 px` abajo
- Espaciado base del layout: `6 px`
- Logo flotante superior derecha: `252 x 189 px`
- Franja superior de titulo: `189 px` de alto, centrada con el logo

### Zonas
- Header de marca:
  - "Agua Purificada": `38 px`
  - "Lupita": `42 px`
- Separacion superior antes del titulo: `18 px`
- Titulo principal: `36 px`
- Imagen central:
  - Alto fijo del contenedor: `198 px`
  - Imagen estatica escalada hasta `330 x 255 px`
- Separacion entre imagen y subtitulo: `28 px`
- Subtitulo: `23 px`
- Boton OK:
  - `420 x 67 px`
  - Texto: `30 px`
  - Radio: `12 px`

### Wireframe
```text
+----------------------------------------------------------------------------------+
|                           Agua Purificada Lupita                 [Logo 252x189] |
|                                                                                  |
|                                  [Titulo]                                        |
|                                                                                  |
|                             [Imagen h=198 / 330x255]                             |
|                                                                                  |
|                                 [Subtitulo]                                      |
|                                                                                  |
|                                 [ OK 420x67 ]                                   |
+----------------------------------------------------------------------------------+
```

## 3. DispensingScreen

### Estructura general
- Margen exterior: `12 px` izquierda y derecha, `12 px` arriba y `6 px` abajo
- Espaciado base del layout: `0 px`
- Logo flotante superior derecha: `252 x 189 px`
- Franja superior de titulo: `189 px` de alto, centrada con el logo

### Zonas
- Header de marca:
  - "Agua Purificada": `38 px`
  - "Lupita": `42 px`
- Separacion superior antes del titulo: `20 px`
- Titulo de proceso: `40 px`
- Area de animacion:
  - Alto minimo: `220 px`
  - Alto maximo: `260 px`
  - Si se usa imagen fija, escala a `260 x 240 px`
- Barra de progreso:
  - `430 x 56 px`
  - Texto interno: `24 px`
  - Borde: `4 px`
  - Radio exterior: `16 px`
  - Radio chunk: `12 px`
- Boton detener:
  - Alto minimo: `53 px`
  - Ancho minimo: `227 px`
  - Ancho maximo: `340 px`
  - Texto: `24 px`
  - Radio: `12 px`

### Wireframe
```text
+----------------------------------------------------------------------------------+
|                           Agua Purificada Lupita                 [Logo 252x189] |
|                                                                                  |
|                                   [Proceso]                                      |
|                                                                                  |
|                            [Animacion h=220..260]                                |
|                                                                                  |
|                               [Progreso 430x56]                                  |
|                                                                                  |
|                           [Detener 227..340 x 53]                                |
+----------------------------------------------------------------------------------+
```

## 4. MessageScreen

### Estructura general
- Hereda `BrandedScreen`
- Margen exterior: `12 px` izquierda y derecha, `12 px` arriba y `6 px` abajo
- Espaciado base del layout: `6 px`
- Logo flotante superior derecha: `252 x 189 px`
- Franja superior de titulo: `189 px` de alto, centrada con el logo

### Zonas
- Header de marca:
  - "Agua Purificada": `38 px`
  - "Lupita": `42 px`
- Separacion superior antes del mensaje: `24 px`
- Mensaje principal: `40 px`
- Separacion hacia animacion: `18 px`
- Animacion:
  - Alto fijo: `180 px`

### Wireframe
```text
+----------------------------------------------------------------------------------+
|                           Agua Purificada Lupita                 [Logo 252x189] |
|                                                                                  |
|                              [Mensaje principal]                                 |
|                                                                                  |
|                                [GIF h=180 px]                                    |
|                                                                                  |
|                                                                                  |
+----------------------------------------------------------------------------------+
```

## Resumen rapido

| Interfaz | Base | Elementos fijos principales |
|---|---:|---|
| ProductScreen | `1024 x 600` | logo `252x189`, credito `368w`, OK `420x67`, 3 tarjetas |
| PromptScreen | `1024 x 600` | logo `252x189`, imagen `h=198`, OK `420x67` |
| DispensingScreen | `1024 x 600` | logo `252x189`, animacion `h=220..260`, progreso `430x56` |
| MessageScreen | `1024 x 600` | logo `252x189`, mensaje `40 px`, GIF `h=180` |
