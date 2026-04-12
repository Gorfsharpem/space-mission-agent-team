"""
Antenna Engineer Agent
-----------------------
Designs all spacecraft antennas: TT&C, payload downlink, inter-satellite links.
Works closely with TT&C and Payload agents.
"""

from agents.base_agent import BaseAgent


class AntennaAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Antenna Engineer",
            role="RF Antenna Design Engineer",
            expertise=(
                "Antenna design (patch, horn, helical, reflector, phased array), "
                "antenna gain and radiation pattern analysis, "
                "polarisation (LHCP, RHCP, linear), axial ratio, "
                "impedance matching (50 Ohm), VSWR, "
                "near-field / far-field testing, antenna placement and pattern distortion "
                "due to spacecraft body, deployable reflector design, "
                "S-band / X-band / Ka-band / UHF antenna design."
            ),
        )

    def design_antennas(self, context: str) -> str:
        # Consult TT&C for link budget requirements
        ttc_info = ""
        if self.network and "TT&C Engineer" in self.network:
            ttc_info = self.ask_agent(
                "TT&C Engineer",
                "Please provide the antenna gain requirements (dBi), frequency bands, "
                "polarisation, coverage requirements (elevation mask), and pointing "
                "constraints I must design to for TT&C and payload downlink.",
                context,
            )

        # Consult Payload for data downlink antenna requirements
        payload_info = ""
        if self.network and "Payload Engineer" in self.network:
            payload_info = self.ask_agent(
                "Payload Engineer",
                "Does the payload require a dedicated high-gain antenna for data downlink? "
                "If so, what are the required gain, frequency, beamwidth, and pointing accuracy?",
                context,
            )

        full_context = context
        if ttc_info:
            full_context += f"\n\n### TT&C antenna requirements\n\n{ttc_info}"
        if payload_info:
            full_context += f"\n\n### Payload antenna requirements\n\n{payload_info}"

        task = (
            "Produce the Antenna Design Preliminary Output.\n\n"
            "Include:\n"
            "1. **Antenna Inventory** — table of all antennas on the spacecraft: "
            "function, frequency band, type, polarisation, quantity\n"
            "2. **TT&C Antenna Design** — omni coverage strategy (low-gain antennas), "
            "gain (dBi), beamwidth, placement to ensure hemispherical coverage\n"
            "3. **Payload / High-Gain Antenna Design** — reflector or phased array trade, "
            "aperture size, gain (dBi), pointing mechanism if steerable\n"
            "4. **Radiation Pattern Analysis** — expected pattern distortion from spacecraft "
            "body, solar array blockage, mitigation (placement, ground plane)\n"
            "5. **Impedance Matching & Feed Network** — waveguide vs coax, VSWR budget, "
            "diplexers and switches if required\n"
            "6. **Deployment & Pointing** — fixed vs deployable vs steerable, "
            "pointing accuracy requirement vs mechanism trade\n"
            "7. **Test Plan** — antenna pattern measurement approach (near-field, far-field, "
            "or compact range), on-orbit verification\n"
            "8. **Mass & Envelope** — antenna mass and stowed/deployed dimensions\n"
            "9. **Antenna Risks** — deployment failure, pattern degradation, interference, "
            "mitigation\n"
        )
        return self.run(task, context=full_context)
