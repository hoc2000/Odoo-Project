from odoo import api, fields, models

STATUS_COLOR = {
    'on_track': 10,  # green / success
    'at_risk': 2,  # orange
    'off_track': 1,  # red / danger
    'on_hold': 4,  # light blue
    False: 0,  # default grey -- for studio
    # Only used in project.task
    'to_define': 0,
}


class ProjectUpdates(models.Model):
    _name = 'project.update'
    _description = 'ProjectUpdates'
    _rec_name = 'title'
    _order = 'create_date desc'

    title = fields.Char(string="Title", help="project update title")
    progress = fields.Integer(string="Progress of the Project", tracking=True)
    progress_percentage = fields.Float(compute='_compute_progress_percentage')
    user_id = fields.Many2one('res.users', string='User Update', required=True, default=lambda self: self.env.user)
    project_id = fields.Many2one('project.ansv', help="Individual projecct update")
    status = fields.Selection([
        ('on_track', 'On Track'),
        ('at_risk', 'At Risk'),
        ('off_track', 'Off Track'),
        ('on_hold', 'On Hold')
    ], string="Status of Task", copy=False, store=True)
    color = fields.Integer(compute='_compute_color')
    update_date = fields.Date(string="Update Date", default=fields.Date.context_today, tracking=True,
                              help="Date that project update the status,...")
    summary = fields.Html(help="This is some description of project udpate status, what update or more info about this")

    @api.depends('status')
    def _compute_color(self):
        for update in self:
            update.color = STATUS_COLOR[update.status]

    @api.depends('progress')
    def _compute_progress_percentage(self):
        for u in self:
            u.progress_percentage = u.progress / 100

    # ---------------------------
    # Change update status
    # ---------------------------
    @api.model_create_multi
    def create(self, vals_list):
        updates = super().create(vals_list)
        print(updates)
        for update in updates:
            print(update.project_id.project_name)
            update.project_id.sudo().last_update_id = update
        return updates
