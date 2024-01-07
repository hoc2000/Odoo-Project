from odoo import models, fields, api


class ResPartnerInherit(models.Model):
    _inherit = 'res.partner'
    _description = 'Inherit res.partner '

    ticket_id = fields.Many2one('mockdesk.ticket', string="Ticket")
    ticket_count = fields.Integer(string="Ticket", compute="get_ticket_helpdesk")

    def open_helpdesk_ticket(self):
        return {
            'name': 'Tickets',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,kanban,form',
            'res_model': 'mockdesk.ticket',
            # 'view_id': self.env.ref("mockdesk.all_ticket_view_kanban").id,
            # self.id <=> active_id
            'domain': [('customer_id', '=', self.id)],
        }

    def get_ticket_helpdesk(self):
        count = self.env['mockdesk.ticket'].search_count([('customer_id', '=', self.id)])
        self.ticket_count = count
