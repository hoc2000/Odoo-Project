from odoo import models, fields, api


class TicketStages(models.Model):
    _name = 'mockdesk.stage'
    _description = 'Stages for ticket of helpdesk'
    _order = 'sequence'
    _rec_name = 'name'
    _fold_name = 'fold'

    active = fields.Boolean(default=True)
    sequence = fields.Integer(string="Sequence")
    name = fields.Char(string="Stages", copy=False)
    # domain = [('model', '=', 'task.project.ansv')],
    mail_template_id = fields.Many2one(
        'mail.template',
        string='Email Template',
        domain=[('model', '=', 'mockdesk.ticket')],
        help="If set, an email will be automatically sent to the customer when the task reaches this stage.")
    fold = fields.Boolean(string='Folded in Kanban',
                          help='This stage is folded in the kanban view when there are no records in that stage to '
                               'display.')
    description = fields.Text(string="Description")
