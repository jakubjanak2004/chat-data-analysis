# Bachelor thesis — data analysis

Download metrics from **Prometheus**, analyze in **Jupyter**, export figures/CSVs for the thesis.

## Setup

```bash
cd data-analysis
python3 -m venv .venv && source .venv/bin/activate   # optional
pip install -r requirements.txt
```

## Prometheus URL

Default in code: **`http://178.104.69.73:9090`**.

Override if needed:

```bash
export PROMETHEUS_URL="http://OTHER_HOST:9090"
```

Or set `os.environ["PROMETHEUS_URL"]` in the first notebook cell.

## Run the notebook

**Important:** start Jupyter so the working directory is **`data-analysis`** (the folder that contains `src/`):

```bash
cd /Users/jakubjanak/Desktop/SIT/Bakalarka/data-analysis
jupyter notebook notebooks/01_prometheus_load_data.ipynb
```

Then open `notebooks/01_prometheus_load_data.ipynb` and run all cells.

## Layout

| Path | Purpose |
|------|--------|
| `src/prometheus_io.py` | `prom_query_range` / `prom_query_instant` → pandas |
| `notebooks/` | Analysis notebooks |
| `data/raw/` | Exported CSV snapshots |
