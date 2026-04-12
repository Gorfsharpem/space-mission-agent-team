# 🛰️ Space Mission Agent Team

A full-organisation, multi-agent AI system that drives space missions **and** innovation projects from business objectives through to commissioning — using a team of specialised engineering and management agents powered by Claude (Anthropic).

All agents **talk to each other** during execution via a built-in inter-agent message bus, and **challenge every change** through an adversarial critical review system before accepting it.

---

## 🏢 The Full Team (24 Agents)

### Management & Control
| Agent | Role | Key Outputs |
|---|---|---|
| **Project Manager** | Mission lifecycle governance | Mission Initiation Document, WBS, schedule |
| **Mission Director** | Chief Systems Engineer | System requirements, integration review, commissioning plan |
| **Project Controller** | Schedule, cost & payment tracking | Milestone reviews, EVM dashboards, payment schedules |
| **Document Manager** | Mission document tree & CM | DRL, document tree, version baseline |

### Business Development
| Agent | Role | Key Outputs |
|---|---|---|
| **Bid Manager** | Commercial strategy, pricing, contracts | Bid/No-Bid decision, pricing strategy, contract review |
| **Proposal Manager** | Proposal writing & win strategy | RFP analysis, technical volume, red team review |
| **R&D Manager** | Innovation portfolio & TRL maturation | R&D PID, technology roadmap, exploitation plan |

### Quality, Safety & Assurance
| Agent | Role | Key Outputs |
|---|---|---|
| **QA/PA Engineer** | Gates every phase, FMEA, acceptance testing | Gate review reports, NCR log, ATP |
| **Safety Engineer** | System safety analysis & safety case | Hazard register, FTA, orbital debris plan, range safety |

### Systems Engineering
| Agent | Role | Key Outputs |
|---|---|---|
| **Mission Analyst** | Orbit, launch, coverage, lifetime | MAR: orbit, delta-V, eclipse fractions |
| **Ground Segment Engineer** | Ground stations, MCS, CONOPS | Station network, ops concept, simulator requirements |
| **Launch Campaign Manager** | Launch campaign, countdown, LEOP | Campaign schedule, LRR checklist, LEOP timeline |

### Subsystem Engineering
| Agent | Role | Key Outputs |
|---|---|---|
| **Payload Engineer** | Payload concept & performance | Payload design, data volume, interface requirements |
| **EPS Engineer** | Power generation & storage | Power budget, solar array & battery sizing |
| **ADCS Engineer** | Attitude control & pointing | Pointing budget, actuator/sensor selection |
| **Thermal Engineer** | Thermal control | MLI, radiators, heater budget, hot/cold cases |
| **Structures Engineer** | Primary structure & configuration | Mass budget, launch loads, configuration layout |
| **Propulsion Engineer** | Delta-V, thrusters, propellant | Propulsion trade, Tsiolkovsky sizing, plume analysis |
| **Mechanical Engineer** | Detailed mechanical design | Harness routing, mechanisms, tolerance stack-up |
| **Electrical Engineer** | Electrical architecture & EMC | Grounding, harness sizing, EIT plan |
| **Antenna Engineer** | RF antennas for TT&C and payload | Antenna inventory, link gain, pattern analysis |
| **TT&C Engineer** | Communications & ground stations | Link budgets, transponder, ground contact strategy |
| **OBSW Engineer** | Flight software & data handling | OBC selection, FDIR, data management |

---

## 🏗️ Architecture

```
Business Objective / RFP / R&D Idea
           │
    ┌──────┴──────────────────────────┐
    │     Message Bus (pub/sub)        │  ← all inter-agent comms logged here
    └──────┬──────────────────────────┘
           │
    ┌──────▼──────────────────────────────────────────────────┐
    │  Agent Network  (registry + routing)                     │
    │  Any agent can query any other agent by name             │
    └──────┬──────────────────────────────────────────────────┘
           │
   ┌───────┴────────────────────────────────────────────────┐
   │                                                        │
   ▼                                                        ▼
MISSION PIPELINE                        R&D / PROPOSAL PIPELINE
Phase 0  Business Analysis              Stage 1  Idea / RFP
Phase A  Mission Analysis               Stage 2  Bid Decision
Phase B  Subsystem Design (parallel)    Stage 3  Technical / Pricing
   QA Gate + Safety Review              Stage 4  Internal Review
Phase C  System Integration             Stage 5  QA Gate
Phase D  Commissioning Plan             Stage 6  Exploitation / Contract
   QA Gate + Launch Campaign Plan       Stage 7  Document Management
Ground Segment Design                   Master Report
Master Mission Design Document

CHANGE PROPAGATION (any time)
Change raised → ImpactMap resolves affected agents →
Parallel adversarial critical reviews →
Mission Director adjudicates →
QA/PA validates → Baseline updated
```

---

## 🔄 Change Propagation

Any agent — or the user — can raise a change at any time. The system:

1. Resolves all affected agents via the dependency graph
2. Each affected agent does a **critical review** — they do NOT agree by default
3. Every review must cover: Impact · Objections · Interface impacts · Alternatives · Verdict
4. Verdict: `ACCEPT` / `ACCEPT WITH CONDITIONS` / `REJECT` (reject requires an alternative)
5. Mission Director adjudicates conflicts
6. QA/PA validates traceability
7. Baseline updated with list of agents needing redesign

---

## 🚀 Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/gorfsharpem/space-mission-agent-team.git
cd space-mission-agent-team
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Add your API key

```bash
cp .env.example .env
# Edit .env — add your ANTHROPIC_API_KEY
```

### 4. Run

```bash
# Web dashboard (recommended)
python web/server.py
# → open http://localhost:5000

# CLI — full mission from business objective
python start.py --from User --mission "MY-SAT-1" --description "..."

# CLI — start from any subsystem
python start.py --from "Propulsion Engineer" --description "Switching to cold gas..."

# CLI — run a milestone review (all 20 agents produce deliverables in parallel)
python start.py --milestone PDR --mission "MY-SAT-1"

# CLI — propagate a change
python start.py --from "Payload Engineer" --severity MAJOR --description "Mass increased to 18kg"

# See all agents and their start behaviour
python start.py --list-agents

# Check session state
python start.py --status
```

---

## 📁 Project Structure

```
space-mission-agent-team/
├── agents/                  24 agent files — one per team member
│   ├── base_agent.py        Base class with inter-agent query + critical review
│   ├── safety_engineer.py   Safety Engineer (NEW)
│   ├── ground_segment.py    Ground Segment Engineer (NEW)
│   ├── launch_campaign.py   Launch Campaign Manager (NEW)
│   └── ...                  21 other agents
├── core/
│   ├── message_bus.py       Pub/sub inter-agent communication log
│   ├── agent_network.py     Registry — any agent queries any other by name
│   ├── change_request.py    Typed change request (CR)
│   ├── impact_map.py        Dependency graph — who is downstream of who
│   ├── change_propagator.py Adversarial review → adjudication → QA gate
│   ├── critical_review.py   The "never rubber-stamp" review protocol
│   ├── deliverable.py       Typed artifact (TABLE/CALCULATION/CODE/REGISTER)
│   ├── milestone_review.py  Parallel domain deliverables at SRR/PDR/CDR
│   ├── session_state.py     JSON persistence of mission baseline
│   └── universal_start.py   Routes any agent start to the right pipeline
├── orchestrator/
│   ├── pipeline.py          Mission pipeline (Phase 0 → D + QA gates)
│   ├── rnd_pipeline.py      R&D pipeline (idea → exploitation)
│   └── proposal_pipeline.py Proposal pipeline (opportunity → contract)
├── tools/
│   └── connectors.py        Notion, Confluence, CSV/JSON exporters
├── web/
│   ├── server.py            Flask dashboard server
│   └── templates/index.html Dark industrial UI
├── examples/
│   └── change_scenarios.py  5 ready-to-run change scenarios
├── CLAUDE.md                Self-documents repo for Claude Code
├── start.py                 Universal CLI entry point
├── trigger.py               Change propagation CLI
└── main.py                  Legacy pipeline runner
```

---

## 📄 Milestone Deliverables

At every milestone (SRR / PDR / CDR), all 20 agents produce domain-specific artifacts in parallel — not generic summaries:

| Agent | What they produce |
|---|---|
| Mission Analyst | Orbital parameters table, delta-V budget, coverage analysis |
| EPS Engineer | Power budget table, eclipse energy balance, solar array sizing calculation |
| Structures Engineer | Mass budget table (component level), launch load analysis, CoM estimate |
| Propulsion Engineer | Tsiolkovsky calculation, propellant budget, tank sizing |
| TT&C Engineer | Link budget tables (all links × geometries), ground contact schedule |
| OBSW Engineer | FDIR state machine, memory map, task list, code metrics |
| Safety Engineer | Hazard register, FTA description, safety-critical functions list |
| Ground Segment Engineer | Station network table, CONOPS phases, ops cost estimate |
| Launch Campaign Manager | Campaign schedule table, LRR checklist, countdown sequence |
| QA/PA Engineer | NCR register, gate checklist, FMEA extract |
| Project Controller | EVM dashboard (SPI/CPI), milestone RAG table, invoice log |

---

## 🔧 Tool Integrations

```python
from tools.connectors import NotionConnector, ConfluenceConnector, LocalExporter

# Export to Notion
notion = NotionConnector(api_key="secret_...", database_id="...")
notion.export_all(package.deliverables)

# Export to Confluence
conf = ConfluenceConnector("https://company.atlassian.net", "user@co.com", "token")
conf.export_all(package.deliverables, space_key="SPACE")

# Local CSV/JSON (no API key needed)
LocalExporter.to_json(session.results, "outputs/mission.json")
LocalExporter.to_csv(session.results, "outputs/mission.csv")
```

---

## 📐 Standards Reference

| Standard | Coverage |
|---|---|
| ECSS-E-ST-10 | Systems engineering |
| ECSS-M-ST-10 | Project planning and control |
| ECSS-M-ST-40 | Configuration and document management |
| ECSS-Q-ST-10/20/80 | Quality assurance, PA, FMEA |
| ECSS-E-ST-20-07 | EMC |
| ECSS-E-ST-40 | Software engineering |
| MIL-STD-882 | System safety |
| IADC | Orbital debris mitigation guidelines |
| CCSDS 131/132/133 | TM/TC packet standards |

---

## 🤝 Contributing

Pull requests are welcome. See `CLAUDE.md` for architecture details and how to add new agents.

---

## 📜 License

MIT License — see [LICENSE](LICENSE) for details.

---

## 👤 Author

**gorfsharpem** — [github.com/gorfsharpem](https://github.com/gorfsharpem)
