
import frappe
from frappe.model.document import Document


def _score_to_rating(score):
    if score >= 15:
        return "Critical"
    elif score >= 10:
        return "High"
    elif score >= 5:
        return "Medium"
    return "Low"


class GRCRiskRegister(Document):
    def validate(self):
        self.inherent_score = int(self.impact or 0) * int(self.likelihood or 0)
        self.risk_rating = _score_to_rating(self.inherent_score)

        if self.residual_impact and self.residual_likelihood:
            self.residual_score = int(self.residual_impact or 0) * int(self.residual_likelihood or 0)
        elif not self.residual_score:
            self.residual_score = 0

        if self.risk_response == "Accept" and not self.acceptance_reference:
            frappe.msgprint(
                "Risk response is 'Accept' but no Risk Acceptance record is linked. "
                "Create a GRC Risk Acceptance record and link it here.",
                indicator="orange",
                alert=True,
            )

        if self.inherent_score >= 20 and self.escalation_status == "Normal":
            self.escalation_status = "Escalated"
            frappe.msgprint(
                f"Risk score {self.inherent_score} is very high. Escalation status set to 'Escalated'.",
                indicator="red",
                alert=True,
            )
