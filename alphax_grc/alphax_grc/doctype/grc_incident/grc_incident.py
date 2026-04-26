import frappe
from frappe.model.document import Document
from frappe.utils import add_to_date, now_datetime


SLA_HOURS = {
    "Critical": 4,
    "High": 24,
    "Medium": 72,
    "Low": 168,
}


class GRCIncident(Document):
    def validate(self):
        if not self.reported_on:
            self.reported_on = now_datetime()
        self._set_sla_due_date()

    def _set_sla_due_date(self):
        if self.sla_due_date:
            return
        hours = SLA_HOURS.get(self.severity, 72)
        base = self.reported_on or now_datetime()
        self.sla_due_date = add_to_date(base, hours=hours)
