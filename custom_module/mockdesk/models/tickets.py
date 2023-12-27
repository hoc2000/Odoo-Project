from odoo import models, fields, api, SUPERUSER_ID
from datetime import datetime, timedelta
import time
from threading import Thread


# Lấy default value của ticket
def get_default_stage(self):
    default_stage = self.env['helpdesk.stage'].search([('sequence', '=', '0')], limit=1)
    return default_stage

class HelpDeskTicket(models.Model):
    # fold in kanban get all stage id
    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        return self.env['helpdesk.stage'].search([], order=order)

    _name = 'helpdesk.ticket'
    _inherit = ['project.ansv']  # project_ansv đã có sẵn mail.mixin.activiy và thread của mail
    _description = 'Ticket of MockDesk'
    _rec_name = 'name'

    ref = fields.Char(string="Ref")
    active = fields.Boolean(string="Active", default=True)
    name = fields.Char(string="Ticket Name", required=True)
    team_id = fields.Many2one('helpdesk.teams', String='Team', required=True)
    priority = fields.Selection([
        ('0', 'No Rate'),
        ('1', 'Minor'),
        ('2', 'Major'),
        ('3', 'Critical')], string="Priority")

    phone = fields.Char(string="Phone", related='customer_id.phone')
    stage_id = fields.Many2one('helpdesk.stage', string="Stage", default=get_default_stage, tracking=True,
                               group_expand='_read_group_stage_ids')
    stage_current_string = fields.Char(string="Stage Right Now")
    email = fields.Char(String="Email", related='customer_id.email')
    assign_to = fields.Many2one('res.users', string="Assign To")
    deadline = fields.Date(String="Deadline", default=fields.Date.context_today, compute="_compute_deadline")
    type = fields.Many2one('helpdesk.ticket.type', string="Type")
    cc = fields.Char(string="Email cc")
    tag_id = fields.Many2many('ticket.tag', string="Tags")
    department = fields.Selection([
        ('DO', 'DO'),
        ('TASC', 'TASC'),
        ('BGD', 'BGD'),
        ('AM', 'AM')
    ], string="Department", default="DO")
    description = fields.Html()
    customer_id = fields.Many2one('res.partner', string="Customer")
    # module khác
    project_id = fields.Many2one('project.ansv', string="Project")
    # selection của product
    product_ticket_id = fields.Many2one('product.ansv', string="Product",
                                        domain="[('project_id', '=', project_id)]")
    ticket_components_list_id = fields.One2many(related="product_ticket_id.components_list_id",
                                                string='Component', readonly=False)
    # SLA Xử lý
    sla_status_id = fields.Many2many('individual.ticket.sla', string="SLA Deadline ID", readonly=True)
    # Tổng thời gian hiện tại của SLA đơn
    working_time_total = fields.Float(string="Working Time", digit=(12, 1))
    is_closed = fields.Boolean(String="Ticket is Closed", default=False)

    # Bảng individual of ticket and sla
    # Các trường được inherit từ model project
    @api.onchange('project_id')
    def _detail_project(self):
        for rec in self:
            rec.project_name = rec.project_id.project_name
            rec.description_project = rec.project_id.description_project

    @api.onchange('stage_id')
    def update_stage_(self):
        for rec in self:
            rec.stage_current_string = rec.stage_id.name

    # Button Chagne the Stage
    def action_in_progress(self):
        for rec in self:
            inprogress_stage = rec.env['helpdesk.stage'].search([('name', '=', 'In Progress')], limit=1)
            rec.stage_id = inprogress_stage
            rec.stage_current_string = rec.stage_id.name

    def action_in_return_new(self):
        for rec in self:
            new_stage = rec.env['helpdesk.stage'].search([('name', '=', 'New')], limit=1)
            rec.stage_id = new_stage
            rec.stage_current_string = rec.stage_id.name

    def action_done(self):
        for rec in self:
            rec.is_closed = True
            solved_stage = rec.env['helpdesk.stage'].search([('name', '=', 'Solved')], limit=1)
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
            cancel_stage = rec.env['helpdesk.stage'].search([('name', '=', 'Cancelled')], limit=1)
            rec.stage_id = cancel_stage
            rec.stage_current_string = rec.stage_id.name

    # =====================================================================================================================
    # Khởi tạo SLA
    @api.model
    def create(self, vals):
        # Tìm các SLA thỏa mãn
        # Gán Ref
        if not self.ref and not vals.get('ref'):
            vals['ref'] = self.env['ir.sequence'].next_by_code('ticket.helpdesk')

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
        for sla in sla_list:
            # Tạo 1  sla riêng biệt ?? cho ticket
            indi_sla_val = {}
            indi_sla_val.update({
                'color': sla.color,
                'name': sla.name,
                'project_id': sla.project_id.id,
                'team_id': sla.team_id.id,
                'priority': sla.priority,
                'type_id': sla.type_id.id,
                'reach_stage': sla.reach_stage.id,
                'sequence': sla.sequence,
                'working_time': sla.working_time,
                'stages_excluded_id': sla.stages_excluded_id.id,
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
        return super(HelpDeskTicket, self).create(vals)

    # WRITE Cập nhật SLA
    def write(self, vals):
        # print(vals)
        global res
        for rec in self:
            working_time = 0
            if 'stage_id' in vals:
                # find if this stage make close ticket
                stage_closed = rec.env['helpdesk.stage'].search(
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
            if priority_write and project_write and team_write:
                sla_list = rec.env['sla.policy.ansv'].search(
                    [('priority', '=', priority_write), ('project_id', '=', project_write),
                     ('team_id', '=', team_write)
                     ])
                sla_individual_existed = rec.env['individual.ticket.sla'].search(
                    [('ticket_ref', '=', rec.ref)])
                sla_id = []
                sla_exist_name = []
                if sla_list:
                    for sla_exist in sla_individual_existed:
                        sla_exist_name.append(sla_exist.name)
                    for sla in sla_list:
                        if sla.name in sla_exist_name:
                            break
                        else:
                            # print(sla)
                            indi_sla_val = {}
                            indi_sla_val.update({
                                'color': sla.color,
                                'name': sla.name,
                                'project_id': sla.project_id.id,
                                'team_id': sla.team_id.id,
                                'priority': sla.priority,
                                'type_id': sla.type_id.id,
                                'reach_stage': sla.reach_stage.id,
                                'sequence': sla.sequence,
                                'working_time': sla.working_time,
                                'stages_excluded_id': sla.stages_excluded_id.id,
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
                stage_next = rec.env['helpdesk.stage'].search(
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
            stage_update = rec.env['helpdesk.stage'].search(
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
        stage_current = self.env['helpdesk.stage'].search(
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

    # =============================================================================================================
    # Tính remaining day
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

    @api.model
    def test_cron_job(self):
        today = datetime.today().date()
        records = self.env['helpdesk.ticket'].search([])
        for rec in records:
            if rec.deadline and rec.deadline < today:
                next_stage_seq = int(rec.stage_id.sequence) + 1
                stage_change = self.env['helpdesk.stage'].search(
                    [('sequence', '=', next_stage_seq), ])
                rec.write({'stage_id': stage_change.id})
        print("update Cron OK")

    def action_send_mail_card(self, template_id):
        print("sending email")
        # Lấy template email
        # template_id = self.env.ref('mockdesk.ticket_card_mail_templates').id
        template = self.env["mail.template"].browse(template_id)
        template.send_mail(
            self.ids[0],
            force_send=True,
            raise_exception=False
        )
