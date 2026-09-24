# pipeline

Planet imagery -> processing COG -> static tile pyramid -> upload.

## Setup

```bash
cd pipeline
python -m venv .venv
source .venv/bin/activate           # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env                # fill in PL_API_KEY and storage creds
```

## Manifest shape

`web/` reads this file - treat it as the contract between the two halves of the repo. See `layers/manifest_schema.py` for the authoritative shape.
