"""
QA / PA Agent
-------------
Quality Assurance and Product Assurance Engineer.
Reviews all engineering outputs at phase gates,
identifies non-conformances, and issues formal review reports.
"""

from agents.base_agent import BaseAgent


class QAPAAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="QA/PA Engineer",
            role="Quality Assurance & Product Assurance Engineer",
            expertise=(
                "ECSS quality management standards (ECSS-Q-ST-10, ECSS-Q-ST-20, ECSS-Q-ST-80), "
                "non-conformance reporting (NCR), failure mode and effects analysis (FMEA), "
                "parts, materials and processes (PMP) control, "
                "supplier quality audits, acceptance testing, "
                "design review chairing (SRR, PDR, CDR, QR, AR), "
                "flight acceptance data packages, and lessons learned management."
            ),
        )

    def phase_gate_review(self, phase_name: str, outputs: str) -> str:
        task = (
            f"Conduct a formal Phase Gate Review for **{phase_name}**.\n\n"
            "Review all outputs submitted and produce a Gate Review Report covering:\n\n"
            "1. **Review Summary** — phase name, review date, documents reviewed, attendees (roles)\n"
            "2. **Compliance Check** — table of all deliverables: "
            "expected vs delivered, completeness rating (Complete / Partial / Missing)\n"
            "3. **Non-Conformances (NCRs)** — list each NCR with:\n"
            "   - NCR-XXX: Description | Severity (Critical / Major / Minor) | "
            "Responsible engineer | Closure date\n"
            "4. **Technical Observations** — open technical risks that are not yet NCRs, "
            "watchlist items for next phase\n"
            "5. **Action Items** — table: AI-XXX | Description | Owner | Due date\n"
            "6. **Gate Decision** — one of:\n"
            "   - **PASS** — all critical items closed, proceed to next phase\n"
            "   - **CONDITIONAL PASS** — proceed with listed conditions to close\n"
            "   - **HOLD** — critical NCRs must be resolved before proceeding\n"
            "7. **Rationale** — justification for the gate decision\n"
        )
        return self.run(task, context=outputs)

    def fmea_review(self, subsystem_outputs: str) -> str:
        task = (
            "Perform a top-level Failure Mode and Effects Analysis (FMEA) review "
            "of the submitted subsystem designs.\n\n"
            "For each subsystem identify:\n"
            "1. **Critical Single Points of Failure (SPoFs)** — items where failure causes "
            "mission loss with no redundancy\n"
            "2. **Severity Classification** — Catastrophic / Critical / Marginal / Negligible\n"
            "3. **Detection Method** — how is the failure detected on-orbit?\n"
            "4. **Mitigation Status** — is redundancy or FDIR in place?\n"
            "5. **Risk Priority Number (RPN)** — Severity × Occurrence × Detectability (1-10 each)\n"
            "6. **Recommendations** — design changes or watchlist items to reduce RPN\n"
        )
        return self.run(task, context=subsystem_outputs)

    def acceptance_test_plan(self, integrated_design: str) -> str:
        task = (
            "Generate the Acceptance Test Plan (ATP) for the mission.\n\n"
            "Include:\n"
            "1. **Test Philosophy** — qualification vs acceptance levels, test-as-you-fly principle\n"
            "2. **Environmental Test Matrix** — table: vibration, acoustic, thermal vacuum (TVAC), "
            "EMC, functional — for each unit and at system level\n"
            "3. **Functional Test Sequence** — order of tests, rationale for sequence\n"
            "4. **Pass/Fail Criteria** — measurable acceptance criteria per test\n"
            "5. **Test Facility Requirements** — chamber sizes, ground support equipment (GSE)\n"
            "6. **Non-Standard Test Items** — any tests requiring waiver or deviation\n"
        )
        return self.run(task, context=integrated_design)
