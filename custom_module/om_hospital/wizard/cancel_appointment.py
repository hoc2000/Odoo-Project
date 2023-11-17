from odoo import api, fields, models
import datetime

class CancelAppointmentWizard(models.TransientModel):
    _name = "cancel.appointment.wizard"
    _description = "Cancel Appointment"

    @api.model
    def default_get(self, fields_list):
        res = super(CancelAppointmentWizard, self).default_get(fields_list)
        print("Default get", res)
        res['cancel_date'] = datetime.date.today()
        return res

    appointment_id = fields.Many2one('hospital.appointment', string="Appointment")
    reason = fields.Text(string="Reason", default="What's your reason")
    cancel_date = fields.Date(string="Cancellation Date")

    def action_cancel(self):
        self.appointment_id.state = "cancel"
