# Space Mission Agent Team — CLAUDE.md

This is a multi-agent AI system for space mission engineering. It runs a full team of
specialised agents (21+) that collaborate, challenge each other, and produce domain deliverables
across the full mission lifecycle: business objectives → commissioning.

---

## Architecture

```
core/
  message_bus.py        pub/sub inter-agent communication log
  agent_network.py      registry — any agent can query any other by name
  change_request.py     typed change (CR) with severity and source type
  impact_map.py         dependency graph — who is downstream of who
  change_propagator.py  adversarial review → Mission Director adjudication → QA gate
  deliverable.py        typed artifact (TABLE / CALCULATION / CODE / REGISTER)
  milestone_review.py   parallel domain deliverables at SRR / PDR / CDR
  session_state.py      JSON persistence of mission baseline across runs
  universal_start.py    routes any agent start to the right pipeline

agents/                 one file per agent, all inherit BaseAgent + CriticalReviewMixin
orchestrator/           mission / R&D / proposal pipelines
tools/                  Notion, Confluence, CSV/JSON exporters
web/                    Flask dashboard (python web/server.py → localhost:5000)

start.py                universal CLI entry point
trigger.py              change propagation CLI
main.py                 legacy pipeline runner (--pipeline mission/rnd/proposal/all)
```

---

## Entry Points

```bash
# Universal start — use this for everything
python start.py --from "User" --mission "SAT-1" --description "..."
python start.py --from "Propulsion Engineer" --description "..."
python start.py --milestone PDR --mission "SAT-1"
python start.py --resume
python start.py --status
python start.py --list-agents

# Change propagation (also accessible via start.py)
python trigger.py --source "Payload Engineer" --severity MAJOR --title "..." --description "..."
python trigger.py --list-impacts "Propulsion Engineer"

# Web dashboard
python web/server.py    # → http://localhost:5000

# Full pipelines
python main.py --pipeline mission
python main.py --pipeline rnd
python main.py --pipeline proposal

# Example change scenarios
python examples/change_scenarios.py --scenario propulsion
python examples/change_scenarios.py --list
```

---

## Adding a New Agent

1. Create `agents/my_agent.py`:
```python
from agents.base_agent import BaseAgent

class MyAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="My Agent",
            role="My Role",
            expertise="...",
        )

    def my_main_method(self, context: str) -> str:
        task = "Produce X covering: 1. ... 2. ... 3. ..."
        return self.run(task, context=context)
```

2. Add to `agents/__init__.py`
3. Register in pipelines and `start.py` `build_network()`
4. Add to `core/impact_map.py` DEPENDENCY_GRAPH
5. Add to `core/milestone_review.py` MILESTONE_DELIVERABLES
6. Add to `core/universal_start.py` AGENT_ACTION_MAP

---

## Change Propagation Rules

- Every agent has `critical_review()` — they DO NOT agree by default
- `ImpactMap` defines who is downstream (edit `core/impact_map.py`)
- `ChangePropagator` runs: impact map → parallel reviews → Mission Director adjudicates → QA validates
- Verdict options: ACCEPT / ACCEPT WITH CONDITIONS / REJECT (must include alternative)
- All exchanges logged to MessageBus, appended to master document

---

## Key Design Rules

- **Never rubber-stamp**: agent system prompts explicitly say "do not agree without evidence"
- **Specific objections**: every concern must name a parameter, budget, or interface — not generic risk
- **REJECT needs an alternative**: a rejection without a concrete proposal is not accepted
- **Parallel where possible**: Phase B subsystems run with ThreadPoolExecutor(max_workers=4)
- **Session state persists**: `outputs/session_state.json` carries baseline across runs
- **Domain deliverables**: at milestones, agents produce their actual artifact (tables, calculations, code), not summaries

---

## Environment Variables

```
ANTHROPIC_API_KEY=sk-ant-...     # required for all agent runs
MISSION_NAME=MY-SAT-1            # optional override
BUSINESS_OBJECTIVE=...           # optional override
RND_PROJECT_NAME=...             # R&D pipeline
RND_IDEA=...                     # R&D pipeline
PROPOSAL_NAME=...                # proposal pipeline
OPPORTUNITY=...                  # proposal pipeline
OUTPUT_DIR=outputs               # where files are saved
```

---

## Tool Integrations

```python
from tools.connectors import NotionConnector, ConfluenceConnector, LocalExporter

# Export to Notion
notion = NotionConnector(api_key="secret_...", database_id="...")
notion.export_all(package.deliverables)

# Export to Confluence
conf = ConfluenceConnector("https://company.atlassian.net", "user@co.com", "token")
conf.export_all(package.deliverables, space_key="SPACE")

# Local CSV/JSON (no API key)
LocalExporter.to_json(session.results, "outputs/mission.json")
LocalExporter.to_csv(session.results, "outputs/mission.csv")
```

---

## Standards the Agents Know

ECSS-E-ST-10 · ECSS-M-ST-10 · ECSS-M-ST-40 · ECSS-Q-ST-10/20/80 ·
ECSS-E-ST-20-07 · ECSS-E-ST-40 · MIL-STD-882 · CCSDS 131/132/133 ·
IEC 61508 · IADC debris mitigation guidelines
