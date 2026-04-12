"""
Critical Review Protocol
-------------------------
The gstack insight applied to space engineering:

  The agent takes your request literally — it never asks if you're
  building the right thing. It will implement exactly what you said,
  even when the real product is something bigger.
                                      — gstack README

The inverse of that failure mode is what we want here.
Each agent MUST challenge a change before accepting it.

This mixin adds critical_review() to any BaseAgent subclass.
The method forces the agent into an adversarial review stance:
  1. State what the change actually means for your subsystem
  2. Raise every technical objection you can find
  3. Quantify the impact (mass, power, cost, schedule)
  4. Propose alternatives if the change creates infeasibility
  5. Give a clear verdict: ACCEPT / ACCEPT WITH CONDITIONS / REJECT

Agents do NOT default to agreement.
"""

from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.change_request import ChangeRequest


CRITICAL_REVIEW_INSTRUCTIONS = """
You are performing a CRITICAL TECHNICAL REVIEW of a proposed change.

Your job is NOT to agree. Your job is to stress-test this change from your subsystem's perspective.

Rules:
- Be specific. Generic concerns like "this may affect schedule" are not acceptable.
  Every concern must name a specific parameter, interface, or requirement.
- Be quantitative wherever possible: mass budgets, power budgets, temperatures, link margins.
- Do not assume the change is correct. Assume it may be wrong or incomplete.
- If the change is technically infeasible from your perspective, say so clearly.
- If you need more information before you can assess it, state exactly what you need.
- If you have a better alternative, propose it concisely.

Your review must cover ALL FIVE of these sections — do not skip any:

1. **Impact Assessment**
   What exactly does this change do to your subsystem?
   List every parameter, interface, budget, or design choice that is affected.
   Be specific: "delta-V increases by X m/s → propellant mass increases by ~Y kg → tank must be resized."

2. **Technical Objections**
   What is wrong, risky, or unclear about this change?
   This is your chance to push back. Be critical.
   If there are no objections, explain WHY there are none (don't just say "no objections").

3. **Interface Impacts**
   Which other subsystems will be affected by the knock-on effects of this change
   as it propagates through your subsystem?
   Name them and state the nature of the impact.

4. **Alternatives or Conditions**
   If you cannot fully accept the change as stated:
   - Propose an alternative approach, OR
   - State the conditions under which you could accept it

5. **Verdict**
   One of:
   - **ACCEPT** — change is technically sound, your subsystem can absorb it
   - **ACCEPT WITH CONDITIONS** — you can accept it only if [specific conditions] are met
   - **REJECT** — change is infeasible or creates unresolvable problems from your perspective
     (a REJECT must be accompanied by a concrete alternative in section 4)

Do not end with pleasantries. End with your Verdict and nothing else.
"""


class CriticalReviewMixin:
    """
    Adds critical_review() to BaseAgent subclasses.
    """

    def critical_review(self, change_request: "ChangeRequest", mission_context: str = "") -> str:
        """
        Perform a critical, adversarial review of a ChangeRequest.

        Args:
            change_request: The CR to review.
            mission_context: Current mission baseline context.

        Returns:
            Structured review string with Impact, Objections, Verdict.
        """
        cr_text = change_request.to_markdown()

        task = (
            f"{CRITICAL_REVIEW_INSTRUCTIONS}\n\n"
            f"---\n\n"
            f"## Change Request to Review\n\n{cr_text}"
        )

        return self.run(task, context=mission_context)  # type: ignore[attr-defined]
