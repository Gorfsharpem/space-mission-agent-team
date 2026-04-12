"""
Launch Campaign Manager Agent
------------------------------
Plans and manages the launch campaign from AIV completion
through launch and LEOP handover to operations.
"""

from agents.base_agent import BaseAgent


class LaunchCampaignAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Launch Campaign Manager",
            role="Launch Campaign Manager",
            expertise=(
                "Launch vehicle integration (Ariane, Vega, Falcon, Soyuz, PSLV, Rocket Lab), "
                "launch site operations (Kourou, Baikonur, Vandenberg, Cape Canaveral), "
                "spacecraft-to-launcher ICD, acoustic and vibration environments, "
                "launch campaign schedule (S/C delivery → launch), "
                "propellant loading and fuelling operations, "
                "launch readiness review (LRR), countdown procedures, "
                "separation confirmation, and LEOP handover."
            ),
        )

    def plan_launch_campaign(self, context: str) -> str:
        # Consult Mission Analyst for launch vehicle selection
        lv_info = ""
        if self.network and "Mission Analyst" in self.network:
            lv_info = self.ask_agent(
                "Mission Analyst",
                "Please confirm the selected launch vehicle, launch site, "
                "target orbit injection parameters, and any shared launch (rideshare) constraints.",
                context,
            )

        full_context = context
        if lv_info:
            full_context += f"\n\n### Launch vehicle inputs\n\n{lv_info}"

        task = (
            "Produce the Launch Campaign Plan.\n\n"
            "Include:\n"
            "1. **Launch Vehicle & Site** — confirmed LV, launch site, orbit injection accuracy, "
            "rideshare or dedicated launch trade\n"
            "2. **Campaign Schedule** — table: activity | duration | start week (relative to L-0) | "
            "responsible party — from S/C delivery to launch\n"
            "   Key milestones: S/C delivery to launch site, mechanical integration, "
            "electrical integration, fuelling, fairing encapsulation, rollout, launch\n"
            "3. **Spacecraft-Launcher ICD Summary** — mechanical interface (separation ring type, "
            "diameter), electrical interface (umbilical connector), load factors\n"
            "4. **Launch Site Operations** — facility requirements: cleanroom class, "
            "lifting equipment, GSE compatibility, personnel access\n"
            "5. **Fuelling & Hazardous Operations** — propellant loading sequence, "
            "safety exclusion zones, personnel PPE requirements\n"
            "6. **Launch Readiness Review (LRR) Checklist** — go/no-go criteria: "
            "spacecraft, launcher, ground segment, range, weather\n"
            "7. **Countdown Sequence** — L-6h to L+separation: key holds, abort criteria\n"
            "8. **LEOP Handover** — first contact plan, acquisition of signal (AOS) timeline, "
            "handover to operations team\n"
            "9. **Launch Campaign Risks** — launch delays, weather, range conflicts, mitigation\n"
        )
        return self.run(task, context=full_context)
