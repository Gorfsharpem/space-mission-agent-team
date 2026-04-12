"""
On-Board Software (OBSW) Agent
--------------------------------
Designs the spacecraft flight software architecture and data handling.
"""

from agents.base_agent import BaseAgent


class OBSWAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="OBSW Engineer",
            role="On-Board Software & Data Handling Engineer",
            expertise=(
                "Flight software architecture (RTEMS, FreeRTOS, VxWorks), "
                "CCSDS Packet Utilisation Standard (PUS), SpaceWire, CAN bus, "
                "on-board computer (OBC) selection, fault detection isolation and recovery (FDIR), "
                "data management, software verification and validation (V&V), "
                "ECSS-E-ST-40 software engineering standards."
            ),
        )

    def design_obsw(self, context: str) -> str:
        task = (
            "Produce the OBSW & Data Handling Preliminary Design output.\n\n"
            "Include:\n"
            "1. **OBC Selection** — processor, memory (RAM/EEPROM/Flash), radiation tolerance, "
            "heritage, mass and power\n"
            "2. **Software Architecture** — RTOS selection, task decomposition, scheduling strategy\n"
            "3. **FDIR Concept** — fault detection levels (software watchdog, hardware watchdog, "
            "safe mode), recovery sequences\n"
            "4. **Data Management** — on-board storage sizing (GB), data prioritisation, "
            "compression strategy, housekeeping vs payload data\n"
            "5. **Internal Data Bus** — SpaceWire / CAN topology, data rates, subsystem connectivity\n"
            "6. **Ground Interface** — TC/TM packet structure (CCSDS/PUS), "
            "number of telemetry parameters, command database size\n"
            "7. **Software Development Plan** — estimated SLOC, V&V approach, "
            "use of model-based engineering\n"
            "8. **OBSW Risks** — single-event upsets, software bugs in FDIR, mitigation\n"
        )
        return self.run(task, context=context)
