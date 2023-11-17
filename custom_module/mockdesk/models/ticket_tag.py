from odoo import models, fields, api


class TicketTag(models.Model):
    _name = 'ticket.tag'
    _description = 'Tag for ticket'

    name = fields.Char(string="Ticket Name")
    color = fields.Integer(string="Color")
