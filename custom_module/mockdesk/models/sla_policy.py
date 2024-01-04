from odoo import models, fields, api
from odoo.exceptions import ValidationError


class SLA(models.Model):
    _name = 'sla.policy.ansv'
    _description = 'SLA of Ticket Team'
    _rec_name = 'name'
    _order = 'sequence asc'

    color = fields.Integer()
    name = fields.Char(string="SLA Name", required=True, copy=False)
    description = fields.Html()
    team_id = fields.Many2one('helpdesk.teams', string="Team", required=True)
    priority = fields.Selection([
        ('0', 'No Rate'),
        ('1', 'Minor'),
        ('2', 'Major'),
        ('3', 'Critical')], string="Priority", required=True)
    type_id = fields.Many2one('helpdesk.ticket.type', string="Type", editable=False)
    tag_id = fields.Many2many('ticket.tag', string="Tags")
    project_id = fields.Many2one('project.ansv', string="Project", required=True)

    # Target calculated
    reach_stage = fields.Many2one('helpdesk.stage', string="Reach Stage", required=True)
    sequence = fields.Integer(string="Sequence")
    working_time = fields.Float(string="Working Time", default=0)
    stages_excluded_id = fields.Many2many('helpdesk.stage', string="Excluding Stages")

    @api.onchange('reach_stage')
    def sequence_sla(self):
        for rec in self:
            rec.sequence = rec.reach_stage.sequence

    @api.constrains('name', 'description', 'team_id', 'priority', 'reach_stage')
    def _check_description(self):
        for record in self:
            duplicate_sla = self.env['sla.policy.ansv'].search([
                ('team_id', '=', record.team_id.id),
                ('priority', '=', record.priority),
                ('project_id', '=', record.project_id.id),
                ('reach_stage', '=', record.reach_stage.id),
                ('id', '!=', record.id),
            ])
            if duplicate_sla:
                raise ValidationError(
                    f"There already existed the SLA ({duplicate_sla.name}) have Team, Project, Priority, Reach Stages satisfied ,Please change !!!")
            # if record.name == record.description:
            #     raise ValidationError("Fields name and description must be different")


class SLA_RELATION(models.Model):
    _name = "individual.ticket.sla"
    _inherit = ["sla.policy.ansv"]
    _rec_name = 'name'
    _order = 'sequence asc'

    ticket_id = fields.Many2one('helpdesk.ticket', string="Ticket")
    ticket_ref = fields.Char(string="Ticket Ref")
    deadline = fields.Date(String="Deadline")
    sla_failed = fields.Boolean(string="Failed SLA")

    @api.constrains('name', 'description', 'team_id', 'priority', 'reach_stage')
    def _check_description(self):
        pass

