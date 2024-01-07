from odoo import models, fields, api
from random import randint


class TicketTag(models.Model):
    _name = 'ticket.tag'
    _description = 'Tag for ticket'

    def _get_default_color(self):
        return randint(1, 11)

    name = fields.Char(string="Ticket Name" )
    color = fields.Integer(string="Color", default=_get_default_color,)

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "A tag with the same name already exists."),
    ]
