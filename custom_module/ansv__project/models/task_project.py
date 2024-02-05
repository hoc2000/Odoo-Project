from time import strftime, strptime
from odoo import models, fields, api


# _,_lt to use translate langugue
def get_default_stage(self):
    default_stage = self.env['stage.tasks'].search([('sequence', '=', '0')], limit=1)
    return default_stage


class ProjectTasks(models.Model):
    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        return self.env['stage.tasks'].search([], order=order)

    _name = 'task.project.ansv'
    _inherit = ['mail.thread',
                'mail.activity.mixin',
                'portal.mixin']
    _description = "Task"
    _rec_name = 'name'
    _order = "priority desc, sequence, id desc"

    sequence = fields.Integer(string="Sequence of Tasks")
    active = fields.Boolean(string="Active", default=True)
    color = fields.Integer(string="Color")
    # header
    name = fields.Text(string="DisplayName")
    closed_days = fields.Date(string="Closed Date")

    actual_mandays = fields.Integer(string="Actual Mandays", compute="closed_date_onchange")
    estimate_mandays = fields.Integer(string="Estimate Mandays")
    upper_display_name = fields.Char(string="Upper Display Name", compute='_get_name_upper')
    child_text = fields.Char(compute="_compute_child_text")
    is_favorite = fields.Boolean(string="Favourite Tasks")
    displayed_image_id = fields.Many2one('ir.attachment',
                                         domain="[('res_model', '=', 'task.project.ansv'), ('res_id', '=', id), "
                                                "('mimetype', 'ilike', 'image')]",
                                         string='Cover Image')
    # subtasks-tự lấy của mình
    allow_subtasks = fields.Boolean(help="This will show the subtasks or not")
    parent_id = fields.Many2one('task.project.ansv', string='Parent Task', index=True)
    child_ids = fields.One2many('task.project.ansv', 'parent_id', string="Sub-tasks")
    subtask_count = fields.Integer("Sub-task Count", compute='_compute_subtask_count')

    # group
    project_id = fields.Many2one('project.ansv', string="Project")
    project_color = fields.Integer(related="project_id.color")
    # Date
    receive_date = fields.Date(string="Date Receive", default=fields.Date.context_today)
    due_date = fields.Date(string="Deadline", default=fields.Date.context_today)
    srs_receive_date = fields.Date(string="Deadline", default=fields.Date.context_today)
    date = fields.Datetime('Date', readonly=True)

    assignees_id = fields.Many2many('res.users', string='Assignees')
    current_id = fields.Integer(compute='get_current_uid', string='Assign ID Computed')
    tag_ids = fields.Many2many('project.ansv.tags', string='Tags')
    stage_id = fields.Many2one('stage.tasks', string="Stages", group_expand='_read_group_stage_ids',
                               default=get_default_stage, tracking=True)

    priority = fields.Selection([('0', 'Not Rate'), ('1', 'Medium'), ('2', 'High'), ('3', 'Urgent')],
                                string="Priority Tasks")

    # default state_selection
    status = fields.Selection([
        ('done', 'Ready'),
        ('normal', 'In Progress'),
        ('blocked', 'Blocked')], string="Status of Task", default='normal', required=True, copy=False, store=True)
    description = fields.Html(string="Description", translate=True)
    task_properties = fields.Properties('Properties', definition='project_id.task_properties_definition', copy=True)

    @api.onchange('project_id')
    def depend_project_tags(self):
        for rec in self:
            rec.tag_ids = rec.project_id.tag_ids

    @api.depends('closed_days')
    def closed_date_onchange(self):
        for rec in self:
            create_date = rec.create_date.date()
            rec.actual_mandays = (rec.closed_days - create_date).days

    @api.depends('child_ids')
    def _compute_child_text(self):
        for task in self:
            if task.subtask_count == 0:
                task.child_text = False
            elif task.subtask_count == 1:
                task.child_text = "(+ 1 task)"
            else:
                task.child_text = f"(+ {task.subtask_count} tasks)"

    @api.depends('name')
    def _get_name_upper(self):
        for rec in self:
            val = str(rec.name)
            rec.upper_display_name = val.upper()

    # OBJECT
    def get_current_uid(self):
        """
        :param self:
        :return:
        """
        if self.env.context.get('uid', False):
            self.current_id = self.env.context.get('uid', False)
        else:
            self.current_id = False

    def assign_to_me(self):
        for rec in self:
            user_array_id = []
            context = self._context
            current_uid = context.get('uid')
            current_user = self.env['res.users'].browse(current_uid)
            user_array_id.append(current_user.id)
            # Get value already exist
            for assignee in rec.assignees_id:
                if assignee.id == current_user.id:
                    continue
                assignee_id = assignee.id
                user_array_id.append(assignee_id)

            assign_value = [(6, 0, user_array_id)]
            rec.write({'assignees_id': assign_value})

    # Lựa chọn color status
    def action_open_task(self):
        return {
            'view_mode': 'form',
            'res_model': 'task.project.ansv',
            'res_id': self.id,
            'type': 'ir.actions.act_window',
        }

    def action_parent_task(self):
        return {
            'name': self.parent_id.name,
            'view_mode': 'form',
            'res_model': 'task.project.ansv',
            'res_id': self.parent_id.id,
            'type': 'ir.actions.act_window',
        }

    @api.depends('child_ids')
    def _compute_subtask_count(self):
        for rec in self:
            rec.subtask_count = self.env['task.project.ansv'].search_count([('parent_id', '=', rec.id)])

    def action_get_subtasks(self):
        return {
            'name': 'Tasks',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'task.project.ansv',
            # 'view_id': self.env.ref("mockdesk.all_ticket_view_kanban").id,
            # self.id <=> active_id
            'domain': [('parent_id', '=', self.id)],
        }

    # Mail Sending
    def action_send_mail_card(self, template_id):
        print("sending email")
        # Lấy template email
        # template_id = self.env.ref('ansv__project.task_status_mail_templates').id
        template = self.env["mail.template"].browse(template_id)
        template.send_mail(
            self.ids[0],
            force_send=True,
            raise_exception=False
        )

    def write(self, vals):
        # khởi tạo ghi giá trị vào trước rồi thực hiện hàm dưới sau
        res = super(ProjectTasks, self).write(vals)
        for rec in self:
            if 'stage_id' in vals:
                stage_id = vals['stage_id']
                stage_next = rec.env['stage.tasks'].search(
                    [('id', '=', stage_id), ])
                template_id = stage_next.mail_template_id.id
                if template_id:
                    print(template_id)
                    rec.action_send_mail_card(template_id)
                else:
                    continue
        return res

    class TaskStage(models.Model):
        _name = 'stage.tasks'
        _description = "Task Stages"
        _rec_name = 'name'
        _order = 'sequence'
        _fold_name = 'fold'

        sequence = fields.Integer(string="Sequence")
        name = fields.Char(string="Stages")
        active = fields.Boolean(string="Active", default=True)
        mail_template_id = fields.Many2one(
            'mail.template',
            string='Email Template',
            domain=[('model', '=', 'task.project.ansv')],
            help="If set, an email will be automatically sent to the customer when the task reaches this stage.")
        description = fields.Text(string="Descriptions", translate=True)
        fold = fields.Boolean(string='Folded in Kanban',
                              help='This stage is folded in the kanban view when there are no records in that stage to display.')
