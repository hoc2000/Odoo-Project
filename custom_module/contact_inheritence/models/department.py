from odoo import api, fields, models


class Department(models.Model):
    _name = 'department.partner'
    _description = 'Department'

    name = fields.Char()
    partner_id = fields.One2many('res.partner', 'department_id', string="Member")
