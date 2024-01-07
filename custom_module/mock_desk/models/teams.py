from odoo import api, fields, models


class HelpTeams(models.Model):
    _name = 'mockdesk.teams'
    _description = 'this is teams of mockdesk'

    active = fields.Boolean(default=True)
    sequence = fields.Integer(string="Sequence")
    name = fields.Char(string="Team Name")
    # phone = fields.Char(string="Phone")
    description = fields.Text(string="Description", help="This help you inform about the team , and it's purpose")
    color = fields.Integer(string="Color")
    auto_assignment = fields.Boolean(string="Auto Assignment")
    member_ids = fields.Many2many('res.users', domain=[('share', '=', False)], string="Team member")

    # count
    open_ticket_count = fields.Integer(string="TKO", compute="get_open_ticket")
    unassigned_tickets = fields.Integer(string="UST", compute="get_unassgined_ticket")
    urgent_ticket = fields.Integer(string="urgent ticket", compute="get_urgent_ticket")
    sla_failed = fields.Integer(string="sla failed", compute="get_sla_failed_ticket")
    closed_ticket = fields.Integer(string="closed ticket", compute="get_closed_ticket")
    success_rated = fields.Float(string="Success Rate",
                                 help="calculated the percent rate of ticket closed that success sla on time."
                                      "(Total number ticket closed success SLA on time) / (total number closed ticket)",
                                 compute="cal_success_rate_ticket")

    average_rating = fields.Float(string="Average rating",
                                  help="average sum up point of rating percent to max point rating = 5",
                                  compute="cal_average_rating")
    average_rating_text = fields.Char(compute="text_base_on_rating")

    @api.depends('average_rating')
    def text_base_on_rating(self):
        for record in self:
            if record.average_rating >= 0.7:
                record.average_rating_text = "Satisfation"
            if 0.3 <= record.average_rating <= 0.7:
                record.average_rating_text = "Okay"
            if record.average_rating <= 0.3:
                record.average_rating_text = "Dissatisfied"

    def action_view_ticket(self):
        for rec in self:
            currTeam = rec.name
            print(currTeam)
            return {
                'name': currTeam,
                'type': 'ir.actions.act_window',
                'view_mode': 'kanban,tree,form',
                'res_model': 'mockdesk.ticket',
                # 'view_id': self.env.ref("mockdesk.all_ticket_view_kanban").id,
                'domain': [('team_id', '=', currTeam)],

            }

    # Các giá trị đếm
    def get_open_ticket(self):
        for rec in self:
            count_open = rec.env['mockdesk.ticket'].search_count(
                [('team_id', '=', rec.id), ('is_closed', '=', False)])
            rec.open_ticket_count = count_open

    def get_unassgined_ticket(self):
        for rec in self:
            count_unassigned = rec.env['mockdesk.ticket'].search_count(
                [('assign_to', '=', False), ('team_id', '=', rec.id)])
            rec.unassigned_tickets = count_unassigned

    def get_urgent_ticket(self):
        for rec in self:
            count_urgent = rec.env['mockdesk.ticket'].search_count(
                [('priority', '=', '3'), ('team_id', '=', rec.id)])
            rec.urgent_ticket = count_urgent

    def get_sla_failed_ticket(self):
        for rec in self:
            count_sla_failed = rec.env['mockdesk.ticket'].search_count(
                [('is_failed', '=', 'false'), ('team_id', '=', rec.id)])
            rec.sla_failed = count_sla_failed

    def get_closed_ticket(self):
        for rec in self:
            count_closed_ticket = rec.env['mockdesk.ticket'].search_count(
                [('is_closed', '=', True), ('team_id', '=', rec.id)])
            rec.closed_ticket = count_closed_ticket

    def cal_success_rate_ticket(self):
        for rec in self:
            closed_ticket = rec.env['mockdesk.ticket'].search_count(
                [('is_closed', '=', 'true'), ('team_id', '=', rec.id)])
            closed_ticket_success = rec.env['mockdesk.ticket'].search_count(
                [('is_closed', '=', 'true'), ('is_failed', '!=', 'true'), ('team_id', '=', rec.id)])
            if closed_ticket and closed_ticket_success:
                rate_number = closed_ticket_success / closed_ticket
                rec.success_rated = rate_number
            else:
                rec.success_rated = 0

    def cal_average_rating(self):
        for rec in self:
            try:
                rated_ticket = rec.env['mockdesk.ticket'].search(
                    [('rating_count', '!=', 0), ('team_id', '=', rec.id)])
                total_ticket = rec.env['mockdesk.ticket'].search_count(
                    [('rating_count', '!=', 0), ('team_id', '=', rec.id)])
                summary = 0
                # print(type(rated_ticket))
                if rated_ticket:
                    for ticket in rated_ticket:
                        summary = summary + ticket.rating_avg
                    rate_percent = (summary / total_ticket) / 5.00
                    rec.average_rating = rate_percent
                else:
                    rec.average_rating = 0
            except Exception as e:
                print(e)

    # VIEW TYPE OBJECT
    def action_open_ratings(self):
        pass

    def action_open_mockdesk_ticket(self):
        pass
