# AG2 Network — Examples & Tutorial

A hands-on companion to the [AG2 Network](https://docs.ag2.ai/docs/user-guide/network/overview)
documentation. This repository contains runnable Python examples and a small static
site (served via GitHub Pages) that walks you through building multi-agent
networks with AG2.

## What is AG2 Network?

`ag2.network` turns one or more `Agent` instances into a **multi-agent network**:
a hub-and-spoke topology where a central `Hub` coordinates channel-based,
protocol-driven exchanges between named agents. It is fully opt-in — bare
`Agent` keeps working standalone.

Adopt it when you need enforceable turn order, a registry of named agents,
durable/replayable transcripts, governance, sub-task observability, or
distributed deployment.

## Quick start

```bash
pip install -r requirements.txt
# needs a running Ollama (default) OR set OPENAI_API_KEY / ANTHROPIC_API_KEY
python examples/01_quickstart_consulting.py
```

## Examples

| File | Demonstrates |
|---|---|
| `01_quickstart_consulting.py` | Smallest end-to-end network: hub + 2 agents + consulting channel |
| `02_conversation.py` | Free-form two-party conversation |
| `03_discussion.py` | Round-robin multi-party discussion |
| `04_workflow.py` | Declarative `TransitionGraph` orchestration |
| `05_hitl_human.py` | Human-in-the-loop via `HumanClient` |
| `06_governance.py` | `Rule`s, access lists, rate limits, audit log |
| `07_distributed.py` | `WsLink` + `serve_ws` across processes |

## GitHub Pages site

The `docs/` folder is a static site. Enable GitHub Pages (source: `docs/`
folder on `main`) and visit the published URL. Locally, open `docs/index.html`.

## License

Apache-2.0 (matching AG2).