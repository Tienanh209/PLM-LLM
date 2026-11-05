# PLM-LLM

Connect a protein language model (e.g. ESM-2) to an LLM so it answers protein questions grounded in the sequence.

## Layout
```
config.yaml        hyperparameters
data/              local data (git-ignored); on Colab use Drive
src/               dataset.py, model.py, train.py, utils.py
notebooks/         colab_train.ipynb
results/           figures, tables, logs
```

## Setup
```bash
pip install -r requirements.txt
```

## Colab
VS Code → `git push` → open `notebooks/colab_train.ipynb` on Colab → run Sync → run train.
Data: `MyDrive/PLM-LLM/data`, outputs: `MyDrive/PLM-LLM/results`.
