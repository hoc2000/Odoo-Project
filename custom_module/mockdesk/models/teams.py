from odoo import api, fields, models


class HelpTeams(models.Model):
    _name = 'helpdesk.teams'
    _description = 'this is teams of mockdesk'

    sequence = fields.Integer(string="Sequence")
    name = fields.Char(string="Team Name")
    phone = fields.Char(string="Phone")
    color = fields.Integer(string="Color")
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

    def action_view_ticket(self):
        for rec in self:
            currTeam = rec.name
            print(currTeam)
            return {
                'name': currTeam,
                'type': 'ir.actions.act_window',
                'view_mode': 'kanban,tree,form',
                'res_model': 'helpdesk.ticket',
                # 'view_id': self.env.ref("mockdesk.all_ticket_view_kanban").id,
                'domain': [('team_id', '=', currTeam)],

            }

    # def print_name(self):
    #     print(self.customer_id)
    # Các giá trị đếm
    def get_open_ticket(self):
        for rec in self:
            count_open = rec.env['helpdesk.ticket'].search_count(
                [('team_id', '=', rec.id), ('stage_id.name', '!=', 'Closed')])
            rec.open_ticket_count = count_open

    def get_unassgined_ticket(self):
        for rec in self:
            count_unassigned = rec.env['helpdesk.ticket'].search_count(
                [('assign_to', '=', False), ('team_id', '=', rec.id)])
            rec.unassigned_tickets = count_unassigned

    def get_urgent_ticket(self):
        for rec in self:
            count_urgent = rec.env['helpdesk.ticket'].search_count(
                [('priority', '=', '3'), ('team_id', '=', rec.id)])
            rec.urgent_ticket = count_urgent

    def get_sla_failed_ticket(self):
        for rec in self:
            count_sla_failed = rec.env['helpdesk.ticket'].search_count(
                [('is_failed', '=', 'false'), ('team_id', '=', rec.id)])
            rec.sla_failed = count_sla_failed

    def get_closed_ticket(self):
        for rec in self:
            count_closed_ticket = rec.env['helpdesk.ticket'].search_count(
                [('is_closed', '=', True), ('team_id', '=', rec.id)])
            rec.closed_ticket = count_closed_ticket

    def cal_success_rate_ticket(self):
        for rec in self:
            closed_ticket = rec.env['helpdesk.ticket'].search_count(
                [('is_closed', '=', 'true'), ('team_id', '=', rec.id)])
            closed_ticket_success = rec.env['helpdesk.ticket'].search_count(
                [('is_closed', '=', 'true'), ('is_failed', '=', 'false'), ('team_id', '=', rec.id)])
            if closed_ticket and closed_ticket_success:
                rate_number = closed_ticket_success / closed_ticket
                rec.success_rated = rate_number * 100
            else:
                rec.success_rated = 0

    def cal_average_rating(self):
        for rec in self:
            try:
                rated_ticket = rec.env['helpdesk.ticket'].search(
                    [('rating_count', '!=', 0), ('team_id', '=', rec.id)])
                total_ticket = rec.env['helpdesk.ticket'].search_count(
                    [('rating_count', '!=', 0), ('team_id', '=', rec.id)])
                summary = 0
                # print(type(rated_ticket))
                if rated_ticket:
                    for ticket in rated_ticket:
                        summary = summary + ticket.rating_avg
                    rate_percent = (summary / total_ticket) / 5.00
                    rec.average_rating = rate_percent * 100
                else:
                    rec.average_rating = 0
            except Exception as e:
                print(e)
