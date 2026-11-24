# CLAUDE.md

Notas para asistentes de IA trabajando en este repo. Mantener este archivo **breve**.

## Stack

- **Prácticas:** Jupyter notebooks (`.ipynb`) en `notebooks/`, pensados para ejecutarse en Google Colab o en local.
- **Gestión de dependencias:** `uv`. Ver `pyproject.toml`.
- **Idioma del material:** inglés.

## Convenciones

- Una carpeta por sesión en `notebooks/`.
- Datos en `data/raw/` (versionados). Se regeneran con los scripts de `scripts/`.
- El repo es un paquete instalable (`curso-agentes-ia`, módulo `cai` en `src/cai/`). La fontanería común (API keys, clientes de modelo, carga de datos) vive en `src/cai/utils.py`; lo que se enseña (herramientas, bucle, middleware, grafos) se queda en los notebooks.
- Primera celda de cada notebook: `%pip install -q git+https://github.com/albertotb/curso-agentes-ia` (Colab instala lo que haya en `main`: no cambiar `src/cai/` durante una clase). Después, `PROVIDER` y `MODEL` visibles en la celda de setup.
- Dependencias en `pyproject.toml` con rangos, no versiones exactas, para no romper los paquetes preinstalados de Colab.
- Notebooks sin salidas en git (`nbstripout`, ver `.gitattributes`).

## Comandos

```bash
uv sync                    # instalar/actualizar entorno
uv run jupyter lab         # arrancar notebooks
uv run nbstripout --install  # una vez por clon, activa el filtro de git
```

## Flujo de trabajo con notebooks

- Tras editar cualquier `.ipynb`, ejecutar `uv run ruff format notebooks/` y `uv run ruff check notebooks/`.
