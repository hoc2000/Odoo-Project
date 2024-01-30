from odoo import api, fields, models
import datetime


class SolutionForTicket(models.TransientModel):
    _name = "solution.ticket.wizard"
    _description = "Ticket Solution"

    # @api.model
    # def default_get(self, fields_list):
    #     res = super(SolutionForTicket, self).default_get(fields_list)
    #     print("Default get", res)
    #     res['cancel_date'] = datetime.date.today()
    #     return res

    solution = fields.Text(string='Solution')

    def action_cancel(self):
        print("Modal wizard successfully click...........!")
        # Take the cuernet record value change it with the wizard
        self.env['mockdesk.ticket'].browse(self._context.get("active_ids")).update({'solution': self.solution})
        return True
