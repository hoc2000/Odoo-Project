import base64
import random

from odoo import models, fields, api, SUPERUSER_ID, _
from datetime import datetime, timedelta
from random import randint
import time
from threading import Thread


# Lấy default value của ticket
def get_default_stage(self):
    default_stage = self.env['mockdesk.stage'].search([('sequence', '=', '0')], limit=1)
    return default_stage


class HelpDeskTicket(models.Model):
    # fold in kanban get all stage id
    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        return self.env['mockdesk.stage'].search([], order=order)

    _name = 'mockdesk.ticket'
    _inherit = ['mail.thread', 'mail.activity.mixin',
                'rating.mixin']  # project_ansv đã có sẵn mail.mixin.activiy và thread của
    exportable = True
    _description = 'MockDesk Ticket'
    _rec_name = 'name'

    ref = fields.Char(string="Ref")
    date_created = fields.Date(string='Date Created', default=fields.Date.today())
    active = fields.Boolean(string="Active", default=True)
    create_date_js = fields.Char(string="DateTime", compute="date_to_js")
    name = fields.Char(string="Ticket Name", required=True)
    team_id = fields.Many2one('mockdesk.teams', String='Team')
    priority = fields.Selection([
        ('0', 'No Rate'),
        ('1', 'Minor'),
        ('2', 'Major'),
        ('3', 'Critical')], string="Priority")

    phone = fields.Char(string="Phone", related='customer_id.phone')
    stage_id = fields.Many2one('mockdesk.stage', string="Stage", default=get_default_stage, tracking=True,
                               group_expand='_read_group_stage_ids')
    stage_current_string = fields.Char(related='stage_id.name', string="Stage Right Now")
    email = fields.Char(String="Email", related='customer_id.email')
    assign_to = fields.Many2one('res.users', domain=[('share', '=', False)], string="Assign To")
    img_64_assignee = fields.Binary(related="assign_to.image_1920")
    deadline = fields.Date(String="Deadline", default=fields.Date.context_today, compute="_compute_deadline")
    type = fields.Many2one('mockdesk.ticket.type', string="Type")
    cc = fields.Char(string="Email cc")
    tag_id = fields.Many2many('ticket.tag', string="Tags")
    department = fields.Selection([
        ('DO', 'DO'),
        ('TASC', 'TASC'),
        ('BGD', 'BGD'),
        ('AM', 'AM')
    ], string="Department", default="DO")
    description = fields.Text()
    description_project = fields.Html()
    solution = fields.Text()
    customer_id = fields.Many2one('res.partner', string="Customer")
    partner_id = fields.Many2one('res.partner', 'Customer Partner', compute="customer_to_partner")
    user_id = fields.Many2one('res.users', 'Assign to as Partner', compute="assignee_to_user")
    # module khác
    project_id = fields.Many2one('project.ansv', string="Project")
    project_manager = fields.Many2one(related="project_id.manager_id")
    project_date_start = fields.Date(related="project_id.date_start")
    project_date_end = fields.Date(related="project_id.date_end")
    # selection của product
    product_ticket_id = fields.Many2one('product.ansv', string="Product",
                                        domain="[('project_id', '=', project_id)]")
    product_version = fields.Char(string='Version')
    product_ref = fields.Char(related="product_ticket_id.product_ref")
    product_type = fields.Selection(related="product_ticket_id.detail_type")
    product_category = fields.Many2one(related="product_ticket_id.category_id")
    ticket_components_list_id = fields.One2many(related="product_ticket_id.components_list_id",
                                                string='Component', readonly=False)
    # SLA Xử lý
    sla_status_id = fields.Many2many('individual.ticket.sla', string="SLA Deadline ID", readonly=True)
    # # Tổng thời gian hiện tại của SLA đơn
    working_time_total = fields.Float(string="Working Time", digit=(12, 1))
    is_closed = fields.Boolean(String="Ticket is Closed", required=False, default=False, compute="check_ticket_opened",
                               store=True)
    is_failed = fields.Boolean(string="Ticket Failed SLA", required=False, default=False, compute="check_ticket_failed",
                               store=True)
    is_approved = fields.Boolean(string="Ticket approved pending", default=False)
    rating_count = fields.Integer('Rating count', compute="_compute_rating_stats", compute_sudo=True, store=True)
    partner_ticket_count = fields.Integer(string="Partner Ticket Count", compute="_count_partner_ticket_count")
    partner_open_ticket_count = fields.Integer(string="Partner Open Ticket Count",
                                               compute="_count_open_partner_ticket_count")

    # bom_file_ids = fields.One2many("ir.attachment", "res_id")

    # Bảng individual of ticket and sla
    # Các trường được inherit từ model project

    def action_open_mockdesk_ticket(self):
        for rec in self:
            thisCustomer = rec.customer_id.name
            return {
                'name': thisCustomer,
                'type': 'ir.actions.act_window',
                'view_mode': 'tree,kanban,form',
                'res_model': 'mockdesk.ticket',
                # 'view_id': self.env.ref("mockdesk.all_ticket_view_kanban").id,
                'domain': [('customer_id', '=', rec.customer_id.id)],
            }

    def _count_partner_ticket_count(self):
        values = self.env['mockdesk.ticket'].search_count(
            [('customer_id', '=', self.customer_id.id)])
        self.partner_ticket_count = values

    def _count_open_partner_ticket_count(self):
        values = self.env['mockdesk.ticket'].search_count(
            [('customer_id', '=', self.customer_id.id), ('is_closed', '=', False)])
        self.partner_open_ticket_count = values

    @api.onchange('project_id')
    def _detail_project(self):
        for rec in self:
            rec.description_project = rec.project_id.description_project

    @api.onchange('stage_id')
    def update_stage_(self):
        for rec in self:
            rec.stage_current_string = rec.stage_id.name

    @api.onchange('team_id')
    def random_pick_assign_to(self):
        for rec in self:
            team_select = rec.env['mockdesk.teams'].search(
                [('id', '=', rec.team_id.id), ('auto_assignment', '=', True)])
            if team_select.member_ids:
                rec.assign_to = random.choice(team_select.member_ids)

    #
    # Button Chagne the Stage
    def action_in_progress(self):
        for rec in self:
            inprogress_stage = rec.env['mockdesk.stage'].search([('name', '=', 'In Progress')], limit=1)
            rec.stage_id = inprogress_stage
            rec.stage_current_string = rec.stage_id.name

    #
    def action_in_return_new(self):
        for rec in self:
            new_stage = rec.env['mockdesk.stage'].search([('name', '=', 'New')], limit=1)
            rec.stage_id = new_stage
            rec.stage_current_string = rec.stage_id.name

    #
    def action_done(self):
        for rec in self:
            rec.is_closed = True
            solved_stage = rec.env['mockdesk.stage'].search([('name', '=', 'Solved')], limit=1)
            rec.stage_id = solved_stage
            rec.stage_current_string = rec.stage_id.name
        return {
            'effect': {
                'fadeout': 'fast',
                'message': 'Ticket Solved',
                'type': 'rainbow_man',
            }
        }

    def action_done_effect(self):
        return {
            'effect': {
                'fadeout': 'fast',
                'message': 'Ticket Solved',
                'type': 'rainbow_man',
            }
        }

    def action_cancel(self):
        for rec in self:
            rec.is_closed = True
            cancel_stage = rec.env['mockdesk.stage'].search([('name', '=', 'Cancelled')], limit=1)
            rec.stage_id = cancel_stage
            rec.stage_current_string = rec.stage_id.name

    def assign_to_me(self):
        for rec in self:
            context = self._context
            current_uid = context.get('uid')
            current_user = self.env['res.users'].browse(current_uid)
            rec.assign_to = current_user

    # # =====================================================================================================================
    # Khởi tạo SLA
    @api.model
    def create(self, vals):
        # Gán Follower
        # Tìm các SLA thỏa mãn
        # Gửi file vào message
        global attachment_received
        if 'attachment_ids' in vals:
            attachment_received = vals['attachment_ids']
        else:
            attachment_received = 'null'
        vals.pop('attachment_ids', None)
        # Gán Ref
        if not self.ref and not vals.get('ref'):
            vals['ref'] = self.env['ir.sequence'].next_by_code('ticket.mockdesk')
            if 'priority' not in vals:
                vals['priority'] = False
            if 'project_id' not in vals:
                vals['project_id'] = False
            if 'team_id' not in vals:
                vals['team_id'] = False

            sla_list = self.env['sla.policy.ansv'].search(
                [('priority', '=', vals['priority']), ('project_id', '=', vals['project_id']),
                 ('team_id', '=', vals['team_id'])
                 ])
            # Lấy stage mới tạo default ó nó sẽ là 'NEW'
            working_time = 0
            if sla_list:
                next_stage = int(self.stage_id.sequence) + 1
                sla_reach = self.env['sla.policy.ansv'].search(
                    [('priority', '=', vals['priority']), ('project_id', '=', vals['project_id']),
                     ('team_id', '=', vals['team_id']), ('reach_stage.sequence', '=', next_stage)])
                print(sla_reach.id)
                # Cần check nếu như SLA chỉ có duy nhất mà nó cách ra Reach Stage khởi tạo thì cần tìm SLA thỏa mãn
                while not sla_reach.id:
                    next_stage += 1
                    sla_reach_new = self.env['sla.policy.ansv'].search(
                        [('priority', '=', vals['priority']), ('project_id', '=', vals['project_id']),
                         ('team_id', '=', vals['team_id']), ('reach_stage.sequence', '=', next_stage)])
                    sla_reach = sla_reach_new
                    print(sla_reach_new)

                working_time = sla_reach.working_time

            sla_id = []
            stage_excluded = []
            for sla in sla_list:
                for stage in sla.stages_excluded_id:
                    stage_excluded.append(stage.id)
                # Tạo 1  sla riêng biệt ?? cho ticket
                indi_sla_val = {}
                indi_sla_val.update({
                    'color': sla.color,
                    'name': sla.name,
                    'project_id': sla.project_id.id,
                    'team_id': sla.team_id.id,
                    'priority': sla.priority,
                    'reach_stage': sla.reach_stage.id,
                    'sequence': sla.sequence,
                    'working_time': sla.working_time,
                    'stages_excluded_id': [(6, 0, stage_excluded)],
                    'ticket_ref': vals['ref']
                })
                self.env['individual.ticket.sla'].create(indi_sla_val)
            # Gắn giá trị individual vào
            sla_individual = self.env['individual.ticket.sla'].search(
                [('ticket_ref', '=', vals['ref']), ])

            for sla_inv in sla_individual:
                sla_id.append(sla_inv.id)
            # Thêm vào vals của hàm write
            sla_value = [(6, 0, sla_id)]
            # print(sla_value)
            vals.update({'sla_status_id': sla_value, 'working_time_total': working_time})
        new_record = super(HelpDeskTicket, self).create(vals)
        # new_record.message_subscribe(partner_ids=[vals['customer_id']])
        if attachment_received != 'null':
            attachment = attachment_received.read()
            new_attachment = self.env['ir.attachment'].create({
                'name': attachment_received.filename,
                'type': 'binary',
                'datas': base64.b64encode(attachment),
                'res_id': new_record.id,
                'res_model': 'mockdesk.ticket',  # Model of the record you want to link to
            })
            message = self.env['mail.message'].create({
                'subject': 'Attachment from Customoer',
                'body': 'Here the Attachment supporting',
                'model': 'mockdesk.ticket',
                'res_id': new_record.id,  # Model of the record you want to link to
                'record_name': vals['name'],
                'attachment_ids': [(6, 0, [new_attachment.id])],  # Attach the created attachment
            })
        return new_record

    # WRITE Cập nhật SLA
    def write(self, vals):
        # print(vals)
        global res
        for rec in self:
            working_time = 0
            if 'stage_id' in vals:
                # find if this stage make close ticket
                stage_closed = rec.env['mockdesk.stage'].search(
                    [('name', 'in', ['Solved', 'Cancelled']), ])
                for i in stage_closed:
                    if vals['stage_id'] == i.id:
                        rec.is_closed = True
                # Tìm working time
                # vals.update({'working_time_total': working_time})
                # super(HelpDeskTicket, self).write(vals)
                # truyền id của thằng stage mói chuyển vào
                rec.change_state_sla(vals['stage_id'], rec.sla_status_id)
                working_time = rec.get_working_time(vals['stage_id'], rec.sla_status_id)

            # Giá trị mặc định nếu nó đã tồn tại
            priority_write = rec.priority
            project_write = rec.project_id.id
            team_write = rec.team_id.id
            # Nếu nó thay đổi thì gán giá trị thay đổi vào trong
            if 'priority' in vals:
                priority_write = vals['priority']
            if 'project_id' in vals:
                project_write = vals['project_id']
            if 'team_id' in vals:
                team_write = vals['team_id']
                # Tìm kiếm giá trị của sla
                # print("vals")
            sla_list = rec.env['sla.policy.ansv'].search(
                [('priority', '=', priority_write), ('project_id', '=', project_write),
                 ('team_id', '=', team_write)
                 ])
            sla_individual_existed = rec.env['individual.ticket.sla'].search(
                [('ticket_ref', '=', rec.ref)])
            sla_id = []
            sla_exist_name = []
            stage_excluded = []
            if sla_list:
                for sla_exist in sla_individual_existed:
                    sla_exist_name.append(sla_exist.name)
                for sla in sla_list:
                    # print(sla.stages_excluded_id)
                    if sla.name in sla_exist_name:
                        break
                    for stage in sla.stages_excluded_id:
                        stage_excluded.append(stage.id)
                    else:
                        # print(sla)
                        indi_sla_val = {}
                        indi_sla_val.update({
                            'color': sla.color,
                            'name': sla.name,
                            'project_id': sla.project_id.id,
                            'team_id': sla.team_id.id,
                            'priority': sla.priority,
                            'reach_stage': sla.reach_stage.id,
                            'sequence': sla.sequence,
                            'working_time': sla.working_time,
                            'stages_excluded_id': [(6, 0, stage_excluded)],
                            'ticket_ref': rec.ref
                        })
                        rec.env['individual.ticket.sla'].create(indi_sla_val)
                    # Gắn giá trị individual vào
                sla_individual = rec.env['individual.ticket.sla'].search(
                    [('ticket_ref', '=', rec.ref), ('priority', '=', priority_write),
                     ('project_id', '=', project_write), ('team_id', '=', team_write)])
                # xóa ticket exist cũ
                sla_individual_diff = rec.env['individual.ticket.sla'].search(
                    [('ticket_ref', '=', rec.ref), '|', '|', ('priority', '!=', priority_write),
                     ('project_id', '!=', project_write), ('team_id', '!=', team_write)])
                sla_individual_diff.unlink()
                for sla_inv in sla_individual:
                    sla_id.append(sla_inv.id)
                if 'stage_id' not in vals:
                    next_stage = int(rec.stage_id.sequence) + 1
                    sla_reach = rec.env['individual.ticket.sla'].search(
                        [('reach_stage.sequence', '=', next_stage), ('id', 'in', sla_id)])
                    working_time = sla_reach.working_time
            # Thêm vào vals của hàm write
            sla_value = [(6, 0, sla_id)]
            # print(sla_value)
            vals.update({'sla_status_id': sla_value, 'working_time_total': working_time})
            res = super(HelpDeskTicket, self).write(vals)
            if 'stage_id' in vals:
                # mail send
                stage_id = vals['stage_id']
                stage_next = rec.env['mockdesk.stage'].search(
                    [('id', '=', stage_id), ])
                template_id = stage_next.mail_template_id.id
                if template_id:
                    print(template_id)
                    rec.action_send_mail_card(template_id)
                else:
                    continue
                if stage_next.name == "Solved":
                    rec.action_done_effect()
        return res

    # xóa bớt sla individual
    def unlink(self):
        for rec in self:
            sla_to_delete = rec.env['individual.ticket.sla'].search(
                [('ticket_ref', '=', rec.ref,)])
            sla_to_delete.unlink()
        return super(HelpDeskTicket, self).unlink()

    # data-color="1" title="Red # data-color="2" title="Orange"  # data-color="3" title="Yellow"  # data-color="4"
    # title="Light blue" # data-color="5" title="Dark purple"# data-color="6" title="Salmon pink" # data-color="7"
    # title="Medium blue" # data-color="8" title="Dark blue"# data-color="9" title="Fushia" # data-color="10"
    # title="Green" # data-color="11" title="Purple
    def change_state_sla(self, stage_id, sla_list):
        today = datetime.today().date()
        # Tim stage dang o hien tai # Default
        for rec in self:
            stage_update = rec.env['mockdesk.stage'].search(
                [('id', '=', stage_id)])
            for sla in sla_list:
                if stage_update.sequence < sla.reach_stage.sequence:
                    next_stage = int(stage_update.sequence) + 1
                    # xét trong các sla mà ticket sở hữu
                    if sla.reach_stage.sequence == next_stage:
                        # print('sla cần đạt được:' + sla.name)
                        rec.working_time_total = sla.working_time
                    sla.color = 0

                elif sla.reach_stage == stage_update:
                    if rec.deadline:
                        if rec.deadline < today:
                            sla.sla_failed = True
                            sla.color = 1
                            rec.working_time_total = 0
                        else:
                            sla.color = 10
                            rec.working_time_total = 0

                elif sla.reach_stage.sequence <= stage_update.sequence:
                    if rec.deadline:
                        if rec.deadline < today:
                            sla.color = 1
                            rec.working_time_total = 0
                        else:
                            if not sla.sla_failed:
                                sla.color = 10
                                rec.working_time_total = 0

    def get_working_time(self, stage_id, sla_list):
        timework = 0
        stage_current = self.env['mockdesk.stage'].search(
            [('id', '=', stage_id)])
        next_stage = int(stage_current.sequence) + 1
        for sla in sla_list:
            if stage_current.sequence <= sla.reach_stage.sequence:
                # xét trong các sla mà ticket sở hữu
                if sla.reach_stage.sequence == next_stage:
                    timework = sla.working_time
            elif sla.reach_stage == stage_current:
                timework = 0
            elif sla.reach_stage.sequence <= stage_current.sequence:
                timework = 0
        return timework

    # # =============================================================================================================
    # # Tính remaining day
    @api.depends('working_time_total')
    def _compute_deadline(self):
        for rec in self:
            if rec.working_time_total:
                daycreate = rec.create_date.date()
                timework = rec.working_time_total
                day_of_work = round(timework / 8)
                delta = timedelta(days=day_of_work)
                new_deadline = daycreate + delta
                rec.deadline = new_deadline
            else:
                rec.deadline = False

    #
    @api.depends('create_date')
    def date_to_js(self):
        for rec in self:
            rec.create_date_js = rec.create_date.isoformat()

    #
    @api.depends('sla_status_id')
    def check_ticket_failed(self):
        for rec in self:
            if rec.sla_status_id:
                for sla in rec.sla_status_id:
                    if sla.sla_failed:
                        rec.is_failed = True
            else:
                rec.is_failed = False

    @api.depends('stage_id')
    def check_ticket_opened(self):
        for rec in self:
            for stage in rec.stage_id:
                if stage.name in ['Solved', 'Cancelled']:
                    rec.is_closed = True
                else:
                    rec.is_closed = False

    @api.depends('customer_id')
    def customer_to_partner(self):
        for rec in self:
            rec.partner_id = rec.customer_id

    @api.depends('assign_to')
    def assignee_to_user(self):
        for rec in self:
            rec.user_id = rec.assign_to

    @api.model
    def test_cron_job(self):
        today = datetime.today().date()
        records = self.env['mockdesk.ticket'].search([])
        for rec in records:
            if rec.deadline and rec.deadline < today:
                next_stage_seq = int(rec.stage_id.sequence) + 1
                stage_change = self.env['mockdesk.stage'].search(
                    [('sequence', '=', next_stage_seq), ])
                rec.write({'stage_id': stage_change.id})
        print("update Cron OK")

    def action_send_mail_card(self, template_id):
        # Lấy template email
        # template_id = self.env.ref('mockdesk.ticket_card_mail_templates').id
        template = self.env["mail.template"].browse(template_id)
        template.send_mail(
            self.ids[0],
            force_send=True,
            raise_exception=False
        )
        return True

    # @api.model
    # def message_new(self, msg, custom_values=None):
    #     """ Overrides mail_thread message_new that is called by the mailgateway
    #         through message_process.
    #         This override updates the document according to the email.
    #     """
    #     # remove default author when going through the mail gateway. Indeed we
    #     # do not want to explicitly set user_id to False; however we do not
    #     # want the gateway user to be responsible if no other responsible is
    #     # found.
    #     if custom_values is None:
    #         custom_values = {}
    #     defaults = {
    #         'name': msg.get('subject') or _("No Subject"),
    #         'customer_id': msg.get('author_id')
    #     }
    #     defaults.update(custom_values)
    #     p_ticket = super(HelpDeskTicket, self).message_new(msg, custom_values=defaults)
    #     return p_ticket

    # ACTION OPEN:
    def action_open_ratings(self):
        for rec in self:
            currTicket = rec.name
            return {
                'name': currTicket,
                'type': 'ir.actions.act_window',
                'view_mode': 'kanban,form',
                'res_model': 'rating.rating',
                'view_type': 'form',
                'target': 'current',
                'domain': [('res_id', '=', rec.id), ('consumed', '=', True)]
            }

    def action_open_solution_wizard(self):
        for rec in self:
            return {
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'solution.ticket.wizard',
                'target': 'new',
            }

    # Report
    def _get_report_base_filename(self):
        return "Ticket Report"
