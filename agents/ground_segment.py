"""
Ground Segment Engineer Agent
------------------------------
Designs the ground station network, mission control infrastructure,
flight dynamics, and operations concept.
"""

from agents.base_agent import BaseAgent


class GroundSegmentAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Ground Segment Engineer",
            role="Ground Segment & Operations Engineer",
            expertise=(
                "Ground station network design (ESTRACK, USN, SATNOGs, commercial networks), "
                "mission control system (MCS) architecture, flight dynamics system (FDS), "
                "operations concept (CONOPS), spacecraft simulator, "
                "launch and early operations (LEOP) planning, "
                "routine operations phase planning, anomaly resolution procedures, "
                "ground-to-space interface (ICD), and end-of-life operations."
            ),
        )

    def design_ground_segment(self, context: str) -> str:
        # Consult TT&C for link requirements
        ttc_info = ""
        if self.network and "TT&C Engineer" in self.network:
            ttc_info = self.ask_agent(
                "TT&C Engineer",
                "Please provide the ground station contact frequency, contact duration, "
                "uplink/downlink frequencies, data volume per pass, and antenna requirements "
                "I need to design the ground segment.",
                context,
            )

        full_context = context
        if ttc_info:
            full_context += f"\n\n### TT&C inputs\n\n{ttc_info}"

        task = (
            "Produce the Ground Segment Preliminary Design.\n\n"
            "Include:\n"
            "1. **Ground Station Network** — selected stations with location, antenna diameter, "
            "frequency capability, contact schedule table (passes/day, duration, elevation)\n"
            "2. **Mission Control System (MCS)** — architecture: commanding, telemetry processing, "
            "archiving, display; COTS vs custom trade\n"
            "3. **Flight Dynamics System (FDS)** — orbit determination, manoeuvre planning, "
            "conjunction analysis tools\n"
            "4. **CONOPS** — operations phases table: LEOP (0-72h) / IOC / routine / EOL, "
            "team size per phase, shift pattern\n"
            "5. **Spacecraft Simulator** — real-time simulator requirements for operator training "
            "and anomaly investigation\n"
            "6. **Ground-Space ICD Summary** — TC/TM formats, data rates, encryption, authentication\n"
            "7. **Operations Cost Estimate** — annual FTE count, station rental, software licences\n"
            "8. **Ground Segment Risks** — single ground station risk, software delivery, "
            "operator training timeline\n"
        )
        return self.run(task, context=full_context)
