# ShiftReport Generator

Convierte un **CSV o Excel** de turno en un **reporte formateado** (Excel + HTML)
y lo **envía solo** a la hora que tú decidas. Pensado para equipos pequeños que hoy
montan ese reporte a mano cada turno.

> El reporte de turno te come ~2 horas. Esto lo convierte en un clic.

Hecho por **César Romero del Palacio** · Licencia MIT · 100% datos sintéticos en los ejemplos.

---

## Qué hace

1. Lee tu archivo (`.csv` / `.xlsx`).
2. Agrupa por la columna que elijas (área, línea, operario…) y suma las métricas numéricas.
3. Genera:
   - un **Excel** con hoja de *Resumen* + hoja de *Detalle*,
   - un **HTML** limpio listo para enviar o publicar.
4. Opcional: lo **envía por correo** (SMTP) a una **hora programada**.

## Instalación

```bash
git clone https://github.com/cesarromerodelpalacio/shiftreport-generator.git
cd shiftreport-generator
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -e .
```

## Uso rápido

```bash
# Reporte agrupando por area, autodetectando metricas numericas
shiftreport examples/sample_shift_data.csv --group-by area --title "Reporte de turno"

# Eligiendo metricas concretas
shiftreport datos.xlsx -g linea -m units_processed -m errors -o outputs

# Programar el envio por correo a las 14:30
shiftreport datos.csv -g area --email-to jefe@empresa.com --at 14:30
```

Los archivos se generan en `outputs/` con marca de tiempo.

## Envío de correo (opcional)

Las credenciales se leen **solo de variables de entorno**, nunca del código:

```bash
set SMTP_HOST=smtp.tu-proveedor.com
set SMTP_PORT=587
set SMTP_USER=tu_usuario
set SMTP_PASS=tu_password
set SMTP_FROM=reportes@empresa.com
```

Para envío recurrente en producción usa el **Programador de tareas de Windows**
(o `cron` en Linux) apuntando al comando `shiftreport`. El flag `--at` sirve para
una sola ejecución diferida.

## Empaquetar como `.exe` (para usuarios sin Python)

```bash
pip install -e ".[dev]"
pyinstaller --onefile --name shiftreport src/shiftreport/__main__.py
# resultado en dist/shiftreport.exe
```

## Desarrollo

```bash
pip install -e ".[dev]"
pytest -v
```

## Estructura

```
shiftreport-generator/
├── src/shiftreport/      # codigo del producto
│   ├── reader.py         # lee CSV/Excel
│   ├── report.py         # agrega + genera Excel/HTML
│   ├── emailer.py        # envio SMTP (env vars)
│   └── cli.py            # interfaz de comandos
├── examples/             # datos sinteticos de ejemplo
├── tests/                # pytest
└── .github/workflows/    # CI
```

## Privacidad

Reimplementación genérica. No incluye datos reales, esquemas internos ni
credenciales. Los ejemplos son sintéticos.
