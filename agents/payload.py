"""
Payload Engineering Agent
--------------------------
Defines the mission payload, its requirements, and preliminary design.
"""

from agents.base_agent import BaseAgent


class PayloadAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Payload Engineer",
            role="Payload Systems Engineer",
            expertise=(
                "Optical, SAR, RF, and scientific payloads; detector technologies; "
                "optical design (resolution, swath, SNR); RF link budgets; "
                "calibration strategies; data volume estimation; "
                "payload-platform interface requirements."
            ),
        )

    def design_payload(self, context: str) -> str:
        task = (
            "Produce the Payload Preliminary Design output.\n\n"
            "Include:\n"
            "1. **Payload Concept** — selected payload type and technology with trade rationale\n"
            "2. **Key Performance Parameters** — resolution, swath, sensitivity, frequency band, etc.\n"
            "3. **Mass & Volume Envelope** — estimated mass (kg) and dimensions (mm)\n"
            "4. **Power Profile** — peak, average, standby power (W)\n"
            "5. **Data Volume** — raw data rate (Mbps) and daily data volume (GB)\n"
            "6. **Thermal Requirements** — operating and survival temperature ranges\n"
            "7. **Interface Requirements** — mechanical, electrical, and data interfaces to platform\n"
            "8. **Calibration & Verification** — how payload performance will be verified on-orbit\n"
            "9. **Payload Risks** — top risks with mitigation\n"
        )
        return self.run(task, context=context)
