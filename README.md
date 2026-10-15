# API Scout

API Scout is a standalone discovery tool that searches GitHub for repositories
that may point to useful public/free APIs, inspects a small number of README
files, and ranks the results for a software project's needs.

## V0 goal

Given needs such as:

- Solana
- on-chain data
- news
- social media
- market data
- weather
- travel

API Scout produces a shortlist with:

- repository name
- GitHub URL
- stars
- last update time
- license metadata
- matched project needs
- free/public hints
- obvious risk/deprecation hints
- README evidence
- a transparent heuristic score

V0 is intentionally deterministic. It does **not** use an LLM yet.

## Important limitation

A GitHub repository mentioning a "free API" is only a lead.

Before integrating any API, verify against the provider's official
documentation:

- current pricing
- free-tier quota
- authentication method
- rate limits
- commercial-use terms
- data licensing
- redistribution restrictions
- maintenance status

## Install on Windows

```powershell
cd D:\
mkdir API-Scout
cd API-Scout
```

Extract this project here, then:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -e ".[dev]"
```

## Run tests

```powershell
ruff check .
pytest
```

## Use it

Basic run:

```powershell
api-scout
```

Target specific needs:

```powershell
api-scout --need solana --need "on-chain" --need "social media"
```

Or without installing the command:

```powershell
python -m api_scout.cli --need news --need crypto
```

Outputs are written to:

```text
api_scout_output/
    api_scout_results.json
    api_scout_report.md
```

## Optional GitHub token

For small V0 searches, API Scout can use public GitHub access without a token.

If you later create a read-only GitHub token, put it in your environment:

```powershell
$env:GITHUB_TOKEN="YOUR_TOKEN"
```

Never commit a token to Git and never paste it into chat.

## Planned roadmap

V0: GitHub discovery + deterministic ranking  
V1: official provider documentation verification  
V2: pricing/free-tier/rate-limit extraction  
V3: API health and maintenance checks  
V4: LLM recommendation layer  
V5: starter integration-code generation  
V6: web app / SaaS / team API catalog
