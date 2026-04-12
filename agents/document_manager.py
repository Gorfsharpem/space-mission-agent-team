"""
Document Manager Agent
-----------------------
Maintains the mission document tree, version control,
document status tracking, and produces the Document Management Plan.
"""

from agents.base_agent import BaseAgent


class DocumentManagerAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Document Manager",
            role="Mission Document Manager",
            expertise=(
                "ECSS documentation standards (ECSS-M-ST-40), "
                "document tree management, configuration management (CM), "
                "version control (baseline management), "
                "document status tracking (draft / review / approved / released), "
                "DRL (Document Requirements List), product tree, "
                "drawing numbering and traceability, and change control boards (CCB)."
            ),
        )

    def build_document_tree(self, mission_name: str, all_outputs: dict[str, str]) -> str:
        doc_list = "\n".join(
            [f"- **{title}**: {len(content)} characters" for title, content in all_outputs.items()]
        )
        task = (
            f"Build the Mission Document Tree for **{mission_name}**.\n\n"
            f"The following documents have been produced by the team:\n{doc_list}\n\n"
            "Produce:\n"
            "1. **Document Requirements List (DRL)** — table with columns: "
            "Doc ID | Title | Author (role) | Applicable Standard | Phase | Status | Rev\n"
            "2. **Document Tree Hierarchy** — how documents relate: "
            "mission-level → system-level → subsystem-level → test documents\n"
            "3. **Numbering Convention** — document numbering schema "
            "(e.g. MISSION-SYS-001-A for first system document, rev A)\n"
            "4. **Review & Approval Matrix** — who reviews and approves each document type\n"
            "5. **Configuration Baseline** — what constitutes the Phase A, B, C baselines\n"
            "6. **Change Control Process** — how changes are raised, reviewed, and incorporated\n"
            "7. **Document Management Plan (DMP)** — tools, storage, access control, archiving\n"
        )
        return self.run(task, context="")

    def status_report(self, all_outputs: dict[str, str]) -> str:
        doc_list = "\n".join(
            [f"- {title}: {'Complete' if content else 'Missing'}" for title, content in all_outputs.items()]
        )
        task = (
            "Produce a Document Status Report.\n\n"
            f"Current document inventory:\n{doc_list}\n\n"
            "Report should include:\n"
            "1. **Status Dashboard** — counts of documents by status: "
            "Issued / In Review / Draft / Planned\n"
            "2. **Overdue Items** — documents not yet issued that are on the critical path\n"
            "3. **Upcoming Deadlines** — next 3 document milestones\n"
            "4. **Action Required** — specific items requiring immediate attention\n"
        )
        return self.run(task, context="")
