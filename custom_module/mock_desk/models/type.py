from odoo import models, fields, api


class TypeTicket(models.Model):
    _name = 'mockdesk.ticket.type'
    _description = 'this is type of ticket'
    _rec_name = 'type_name'
    
    sequence = fields.Integer()
    type_name = fields.Char(string="Name")
