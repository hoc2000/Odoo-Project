from odoo import api, fields, models

class ProjectTeams(models.Model):
    _name = 'project.teams'
    _description = 'ProjectTeams'

    active = fields.Boolean(default=True)
    sequence = fields.Integer(string="Sequence")
    name = fields.Char(string="Team Name")
    # phone = fields.Char(string="Phone")
    description = fields.Text(string="Description", help="This help you inform about the team , and it's purpose")
    member_ids = fields.Many2many('res.users', domain=[('share', '=', False)], string="Team member")

