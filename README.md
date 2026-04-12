# 🛰️ Space Mission Agent Team

A full-organisation, multi-agent AI system that drives space missions **and** innovation projects from business objectives through to commissioning — using a team of specialised engineering and management agents powered by Claude (Anthropic).

All agents can **talk to each other** during execution via a built-in inter-agent message bus, producing richer, cross-referenced outputs.

---

## 🏢 The Full Team

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

### Quality & Assurance
| Agent | Role | Key Outputs |
|---|---|---|
| **QA/PA Engineer** | Gates every phase, FMEA, acceptance testing | Gate review reports, NCR log, ATP |

### Systems Engineering
| Agent | Role | Key Outputs |
|---|---|---|
| **Mission Analyst** | Orbit, launch, coverage, lifetime | MAR: orbit, delta-V, eclipse fractions |

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
   ┌───────┴────────────────────────────────────┐
   │                                            │
   ▼                                            ▼
MISSION PIPELINE                        R&D / PROPOSAL PIPELINE
Phase 0  Business Analysis              Stage 1  Idea / RFP
Phase A  Mission Analysis               Stage 2  Bid Decision
Phase B  Subsystem Design (parallel)    Stage 3  Technical / Pricing
   QA Gate ← non-conformance check      Stage 4  Internal Review
Phase C  System Integration             Stage 5  QA Gate
Phase D  Commissioning Plan             Stage 6  Exploitation / Contract
   QA Gate ← mission readiness          Stage 7  Document Management
Document Tree                           Master Report
Master Mission Design Document
```

---

## 🔗 Inter-Agent Communication

Subsystem agents query each other during Phase B to resolve interface dependencies:

| Querying Agent | Asks | Target Agent |
|---|---|---|
| Propulsion | Delta-V budget per phase | Mission Analyst |
| Mechanical | Structural envelope & keep-out zones | Structures |
| Electrical | Power bus voltage & connector interfaces | EPS |
| Electrical | Data bus topology & signal levels | OBSW |
| Antenna | Gain / frequency / coverage requirements | TT&C |
| Antenna | High-gain downlink requirements | Payload |
| Proposal | Technology heritage & TRL evidence | R&D Manager |
| Bid | Cost baseline & resource rates | Project Controller |

All exchanges are logged on the **Message Bus** and appended to the master document.

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

### 3. Configure your API key

```bash
cp .env.example .env
# Edit .env — add your ANTHROPIC_API_KEY
```

### 4. Run a pipeline

```bash
# Full mission lifecycle
python main.py --pipeline mission

# R&D / innovation project
python main.py --pipeline rnd

# Proposal / bid lifecycle
python main.py --pipeline proposal

# All three
python main.py --pipeline all
```

All outputs are saved as markdown files in `outputs/`, plus a consolidated master document per pipeline.

---

## ⚙️ Configuration

Set via environment variables or edit `main.py`:

| Variable | Pipeline | Description |
|---|---|---|
| `ANTHROPIC_API_KEY` | All | Your Anthropic API key *(required)* |
| `MISSION_NAME` | Mission | Name of the mission |
| `BUSINESS_OBJECTIVE` | Mission | One-paragraph mission business case |
| `RND_PROJECT_NAME` | R&D | Name of the R&D project |
| `RND_IDEA` | R&D | Technology idea to develop |
| `PROPOSAL_NAME` | Proposal | Name of the bid |
| `OPPORTUNITY` | Proposal | RFP/ITT description |

### Programmatic usage

```python
from orchestrator import MissionPipeline, RnDPipeline, ProposalPipeline

# Mission
MissionPipeline("MY-SAT-1", "Provide global AIS tracking...").run()

# R&D
RnDPipeline("MICRO-THRUSTER-001", "Develop a 0.5 kg Hall thruster for 6U CubeSats...").run()

# Proposal
ProposalPipeline("ESA-EO-2025", "ESA Fast Track EO opportunity...").run()
```

---

## 📁 Project Structure

```
space-mission-agent-team/
├── agents/
│   ├── base_agent.py            # Base class — inter-agent query support
│   ├── mission_director.py      # Chief Systems Engineer
│   ├── project_manager.py       # Project Manager
│   ├── project_controller.py    # Project Controller (EVM, milestones, payments)
│   ├── document_manager.py      # Document Manager (DRL, CM, baselines)
│   ├── qa_pa.py                 # QA/PA Engineer (gate reviews, FMEA, ATP)
│   ├── bid_manager.py           # Bid Manager (pricing, contracts)
│   ├── proposal_manager.py      # Proposal Manager (RFP analysis, tech volume)
│   ├── rnd_manager.py           # R&D Manager (TRL, roadmap, portfolio)
│   ├── mission_analysis.py      # Mission Analysis & Astrodynamics
│   ├── payload.py               # Payload Engineering
│   ├── eps.py                   # Electrical Power System
│   ├── adcs.py                  # ADCS
│   ├── thermal.py               # Thermal Control
│   ├── structures.py            # Structures & Mechanisms
│   ├── propulsion.py            # Propulsion
│   ├── mechanical.py            # Mechanical Engineering
│   ├── electrical.py            # Electrical Engineering
│   ├── antenna.py               # Antenna Engineering
│   ├── ttc.py                   # TT&C
│   └── obsw.py                  # On-Board Software
├── core/
│   ├── message_bus.py           # Pub/sub inter-agent message log
│   └── agent_network.py         # Agent registry and query routing
├── orchestrator/
│   ├── pipeline.py              # Mission pipeline (Phase 0 → D + QA gates)
│   ├── rnd_pipeline.py          # R&D pipeline (idea → exploitation)
│   └── proposal_pipeline.py     # Proposal pipeline (opportunity → contract)
├── outputs/                     # Generated documents (git-ignored)
├── docs/                        # Additional documentation
├── main.py                      # Entry point — CLI with --pipeline flag
├── requirements.txt
├── .env.example
└── README.md
```

---

## 📄 Outputs Per Pipeline

### Mission Pipeline
Business Analysis · Payment Schedule · Mission Analysis · System Requirements ·
Payload / EPS / ADCS / Thermal / Structures / Propulsion / Mechanical / Electrical / Antenna / TT&C / OBSW Design ·
QA Gate B Review · FMEA Review · System Integration Review · Phase C Milestone Review ·
Commissioning Plan · Acceptance Test Plan · QA Final Gate Review · Document Tree ·
**Master Mission Design Document**

### R&D Pipeline
R&D Project Initiation Document · Technology Roadmap · Bid Decision · R&D Pricing Strategy ·
Proposal Technical Volume · R&D Project Plan · R&D Payment Schedule ·
R&D Portfolio Review · R&D Milestone Review · R&D QA Gate Review ·
R&D Exploitation Plan · R&D Document Tree · **R&D Master Report**

### Proposal Pipeline
Bid Decision · RFP Analysis · Technical Volume · Commercial Volume ·
Proposed Payment Schedule · Red Team Review · Proposal QA Gate ·
Submission Document List · Contract Review · **Proposal Master Package**

---

## 🔧 Extending the Team

To add a new agent:

1. Create `agents/my_agent.py` inheriting from `BaseAgent`
2. Add it to `agents/__init__.py`
3. Register it in the relevant pipeline's `__init__`
4. Use `self.ask_agent("Target Name", "question", context)` for inter-agent queries

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
| CCSDS 131/132/133 | TM/TC packet standards |

---

## 🤝 Contributing

Pull requests are welcome. Please open an issue first to discuss major changes.

---

## 📜 License

MIT License — see [LICENSE](LICENSE) for details.

---

## 👤 Author

**gorfsharpem** — [github.com/gorfsharpem](https://github.com/gorfsharpem)
