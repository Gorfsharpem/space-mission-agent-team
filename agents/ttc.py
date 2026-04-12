"""
Telemetry, Tracking & Command (TT&C) Agent
-------------------------------------------
Designs the spacecraft communications and ground contact architecture.
"""

from agents.base_agent import BaseAgent


class TTCAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="TT&C Engineer",
            role="Telemetry, Tracking & Command Engineer",
            expertise=(
                "RF communications (S-band, X-band, Ka-band, UHF/VHF), "
                "link budget analysis, antenna design and patterns, "
                "modulation and coding (BPSK, QPSK, turbo codes, LDPC), "
                "ground station network (ESTRACK, USN, SATNOGs), "
                "transponder selection, CCSDS standards, and inter-satellite links."
            ),
        )

    def design_ttc(self, context: str) -> str:
        task = (
            "Produce the TT&C Preliminary Design output.\n\n"
            "Include:\n"
            "1. **Communications Architecture** — frequency bands, links (TM, TC, ranging, payload downlink), "
            "duplex strategy\n"
            "2. **Link Budget Summary** — table showing Eb/N0, link margin (dB) for each link "
            "in worst-case geometry (low elevation, EOL EIRP)\n"
            "3. **Antenna Design** — type (omni, patch, horn, deployable dish), gain (dBi), "
            "coverage, pointing strategy\n"
            "4. **Transponder / Radio** — selected hardware or heritage design, mass, power\n"
            "5. **Ground Station Strategy** — selected network, contact frequency, "
            "daily data downlink capacity (GB/day)\n"
            "6. **Data Handling Interface** — interface with OBSW, data volume flow\n"
            "7. **Mass & Power** — total TT&C mass (kg) and peak/average power (W)\n"
            "8. **TT&C Risks** — anomaly contact windows, RF interference, mitigation\n"
        )
        return self.run(task, context=context)
