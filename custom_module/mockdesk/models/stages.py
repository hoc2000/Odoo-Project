from odoo import models, fields, api


class TicketStages(models.Model):
    _name = 'helpdesk.stage'
    _description = 'Stages for ticket of helpdesk'
    _order = 'sequence'
    _rec_name = 'name'

    sequence = fields.Integer(string="Sequence")
    name = fields.Char(string="Stages", readonly="1")
