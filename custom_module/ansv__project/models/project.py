# -*- coding: utf-8 -*-
import random

from odoo import models, fields, api
from random import randint, choice
from datetime import datetime, timedelta

COLOR = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]


class ProjectProperties(models.Model):
    _name = 'project.property'
    _description = 'ProjectProperties'

    name = fields.Text(string='Display name')
    project_properties_definition = fields.PropertiesDefinition('ProjectDefinition')
    ref = fields.Char(string="Reference")

    @api.model
    def create(self, vals):
        if not self.ref and not vals.get('ref'):
            vals['ref'] = self.env['ir.sequence'].next_by_code('project.property.ansv')
        return super(ProjectProperties, self).create(vals)


def get_default_currency(self):
    default_currency = self.env['res.currency'].search([('name', '=', 'VND')])
    return default_currency


class Project(models.Model):
    def random_color(self):
        color = random.choice(COLOR)
        return color

    _sql_constraints = [
        ('project_date_greater', 'check(date_end >= date_start)',
         "The project's start date must be before its end date.")
    ]
    _name = 'project.ansv'
    _inherit = ['mail.thread',
                'mail.activity.mixin', 'portal.mixin']
    _description = 'Project'
    _rec_name = 'project_name'

    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True, )
    stage_id = fields.Many2one('project.stage', string="Stages Project")
    color = fields.Integer(String="Color", default=random_color)
    is_favorite = fields.Boolean(string='Show Project on Dashboard')
    project_name = fields.Char(required=True)
    # Tasks
    priority = fields.Selection([
        ('0', 'Minor'),
        ('1', 'Low'),
        ('2', 'High'),
        ('3', 'Highest'),
        ('4', 'Urgent')], string="Priority")
    label_tasks = fields.Char(string="Name of the tasks", default="Tasks")
    # personal_stage_type_ids = fields.Many2many('project.task.type', 'project_task_user_rel', column1='task_id', column2='stage_id',
    #     ondelete='restrict', group_expand='_read_group_personal_stage_type_ids', copy=False,
    #     domain="[('user_id', '=', user.id)]", depends=['user_ids'], string='Personal Stage')
    partner_ids = fields.Many2one('res.partner', string="Partner")
    department = fields.Many2one('department.partner', string="Department")
    tag_ids = fields.Many2many('project.ansv.tags', string='Tags')
    category_id = fields.Many2one('project.category', string='Category')
    manager_id = fields.Many2one('res.users', string='Project Manager', default=lambda self: self.env.user,
                                 tracking=True)
    team_id = fields.Many2one('project.teams', string='Team', tracking=True)
    member_ids = fields.Many2many('res.users', domain=[('share', '=', False)], related='team_id.member_ids')
    acc_code = fields.Char(string="Accounting Code")
    con_code = fields.Char(string="Contract Code")

    date_start = fields.Date(string="Date start the project")
    date_end = fields.Date(string="Date end the project")
    date = fields.Date(string='Expiration Date', index=True, tracking=True,
                       help="Date on which this project ends. The timeframe defined on the project is taken into account when viewing its planning.")
    # Count amount here
    product_count = fields.Integer(string="Amount of Product", compute="_count_product")
    task_count = fields.Integer(string="Amount of Tasks", compute="_count_tasks")
    ticket_count = fields.Integer(string="Amount of Ticket", compute="_count_ticket")

    completed_tasks = fields.Integer(string="Amount of completed Tasks", compute="_count_completed_task")
    Incompleted_tasks = fields.Integer(string="Amount of incmopleted Tasks", compute="_count_incompleted_task")
    medium_tasks = fields.Integer(compute="_count_medium_task")
    high_tasks = fields.Integer(compute="_count_high_task")
    urgent_tasks = fields.Integer(compute="_count_urgent_task")

    description_project = fields.Text(string="Description")
    product_lines_id = fields.One2many('product.ansv', 'project_id', string="Product")
    # Properties fields
    task_properties_definition = fields.PropertiesDefinition('Task Properties')
    project_properties_definition = fields.PropertiesDefinition('ProjectDefinition')
    project_prop_id = fields.Many2one('project.property', string="Properties Template Value")
    project_properties = fields.Properties('Properties', definition='project_prop_id.project_properties_definition',
                                           copy=True)

    # count
    open_ticket_count = fields.Integer(string="TKO", compute="get_open_ticket")
    unassigned_tickets = fields.Integer(string="UST", compute="get_unassgined_ticket")
    urgent_ticket = fields.Integer(string="urgent ticket", compute="get_urgent_ticket")
    sla_failed = fields.Integer(string="sla failed", compute="get_sla_failed_ticket")

    # CASHFLOW
    currency_id = fields.Many2one('res.currency', string="Currency", default=get_default_currency)

    dac_cash = fields.Monetary(string="Cash DAC", help="This is price of the product exchange to VNĐ")
    dac_contact_date = fields.Date(string="DAC Contact Date")
    dac_target_date = fields.Date(string="DAC Target Date")
    dac_reality_date = fields.Date(string="DAC Reality Date")
    dac_duration = fields.Integer(string="Duration", compute="calculated_time_notice_DAC")
    dac_time_notice = fields.Char(string="Time Notice String", compute="get_dac_time_notice")

    pac_cash = fields.Monetary(string="Cash PAC", help="This is price of the product exchange to VNĐ")
    pac_contact_date = fields.Date(string="PAC Contact Date")
    pac_target_date = fields.Date(string="PAC Target Date")
    pac_reality_date = fields.Date(string="PAC Reality Date")
    pac_duration = fields.Integer(string="Duration", compute="calculated_time_notice_PAC")
    pac_time_notice = fields.Char(string="Time Notice String", compute="get_dac_time_notice")

    fac_cash = fields.Monetary(string="Cash FAC", help="This is price of the product exchange to VNĐ")
    fac_contact_date = fields.Date(string="FAC Contact Date")
    fac_target_date = fields.Date(string="FAC Target Date")
    fac_reality_date = fields.Date(string="FAC Reality Date")
    fac_duration = fields.Integer(string="Duration", compute="calculated_time_notice_FAC")
    fac_time_notice = fields.Char(string="Time Notice String", compute="get_dac_time_notice")

    summary_target = fields.Monetary(string="Cash Summary", help="This is price of the product exchange to VNĐ")

    # CALCULATED CASHFLOW TERM NOTICE
    def calculated_time_notice_DAC(self):
        for rec in self:
            if rec.dac_reality_date:
                duration = rec.dac_target_date - rec.dac_reality_date
                rec.dac_duration = duration.days
            else:
                today = datetime.today().date()
                duration = rec.dac_target_date - today
                rec.dac_duration = duration.days

    def calculated_time_notice_PAC(self):
        for rec in self:
            if rec.dac_reality_date:
                duration = rec.pac_target_date - rec.pac_reality_date
                rec.pac_duration = duration.days
            else:
                today = datetime.today().date()
                duration = rec.pac_target_date - today
                rec.pac_duration = duration.days

    def calculated_time_notice_FAC(self):
        for rec in self:
            if rec.dac_reality_date:
                duration = rec.fac_target_date - rec.fac_reality_date
                rec.fac_duration = duration.days
            else:
                today = datetime.today().date()
                duration = rec.fac_target_date - today
                rec.fac_duration = duration.days

    @api.depends('dac_duration', 'pac_duration', 'fac_duration')
    def get_dac_time_notice(self):
        for rec in self:
            # DAC
            if rec.dac_duration > 0:
                rec.dac_time_notice = f"{abs(rec.dac_duration)} days sooner"
            elif rec.dac_duration < 0:
                rec.dac_time_notice = f"{abs(rec.dac_duration)} days late"
            elif rec.dac_duration == 0:
                rec.dac_time_notice = "On time"
            # PAC
            if rec.pac_duration > 0:
                rec.pac_time_notice = f"{abs(rec.pac_duration)} days sooner"
            elif rec.pac_duration < 0:
                rec.pac_time_notice = f"{abs(rec.pac_duration)} days late"
            elif rec.pac_duration == 0:
                rec.pac_time_notice = "On time"
            # FAC
            if rec.fac_duration > 0:
                rec.fac_time_notice = f"{abs(rec.fac_duration)} days sooner"
            elif rec.fac_duration < 0:
                rec.fac_time_notice = f"{abs(rec.fac_duration)} days late"
            elif rec.fac_duration == 0:
                rec.fac_time_notice = "On time"

    # Count ORM###################
    def _count_product(self):
        for rec in self:
            rec.product_count = self.env['product.ansv'].search_count([('project_id', '=', rec.id)])

    # count DEF
    def _count_tasks(self):
        for rec in self:
            rec.task_count = self.env['task.project.ansv'].search_count([('project_id', '=', rec.id)])

    def _count_ticket(self):
        for rec in self:
            rec.ticket_count = self.env['mockdesk.ticket'].search_count([('project_id', '=', rec.id)])

    def _count_completed_task(self):
        for rec in self:
            rec.completed_tasks = self.env['task.project.ansv'].search_count(
                [('stage_id', 'in', ['Solved', 'Cancelled']), ('project_id', '=', rec.id)])

    def _count_incompleted_task(self):
        for rec in self:
            rec.Incompleted_tasks = self.env['task.project.ansv'].search_count(
                [('stage_id', 'in', ['In Progress', 'New', 'Testing']), ('project_id', '=', rec.id)])

    def _count_medium_task(self):
        for rec in self:
            rec.medium_tasks = self.env['task.project.ansv'].search_count(
                [('priority', '=', '1'), ('project_id', '=', rec.id)])

    def _count_high_task(self):
        for rec in self:
            rec.high_tasks = self.env['task.project.ansv'].search_count(
                [('priority', '=', '2'), ('project_id', '=', rec.id)])

    def _count_urgent_task(self):
        for rec in self:
            rec.urgent_tasks = self.env['task.project.ansv'].search_count(
                [('priority', '=', '3'), ('project_id', '=', rec.id)])

    def get_open_ticket(self):
        for rec in self:
            count_open = rec.env['mockdesk.ticket'].search_count(
                [('project_id', '=', rec.id), ('is_closed', '=', False)])
            rec.open_ticket_count = count_open

    def get_unassgined_ticket(self):
        for rec in self:
            count_unassigned = rec.env['mockdesk.ticket'].search_count(
                [('assign_to', '=', False), ('project_id', '=', rec.id)])
            rec.unassigned_tickets = count_unassigned

    def get_urgent_ticket(self):
        for rec in self:
            count_urgent = rec.env['mockdesk.ticket'].search_count(
                [('priority', '=', '3'), ('project_id', '=', rec.id)])
            rec.urgent_ticket = count_urgent

    def get_sla_failed_ticket(self):
        for rec in self:
            count_sla_failed = rec.env['mockdesk.ticket'].search_count(
                [('is_failed', '=', 'false'), ('project_id', '=', rec.id)])
            rec.sla_failed = count_sla_failed

    # Count ORM###################
    def action_view_tasks(self):
        for rec in self:
            currProjectId = rec.id
            return {
                'name': rec.project_name,
                'type': 'ir.actions.act_window',
                'view_mode': 'kanban,tree,form,calendar',
                'res_model': 'task.project.ansv',
                # 'view_id': self.env.ref("mockdesk.all_ticket_view_kanban").id,
                'domain': [('project_id', '=', currProjectId)],

            }

    def action_view_products(self):
        for rec in self:
            currProjectId = rec.id
            return {
                'name': rec.project_name,
                'type': 'ir.actions.act_window',
                'view_mode': 'kanban,tree,form',
                'res_model': 'product.ansv',
                # 'view_id': self.env.ref("mockdesk.all_ticket_view_kanban").id,
                'domain': [('project_id', '=', currProjectId)],

            }

    def action_view_ticket(self):
        for rec in self:
            currProjectId = rec.id
            return {
                'name': rec.project_name,
                'type': 'ir.actions.act_window',
                'view_mode': 'kanban,tree,form',
                'res_model': 'mockdesk.ticket',
                # 'view_id': self.env.ref("mockdesk.all_ticket_view_kanban").id,
                'context': {'default_project_id': rec.id},
                'domain': [('project_id', '=', currProjectId)],

            }

    # Open Ticket in Mockdesk
    def action_view_open_ticket(self):
        for rec in self:
            currProjectId = rec.id
            return {
                'name': rec.project_name,
                'type': 'ir.actions.act_window',
                'view_mode': 'kanban,tree,form',
                'res_model': 'mockdesk.ticket',
                # 'view_id': self.env.ref("mockdesk.all_ticket_view_kanban").id,
                'context': {'default_project_id': rec.id},
                'domain': [('project_id', '=', currProjectId), ('is_closed', '=', False)],

            }

    def action_view_unassigned_ticket(self):
        for rec in self:
            currProjectId = rec.id
            return {
                'name': rec.project_name,
                'type': 'ir.actions.act_window',
                'view_mode': 'kanban,tree,form',
                'res_model': 'mockdesk.ticket',
                # 'view_id': self.env.ref("mockdesk.all_ticket_view_kanban").id,
                'context': {'default_project_id': rec.id},
                'domain': [('project_id', '=', currProjectId), ('assign_to', '=', False)],

            }

    def action_view_urgent_ticket(self):
        for rec in self:
            currProjectId = rec.id
            return {
                'name': rec.project_name,
                'type': 'ir.actions.act_window',
                'view_mode': 'kanban,tree,form',
                'res_model': 'mockdesk.ticket',
                # 'view_id': self.env.ref("mockdesk.all_ticket_view_kanban").id,
                'context': {'default_project_id': rec.id},
                'domain': [('project_id', '=', currProjectId), ('priority', '=', '3')],

            }

    def action_view_sla_failed(self):
        for rec in self:
            currProjectId = rec.id
            return {
                'name': rec.project_name,
                'type': 'ir.actions.act_window',
                'view_mode': 'kanban,tree,form',
                'res_model': 'mockdesk.ticket',
                # 'view_id': self.env.ref("mockdesk.all_ticket_view_kanban").id,
                'context': {'default_project_id': rec.id},
                'domain': [('project_id', '=', currProjectId), ('is_failed', '=', 'false')],

            }

    @api.onchange('partner_ids')
    def change_department(self):
        for rec in self:
            rec.department = rec.partner_ids.department_id


class ProjectTags(models.Model):
    _name = "project.ansv.tags"
    _description = "Tags in Project"

    # random color get for tag when create
    def _get_default_color(self):
        return randint(1, 11)

    name = fields.Char('Name', required=True, translate=True)
    color = fields.Integer(string='Color', default=_get_default_color,
                           help="Transparent tags are not visible in the kanban view of your projects and tasks.")

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "A tag with the same name already exists."),
    ]


class ProjectCategory(models.Model):
    _name = 'project.category'
    _description = 'ProjectCategory'

    name = fields.Char(string="Project Category")


class ProjectStage(models.Model):
    _name = 'project.stage'
    _description = "Project Stages"
    _rec_name = 'name'
    _order = 'sequence'

    sequence = fields.Integer(string="Sequence")
    name = fields.Char(string="Stages")
    active = fields.Boolean(string="Active", default=True)
    description = fields.Text(string="Descriptions", translate=True)
