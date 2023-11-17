from odoo import models, fields, api
from datetime import datetime, timedelta


# Lấy default value của ticket
def get_default_stage(self):
    default_stage = self.env['helpdesk.stage'].search([('sequence', '=', '0')], limit=1)
    return default_stage


# Khai báo trường thông tin của model Ticket và các xử lý cơ bản trong đó
class HelpDeskTicket(models.Model):
    _name = 'helpdesk.ticket'
    _inherit = ['mail.thread',
                'mail.activity.mixin',
                'project.ansv', ]

    _description = 'Ticket of MockDesk'
    _rec_name = 'name'

    active = fields.Boolean(string="Active", default=True)
    name = fields.Char(string="Ticket Name", required=True)
    team_id = fields.Many2one('helpdesk.teams', String='Team', required=True)
    priority = fields.Selection([
        ('0', 'No Rate'),
        ('1', 'Minor'),
        ('2', 'Major'),
        ('3', 'Critical')], string="Priority")

    phone = fields.Char(string="Phone", related='customer_id.phone')
    stage_id = fields.Many2one('helpdesk.stage', string="Stage", default=get_default_stage, tracking=True)
    stage_current_string = fields.Char(string="Stage Right Now")
    email = fields.Char(String="Email", related='customer_id.email')
    assign_to = fields.Many2one('res.users', string="Assign To")
    deadline = fields.Datetime(String="Deadline", compute="_compute_deadline")
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
    product_ticket_id = fields.Many2one('product.in.project', string="Product",
                                        domain="[('project_product_id', '=', project_id)]")
    ticket_components_list_id = fields.One2many(related="product_ticket_id.product_id.components_list_id",
                                                string='Component', readonly=False)
    sla_deadline = fields.Many2many('sla.policy.ansv', string="SLA Deadline", readonly=True)
    # Tổng thời gian hiện tại của SLA đơn
    working_time_total = fields.Float(string="Working Time", digit=(12, 1))
    # Các trường được inherit từ model project
    @api.onchange('project_id')
    def _detail_project(self):
        for rec in self:
            rec.project_name = rec.project_id.project_name
            rec.description_project = rec.project_id.description_project
            rec.value = rec.project_id.value
            rec.value2 = rec.project_id.value2

    @api.onchange('stage_id')
    def update_stage_(self):
        for rec in self:
            rec.stage_current_string = rec.stage_id.name

    def action_test(self):
        print("Button clicked!!!")
        return {
            'effect': {
                'fadeout': 'fast',
                'message': 'Click Successful',
                'type': 'rainbow_man',
            }
        }

    # Button Chagne the Stage
    def action_in_progress(self):
        for rec in self:
            inprogress_stage = rec.env['helpdesk.stage'].search([('name', '=', 'In Progress')], limit=1)
            print(inprogress_stage)
            rec.stage_id = inprogress_stage
            rec.stage_current_string = rec.stage_id.name

    def action_done(self):
        for rec in self:
            solved_stage = rec.env['helpdesk.stage'].search([('name', '=', 'Solved')], limit=1)
            print(solved_stage)
            rec.stage_id = solved_stage
            rec.stage_current_string = rec.stage_id.name
        return {
            'effect': {
                'fadeout': 'fast',
                'message': 'Ticket Solved',
                'type': 'rainbow_man',
            }
        }

    def action_cancel(self):
        for rec in self:
            cancel_stage = rec.env['helpdesk.stage'].search([('name', '=', 'Cancelled')], limit=1)
            print(cancel_stage)
            rec.stage_id = cancel_stage
            rec.stage_current_string = rec.stage_id.name

    # =====================================================================================================================
    # Khởi tạo SLA
    @api.model
    def create(self, vals):
        print(vals)
        # Tìm các SLA thỏa mãn
        # if vals['team_id'] == vals['priority'] == vals['type'] == False:
        sla_list = self.env['sla.policy.ansv'].search(
            [('team_id', '=', vals['team_id']), ('priority', '=', vals['priority']), ('type_id', '=', vals['type']),
             ])
        # Lấy stage mới tạo default ó nó sẽ là 'NEW'
        working_time = 0
        if sla_list:
            next_stage = int(self.stage_id.sequence) + 1
            sla_reach = self.env['sla.policy.ansv'].search(
                [('reach_stage.sequence', '=', next_stage)])
            print(sla_reach)
            working_time = sla_reach.working_time
        sla_id = []
        for sla in sla_list:
            sla_id.append(sla.id)
        # Thêm vào vals của hàm write
        sla_value = [(6, 0, sla_id)]
        # print(sla_value)
        vals.update({'sla_deadline': sla_value, 'working_time_total': working_time})
        return super(HelpDeskTicket, self).create(vals)

    # WRITE Cập nhật SLA
    def write(self, vals):
        for rec in self:
            working_time = 0
            if 'stage_id' in vals:
                # truyền id của thằng stage mói chuyển vào
                rec.change_state_sla(vals['stage_id'], rec.sla_deadline)
                working_time = rec.get_working_time(vals['stage_id'], rec.sla_deadline)
            # Giá trị mặc định nếu nó đã tồn tại
            priority_write = rec.priority
            team_id_write = rec.team_id.id
            type_write = rec.type.id
            # Nếu nó thay đổi thì gán giá trị thay đổi vào trong
            if 'priority' in vals:
                priority_write = vals['priority']
            if 'team_id' in vals:
                team_id_write = vals['team_id']
            if 'type' in vals:
                type_write = vals['type']
            # Tìm kiếm giá trị của sla
            if priority_write and team_id_write and type_write:
                sla_list = rec.env['sla.policy.ansv'].search(
                    [('team_id', '=', team_id_write), ('priority', '=', priority_write), ('type_id', '=', type_write),
                     ])
                sla_id = []
                if sla_list:
                    for sla in sla_list:
                        sla_id.append(sla.id)
                    if 'stage_id' not in vals :
                        next_stage = int(rec.stage_id.sequence) + 1
                        sla_reach = rec.env['sla.policy.ansv'].search(
                            [('reach_stage.sequence', '=', next_stage), ('id', 'in', sla_id)])
                        working_time = sla_reach.working_time
                        print(working_time)
                # Thêm vào vals của hàm write
                sla_value = [(6, 0, sla_id)]
                # print(sla_value)
                vals.update({'sla_deadline': sla_value, 'working_time_total': working_time})
        return super(HelpDeskTicket, self).write(vals)

    # data-color="1" title="Red # data-color="2" title="Orange"  # data-color="3" title="Yellow"  # data-color="4"
    # title="Light blue" # data-color="5" title="Dark purple"# data-color="6" title="Salmon pink" # data-color="7"
    # title="Medium blue" # data-color="8" title="Dark blue"# data-color="9" title="Fushia" # data-color="10"
    # title="Green" # data-color="11" title="Purple
    def change_state_sla(self, stage_id, sla_list):
        # Tim stage dang o hien tai # Default
        for rec in self:
            stage_current = rec.env['helpdesk.stage'].search(
                [('id', '=', stage_id)])
            for sla in sla_list:
                if stage_current.sequence < sla.reach_stage.sequence:
                    next_stage = int(stage_current.sequence) + 1
                    # xét trong các sla mà ticket sở hữu
                    if sla.reach_stage.sequence == next_stage:
                        print('sla cần đạt được:' + sla.name)
                        rec.working_time_total = sla.working_time
                    sla.color = 0
                elif sla.reach_stage == stage_current:
                    sla.color = 10
                    rec.working_time_total = 0
                elif sla.reach_stage.sequence <= stage_current.sequence:
                    sla.color = 10
                    rec.working_time_total = 0

    def get_working_time(self, stage_id, sla_list):
        timework = 0
        stage_current = self.env['helpdesk.stage'].search(
            [('id', '=', stage_id)])
        for sla in sla_list:
            if stage_current.sequence < sla.reach_stage.sequence:
                next_stage = int(stage_current.sequence) + 1
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
            if not rec.deadline:
                today = datetime.now().date()
                timework = rec.working_time_total
                day_of_work = round(timework / 8)
                delta = timedelta(days=day_of_work)
                new_deadline = today + delta
            rec.deadline = new_deadline
