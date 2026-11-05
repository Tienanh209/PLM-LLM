# PLM-LLM

Connect a protein language model (e.g. ESM-2) to an LLM so it answers protein questions grounded in the sequence.

## Layout
```
config.yaml        hyperparameters
data/              local data (git-ignored); on Colab use Drive
src/               dataset.py, model.py, train.py, utils.py
notebooks/         01_data.ipynb (CPU: collect/process data), 02_train.ipynb (GPU: train)
results/           figures, tables, logs
```

## Setup
```bash
pip install -r requirements.txt
```

## Colab
VS Code → `git push` → open `notebooks/02_train.ipynb` on Colab → run Sync → run train.
Data: `MyDrive/PLM-LLM/data`, outputs: `MyDrive/PLM-LLM/results`.

## Data: Swiss-Prot
`src/prepare_data.py` (stdlib only):
```bash
python src/prepare_data.py download --out data/raw/swissprot.tsv.gz   # --limit 500 for a quick test
python src/prepare_data.py cluster  --tsv data/raw/swissprot.tsv.gz   # optional; needs mmseqs2, 30% identity
```
TODO: build step (annotations -> QA jsonl + split) to be defined.
