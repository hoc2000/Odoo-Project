from odoo import api, fields, models


class HospitalAppointment(models.Model):
    _name = "hospital.appointment"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Hospital Appointment"
    _rec_name = "ref"

    patient_id = fields.Many2one(comodel_name='hospital.patient', string="Patient")
    booking = fields.Date(string="Booking", default=fields.Date.context_today)
    gender = fields.Selection(related='patient_id.gender')
    appointment_time = fields.Datetime(string="Appointment Time", default=fields.Datetime.now)
    ref = fields.Char(string="reference")
    prescription = fields.Html(string="Prescription")
    priority = fields.Selection([
        ('0', 'Bad'),
        ('1', 'Normal'),
        ('2', 'Good'),
        ('3', 'Very good')], string="Priority")

    state = fields.Selection([
        ('draft', 'Draft'),
        ('in_progress', 'In Progress'),
        ('done', 'Done'),
        ('cancel', 'Cancel')], default="draft", string="Status", required=True)
    doctor_id = fields.Many2one(comodel_name='res.users', string="Doctor", tracking=True)
    pharmacy_line_ids = fields.One2many('appointment.pharmacy.lines', 'appointment_id', string="Pharmacy Lines")
    hide_sale_price = fields.Boolean(string="Hide Sale Price")

    @api.onchange('patient_id')
    def onChange_patient_id(self):
        self.ref = self.patient_id.ref

    def action_test(self):
        print("Button clicked!!!")
        return {
            'effect': {
                'fadeout': 'fast',
                'message': 'Click Successful',
                'type': 'rainbow_man',
            }
        }

    def action_in_progress(self):
        for rec in self:
            rec.state = 'in_progress'

    def action_done(self):
        for rec in self:
            rec.state = 'done'

    def action_cancel(self):
        action = self.env.ref('om_hospital.action_cancel_appointment').read()[0]
        return action

    def action_draft_reset(self):
        for rec in self:
            rec.state = 'draft'


# APPOINTMENT_LINES_ONE2MANY
class AppointmentPharmacyLines(models.Model):
    _name = "appointment.pharmacy.lines"
    _description = "Appointment Pharmacy Lines"

    product_id = fields.Many2one('product.product', string="product")
    price_unit = fields.Float(realated="product_id.list_price")
    qty = fields.Integer(string="Quantity", default=1)
    appointment_id = fields.Many2one('hospital.appointment', string="Appointment")
