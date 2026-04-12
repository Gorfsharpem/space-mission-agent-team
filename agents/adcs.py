"""
Attitude Determination & Control System (ADCS) Agent
------------------------------------------------------
Designs the spacecraft pointing, stabilisation, and attitude control subsystem.
"""

from agents.base_agent import BaseAgent


class ADCSAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="ADCS Engineer",
            role="Attitude Determination & Control Subsystem Engineer",
            expertise=(
                "3-axis stabilisation, spin-stabilised and gravity-gradient configurations, "
                "reaction wheels, magnetorquers, thrusters, star trackers, sun sensors, "
                "magnetometers, GPS-based attitude, control law design (PID, sliding mode), "
                "pointing error budgets, and disturbance torque analysis."
            ),
        )

    def design_adcs(self, context: str) -> str:
        task = (
            "Produce the ADCS Preliminary Design output.\n\n"
            "Include:\n"
            "1. **Pointing Requirements** — required pointing accuracy and stability (arcsec or degrees) "
            "derived from payload needs\n"
            "2. **ADCS Architecture** — selected stabilisation approach with trade rationale\n"
            "3. **Actuator Selection** — reaction wheels (size, speed, torque), magnetorquers, thrusters "
            "with sizing rationale\n"
            "4. **Sensor Selection** — star trackers, sun sensors, magnetometers, gyros with accuracy specs\n"
            "5. **Disturbance Torque Budget** — gravity gradient, aerodynamic, solar radiation, magnetic\n"
            "6. **Pointing Error Budget** — allocation from requirement to sensor/actuator errors\n"
            "7. **Momentum Management** — desaturation strategy and frequency\n"
            "8. **Mass & Power** — total ADCS mass (kg) and average power (W)\n"
            "9. **ADCS Risks** — wheel failure, sensor blinding, mitigation strategies\n"
        )
        return self.run(task, context=context)
