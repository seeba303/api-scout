# API Scout

API Scout is a standalone data-source intelligence tool. It discovers GitHub
repositories that may lead to useful APIs, SDKs and public data sources, applies
a relevance gate, extracts local evidence, classifies the source, and ranks
candidates with deterministic, explainable scoring.

GitHub is discovery, not truth. API Scout does not claim a provider is free,
legal for your use case, available, or production-safe until official provider
documentation is verified.

## What changed in V0.2

- relevance-first GitHub search instead of star-first ranking
- hard relevance gate to suppress giant unrelated repositories
- context-aware README evidence windows
- API directory / provider / SDK / generic-resource classification
- intelligence capability taxonomy
- lower weighting for GitHub stars
- local risk/free-hint detection instead of whole-README keyword scanning
- Windows-friendly Markdown encoding
- graceful GitHub rate-limit errors
- built-in `cipher-intelligence` discovery profile

## C.I.P.H.E.R. intelligence profile

The profile searches for legitimate public data access around:

- X/Twitter public-post APIs and clients
- social-media/public-post data
- Bluesky / ATProto
- meme, GIF and reaction trends
- Reddit/community data
- news and RSS
- Solana and on-chain data
- crypto market / DEX data

Run:

```powershell
api-scout --profile cipher-intelligence
```

Add extra requirements when needed:

```powershell
api-scout --profile cipher-intelligence --need websocket --need "historical data"
```

General discovery still works:

```powershell
api-scout
api-scout --need weather --need travel
```

## Output

```text
api_scout_output/
    api_scout_results.json
    api_scout_report.md
```

The report includes:

- deterministic score
- confidence label
- source type
- matched needs
- intelligence capabilities
- local API evidence
- free/public hints
- risk hints
- ranking reasons
- relevant README evidence

## Install on Windows

```powershell
cd D:\API-Scout
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -e ".[dev]"
```

## Validate

```powershell
python -m ruff check .
python -m pytest
```

## Optional GitHub token

Small runs can use public GitHub access. For higher GitHub rate limits, create a
read-only token and expose it only in your shell or another secret store:

```powershell
$env:GITHUB_TOKEN="YOUR_TOKEN"
```

Never commit a token and never paste it into chat.

## Roadmap

V0.2: precision discovery + C.I.P.H.E.R. intelligence profile  
V1: official provider documentation verification  
V2: pricing, free-tier, authentication and rate-limit extraction  
V3: licensing/commercial-use checks + API health  
V4: recommendation/LLM layer over verified evidence  
V5: starter integration-code generation  
V6: web app / SaaS / team source catalog
