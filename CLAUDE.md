# CLAUDE.md

Notas para asistentes de IA trabajando en este repo. Mantener este archivo **breve**.

## Stack

- **Prácticas:** Jupyter notebooks (`.ipynb`) en `notebooks/`, pensados para ejecutarse en Google Colab o en local.
- **Gestión de dependencias:** `uv`. Ver `pyproject.toml`.
- **Idioma del material:** inglés.

## Convenciones

- Una carpeta por sesión en `notebooks/`.
- Datos en `data/raw/` (versionados). Se regeneran con los scripts de `scripts/`.
- Cada notebook es autocontenido: configuración de proveedor (`PROVIDER`, OpenAI o Gemini) en la primera celda, y busca los datos en `../../data/raw/` o los descarga de GitHub si no están (Colab).
- Notebooks sin salidas en git (`nbstripout`, ver `.gitattributes`).

## Comandos

```bash
uv sync                    # instalar/actualizar entorno
uv run jupyter lab         # arrancar notebooks
uv run nbstripout --install  # una vez por clon, activa el filtro de git
```

## Flujo de trabajo con notebooks

- Tras editar cualquier `.ipynb`, ejecutar `uv run ruff format notebooks/` y `uv run ruff check notebooks/`.
- Para Gemini en LangChain usar la integración nativa (`google_genai:`), no el endpoint compatible con OpenAI: Gemini 3 exige devolver la *thought signature* de cada tool call y `ChatOpenAI` la descarta (error 400).
