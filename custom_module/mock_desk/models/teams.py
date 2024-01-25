from odoo import api, fields, models
import json
from odoo.release import version


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
    # count ticket
    ticket_new = fields.Integer(string="New Ticket", compute="count_new_ticket")
    ticket_inprogress = fields.Integer(string="In Progress Ticket", compute="count_inprogress_ticket")
    solved_ticket = fields.Integer(string="Solved Ticket", compute="count_solved_ticket")
    cancelled_ticket = fields.Integer(string="Cancelled Ticket", compute="count_cancelled_ticket")
    graph_data = fields.Text(compute="_compute_dashboard_graph")

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

    # Ticket Count
    def count_new_ticket(self):
        for rec in self:
            count = rec.env['mockdesk.ticket'].search_count([('team_id', '=', rec.id), ('stage_id.name', '=', 'New')])
            rec.ticket_new = count

    def count_inprogress_ticket(self):
        for rec in self:
            count = rec.env['mockdesk.ticket'].search_count(
                [('team_id', '=', rec.id), ('stage_id.name', '=', 'In Progress')])
            rec.ticket_inprogress = count

    def count_solved_ticket(self):
        for rec in self:
            count = rec.env['mockdesk.ticket'].search_count(
                [('team_id', '=', rec.id), ('stage_id.name', '=', 'Solved')])
            rec.solved_ticket = count

    def count_cancelled_ticket(self):
        for rec in self:
            count = rec.env['mockdesk.ticket'].search_count(
                [('team_id', '=', rec.id), ('stage_id.name', '=', 'Cancelled')])
            rec.cancelled_ticket = count

    # VIEW TYPE OBJECT
    def action_open_ratings(self):
        pass

    def action_open_mockdesk_ticket(self):
        pass

    def _compute_dashboard_graph(self):
        for team in self:
            team.graph_data = json.dumps(team._get_dashboard_graph_data())

    def _get_dashboard_graph_data(self):
        values = []
        today = fields.Date.from_string(fields.Date.context_today(self))
        x_field = 'label'
        y_field = 'value'
        short_name = ['Open', 'Unassigned', 'Critical', 'Failed']
        for i in range(4):
            values.append({x_field: short_name[i], y_field: 0, 'type': 'ticket'})

        data_in_team = [self.open_ticket_count, self.unassigned_tickets, self.urgent_ticket, self.sla_failed]
        for data_item in range(4):
            values[data_item][y_field] = data_in_team[data_item]

        color = '#875A7B' if '+e' in version else '#7c7bad'

        # If no actual data available, show some sample data
        # if not graph_data:
        #     graph_key = _('Sample data')
        #     for value in values:
        #         value['type'] = 'o_sample_data'
        #         # we use unrealistic values for the sample data
        #         value['value'] = random.randint(0, 20)
        return [{'values': values, 'area': True, 'title': 'Team View', 'key': 'ticket', 'color': color}]
