from odoo import api, fields, models
from datetime import datetime


def get_default_currency(self):
    default_currency = self.env['res.currency'].search([('name', '=', 'VND')])
    return default_currency


class ProjectCashflow(models.Model):
    _name = 'project.cashflow'
    _description = 'DAC Project Cashflow'
    _rec_name = 'name'
    _order = 'sequence'

    # CASHFLOW
    sequence = fields.Integer(string="Sequence")
    name = fields.Char(string="Reference")
    currency_id = fields.Many2one('res.currency', string="Currency", default=get_default_currency)

    base_cash = fields.Monetary(string="Cash DAC", help="This is price of the product exchange to VNĐ")
    base_contact_date = fields.Date(string="DAC Contact Date")
    base_target_date = fields.Date(string="DAC Target Date")
    base_reality_date = fields.Date(string="DAC Reality Date")
    base_duration = fields.Integer(string="Duration", compute="_compute_duration")
    base_time_notice = fields.Char(string="Time Notice String", compute="get_dac_time_notice")

    @api.depends('base_target_date', 'base_reality_date')
    def _compute_duration(self):
        for rec in self:
            stages = ['base']

            for stage in stages:
                target_date = rec[f'{stage}_target_date']
                reality_date = rec[f'{stage}_reality_date']
                duration_field = f'{stage}_duration'

                if reality_date and target_date:
                    duration = target_date - reality_date
                    rec[duration_field] = duration.days
                elif target_date:
                    today = datetime.today().date()
                    duration = target_date - today
                    rec[duration_field] = duration.days
                else:
                    rec[duration_field] = False

    @api.depends('base_target_date', 'base_reality_date', 'base_duration')
    def get_dac_time_notice(self):
        for rec in self:
            stages = ['base']

            for stage in stages:
                target_date = rec[f'{stage}_target_date']
                reality_date = rec[f'{stage}_reality_date']
                duration = rec[f'{stage}_duration']
                time_notice_field = f'{stage}_time_notice'

                if not reality_date and not target_date:
                    rec[time_notice_field] = False
                elif reality_date:
                    if duration > 0:
                        rec[time_notice_field] = f"{abs(duration)} days sooner"
                    elif duration < 0:
                        rec[time_notice_field] = f"{abs(duration)} days late"
                    elif duration == 0:
                        rec[time_notice_field] = "On time"
                else:
                    if duration > 0:
                        rec[time_notice_field] = f"{abs(duration)} days remain"
                    elif duration < 0:
                        rec[time_notice_field] = f"{abs(duration)} days overdue"
                    elif duration == 0:
                        rec[time_notice_field] = "Today"


class ProjectCashFlowANSV(models.Model):
    _name = 'ansv.project.cashflow'
    _description = 'DAC Project Cashflow'
    _inherit = ['project.cashflow']

    project_id = fields.Many2one('project.ansv', string="Project")
