# Patent Search Project Context

## What this project does
- Command-line patent semantic search tool targeting vehicle patent applications.
- Loads JSON patent batches, builds SentenceTransformer embeddings, and runs cosine-similarity search with optional filters and patent-to-patent similarity.
- Reuses cached embeddings at `embeddings/patent_embeddings.pkl` when present; otherwise creates them.

## Key entry points
- `main.py` – prints banner, creates `PatentSearchInterface`, calls `setup(data_folder='data/patent_data_small')`, then runs the interactive menu.
- `src/interface.py` – user flow (basic search, advanced search with filters, similar-patent search, stats). Handles console prompts and delegates to loader/engine.
- `src/data_loader.py` – loads `patents_ipa*.json` from the data folder. Normalizes fields (document number, title, abstract, claims, description, classification, bibtex) and builds `searchable_text` by concatenating title, abstract, claims, and truncated description. Provides simple stats.
- `src/search_engine.py` – loads SentenceTransformer model (default `all-MiniLM-L6-v2`), builds/loads embeddings, and performs cosine-similarity search with optional classification prefix and title keyword filters. Also supports similarity-by-patent-id and computes result stats.

## Data expectations
- Data folder: `data/patent_data_small/` (default). Files named `patents_ipa*.json`, each a list of patent dicts.
- Expected fields (flexible): document number (`Document Number`, `id`, etc.), `Title`, `Abstract`, `Claims`, `Detailed Description`/`description`, `Classification Code`, `Bibtext Citation`. Missing fields get defaults; any patent is accepted.

## How to run
1. Install deps: `pip install -r requirements.txt` (uses `sentence-transformers`, `torch`, `numpy`, `pandas`, `scikit-learn`).
2. Run CLI: `python main.py` (from repo root). First run may take minutes to build embeddings; subsequent runs load the cached pickle.
3. Use menu options: basic search, advanced search (filters), similar-patent search, or statistics.

## Notable behaviors / caveats
- Embedding file is stored under `embeddings/`; ensure the directory is writable. Remove it to force a rebuild.
- Filtering is simple: classification code prefix match and case-insensitive title keyword containment.
- `searchable_text` truncates description to 1000 chars and only uses first three description list entries when present.
- Model downloads (`all-MiniLM-L6-v2`) require network on first run.
- Interface is blocking/interactive; no API/server layer included.

## Quick map of important files
- `main.py` – entrypoint banner + interface bootstrap.
- `src/interface.py` – console UX and menu loop.
- `src/data_loader.py` – JSON ingestion and patent normalization.
- `src/search_engine.py` – embedding model, search, filters, similarity, stats.
- `requirements.txt` – dependency pins (minimal versions).

## Possible next questions to ask
- Do you need batch/non-interactive search or an API wrapper?
- Should we add persistence/versioning for embeddings keyed by model + data hash?
- Any need for eval scripts or unit tests against known queries?
- Should we log results or export to CSV/JSON for downstream analysis?
