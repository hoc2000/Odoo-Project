from datetime import date
from odoo import api, fields, models


class HospitalPatient(models.Model):
    _name = "hospital.patient"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Hospital Patient"
    _rec_name = "name"

    name = fields.Char(string="Name", tracking=True)
    ref = fields.Char(string="reference")
    date_of_birth = fields.Date(string="Date of birth")
    age = fields.Integer(string="Age", compute='compute_age', store=True)
    gender = fields.Selection(
        [('male', 'Male'),
         ('female', 'Female')]
        , string="Gender")
    active = fields.Boolean(string="Active", default=True)
    appointment_id = fields.Many2one(comodel_name='hospital.appointment', string="Appointment")
    image = fields.Image(string="image")
    tag_id = fields.Many2many('patient.tag', string="Tags")

    @api.model
    def create(self, vals):
        # print(vals)
        vals['ref'] = self.env['ir.sequence'].next_by_code('hospital.patient')
        return super(HospitalPatient, self).create(vals)


    def write(self, vals):
        if not self.ref and not vals.get('ref'):
            vals['ref'] = self.env['ir.sequence'].next_by_code('hospital.patient')
        return super(HospitalPatient, self).write(vals)

    @api.depends('date_of_birth')
    def compute_age(self):
        today = date.today()
        for rec in self:
            if rec.date_of_birth:
                rec.age = today.year - rec.date_of_birth.year
            else:
                rec.age = 0


    def name_get(self):
        patient_list = []
        for rec in self:
            name = "[%s] %s" % (rec.ref, rec.name)
            patient_list.append((rec.id, name))
        return patient_list
