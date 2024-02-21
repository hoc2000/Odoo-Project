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
    _order = 'id desc'

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
    # PROJECT UPDATE
    project_update_id = fields.Many2one('project.update',
                                        help="This is the update status or in progress of the project add by weekly")
    last_update_id = fields.Many2one('project.update',
                                     help="This is the last update state of the project")
    last_update_status = fields.Selection(related="last_update_id.status", store=True, readonly=False)
    last_update_color = fields.Integer(related="last_update_id.color")
    last_update_progress = fields.Integer(related="last_update_id.progress")
    last_update_progress_percentage = fields.Float(related="last_update_id.progress_percentage")
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
    show_cashflow = fields.Boolean(name="CF show", default=False)
    currency_id = fields.Many2one('res.currency', string="Currency", default=get_default_currency)

    # DAC
    dac_info_id = fields.Many2one('ansv.project.cashflow',
                                  string="DAC",
                                  domain="[('project_id', '=', id),('name','ilike','DAC')]"
                                  )
    dac_cash = fields.Monetary(string="Cash DAC", help="This is price of the product exchange to VNĐ",
                               related="dac_info_id.base_cash", store=True,
                               readonly=False)
    dac_contact_date = fields.Date(string="DAC Contact Date", related="dac_info_id.base_contact_date", store=True,
                                   readonly=False)
    dac_target_date = fields.Date(string="DAC Target Date", related="dac_info_id.base_target_date", store=True,
                                  readonly=False)
    dac_reality_date = fields.Date(string="DAC Reality Date", related="dac_info_id.base_reality_date", store=True,
                                   readonly=False)
    dac_duration = fields.Integer(string="Duration", related="dac_info_id.base_duration")
    dac_time_notice = fields.Char(string="Time Notice String", related="dac_info_id.base_time_notice")

    # PAC
    pac_info_id = fields.Many2one('ansv.project.cashflow',
                                  string="PAC",
                                  domain="[('project_id', '=', id),('name','ilike','PAC')]",
                                  )
    pac_cash = fields.Monetary(string="Cash PAC", help="This is price of the product exchange to VNĐ",
                               related="pac_info_id.base_cash", store=True,
                               readonly=False)
    pac_contact_date = fields.Date(string="PAC Contact Date", related="pac_info_id.base_contact_date", store=True,
                                   readonly=False)
    pac_target_date = fields.Date(string="PAC Target Date", related="pac_info_id.base_target_date", store=True,
                                  readonly=False)
    pac_reality_date = fields.Date(string="PAC Reality Date", related="pac_info_id.base_reality_date", store=True,
                                   readonly=False)
    pac_duration = fields.Integer(string="Duration", related="pac_info_id.base_duration")
    pac_time_notice = fields.Char(string="Time Notice String", related="pac_info_id.base_time_notice")

    # FAC
    fac_info_id = fields.Many2one('ansv.project.cashflow',
                                  string="FAC",
                                  domain="[('project_id', '=', id),('name','ilike','FAC')]",
                                  )
    fac_cash = fields.Monetary(string="Cash FAC", help="This is price of the product exchange to VNĐ",
                               related="fac_info_id.base_cash", store=True,
                               readonly=False)
    fac_contact_date = fields.Date(string="FAC Contact Date", related="fac_info_id.base_contact_date", store=True,
                                   readonly=False)
    fac_target_date = fields.Date(string="FAC Target Date", related="fac_info_id.base_target_date", store=True,
                                  readonly=False)
    fac_reality_date = fields.Date(string="FAC Reality Date", related="fac_info_id.base_reality_date", store=True,
                                   readonly=False)
    fac_duration = fields.Integer(string="Duration", related="fac_info_id.base_duration")
    fac_time_notice = fields.Char(string="Time Notice String", related="fac_info_id.base_time_notice")
    summary_target = fields.Monetary(string="Cash Summary", help="This is price of the product exchange to VNĐ")

    # CASH FLOW
    @api.model
    def create(self, vals_list):
        new_project = super(Project, self).create(vals_list)
        project_id = new_project.id
        self.create_cashflow(project_id)
        # add default value
        for name in ['DAC', 'PAC', 'FAC']:
            default_cf = self.env['ansv.project.cashflow'].search(
                [('project_id', '=', new_project.id), ('sequence', '=', '0'), ('name', 'ilike', name)],
                limit=1
            )
            setattr(new_project, f'{name.lower()}_info_id', default_cf)
        return new_project

    def create_cashflow(self, project_id):
        # cf_ansv = self.env['ansv.project.cashflow'].search_count([])
        # if cf_ansv == 0:
        amount_of_cf = self.env['project.cashflow'].search([])
        for cf in amount_of_cf:
            cf_dict = {}
            cf_dict.update({
                'sequence': cf.sequence,
                'name': cf.name,
                'currency_id': cf.currency_id.id,
                'project_id': project_id,
                'base_cash': cf.base_cash,
                'base_contact_date': cf.base_contact_date,
                'base_target_date': cf.base_target_date,
                'base_reality_date': cf.base_reality_date,
            })
            self.env['ansv.project.cashflow'].create(cf_dict)
        for name in ['DAC', 'PAC', 'FAC']:
            default_cf = self.env['ansv.project.cashflow'].search(
                [('project_id', '=', self.id), ('sequence', '=', '0'), ('name', 'ilike', name)],
                limit=1
            )
            setattr(self, f'{name.lower()}_info_id', default_cf)

    def create_cashflow_by_button(self):
        # cf_ansv = self.env['ansv.project.cashflow'].search_count([])
        # if cf_ansv == 0:
        amount_of_cf = self.env['project.cashflow'].search([])
        for cf in amount_of_cf:
            cf_dict = {}
            cf_dict.update({
                'sequence': cf.sequence,
                'name': cf.name,
                'currency_id': cf.currency_id.id,
                'project_id': self.id,
                'base_cash': cf.base_cash,
                'base_contact_date': cf.base_contact_date,
                'base_target_date': cf.base_target_date,
                'base_reality_date': cf.base_reality_date,
            })
            self.env['ansv.project.cashflow'].create(cf_dict)

    # MODAL VIEW TREE OF CASHFLOW
    def dac_modal_tree_view(self):
        for rec in self:
            currProjectId = rec.id
            return {
                'name': 'DAC CashFlow',
                'type': 'ir.actions.act_window',
                'res_model': 'ansv.project.cashflow',  # Replace with the actual model name
                'view_mode': 'tree',
                'view_id': self.env.ref('ansv__project.ansv_project_cashflow_view_tree').id,
                # Replace with the actual tree view ID
                'target': 'new',
                'domain': [('project_id', '=', currProjectId), ('name', 'ilike', 'DAC')],
            }

    def pac_modal_tree_view(self):
        for rec in self:
            currProjectId = rec.id
            return {
                'name': 'PAC CashFlow',
                'type': 'ir.actions.act_window',
                'res_model': 'ansv.project.cashflow',  # Replace with the actual model name
                'view_mode': 'tree',
                'view_id': self.env.ref('ansv__project.ansv_project_cashflow_view_tree').id,
                # Replace with the actual tree view ID
                'target': 'new',
                'domain': [('project_id', '=', currProjectId), ('name', 'ilike', 'PAC')],
            }

    def fac_modal_tree_view(self):
        for rec in self:
            currProjectId = rec.id
            return {
                'name': 'FAC CashFlow',
                'type': 'ir.actions.act_window',
                'res_model': 'ansv.project.cashflow',  # Replace with the actual model name
                'view_mode': 'tree',
                'view_id': self.env.ref('ansv__project.ansv_project_cashflow_view_tree').id,
                # Replace with the actual tree view ID
                'target': 'new',
                'domain': [('project_id', '=', currProjectId), ('name', 'ilike', 'FAC')],
            }

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

    # UPDATE PROJECT ACTION
    def action_view_updates(self):
        for rec in self:
            return {
                'name': f"{rec.project_name}'s Updates",
                'type': 'ir.actions.act_window',
                'view_mode': 'kanban,tree,form',
                'res_model': 'project.update',
                # 'view_id': self.env.ref("mockdesk.all_ticket_view_kanban").id,
                'context': {'default_project_id': rec.id},
                'domain': [('project_id', '=', rec.id)],
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
