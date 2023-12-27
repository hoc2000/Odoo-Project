# -*- coding: utf-8 -*-
import random

from odoo import models, fields, api
from random import randint, choice

COLOR = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]


class Project(models.Model):
    def random_color(self):
        color = random.choice(COLOR)
        return color

    _name = 'project.ansv'
    _inherit = ['mail.thread',
                'mail.activity.mixin', 'portal.mixin']
    _description = 'Project'
    _rec_name = 'project_name'

    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True, )
    color = fields.Integer(String="Color", default=random_color)
    is_favorite = fields.Boolean(string='Show Project on Dashboard')
    project_name = fields.Char(required=True)
    # Tasks
    label_tasks = fields.Char(string="Name of the tasks", default="Tasks")
    # personal_stage_type_ids = fields.Many2many('project.task.type', 'project_task_user_rel', column1='task_id', column2='stage_id',
    #     ondelete='restrict', group_expand='_read_group_personal_stage_type_ids', copy=False,
    #     domain="[('user_id', '=', user.id)]", depends=['user_ids'], string='Personal Stage')
    partner_ids = fields.Many2one('res.partner', string="Customer")
    tag_ids = fields.Many2many('project.ansv.tags', string='Tags')
    manager_id = fields.Many2one('res.users', string='Project Manager', default=lambda self: self.env.user,
                                 tracking=True)
    date_start = fields.Date(string="Date start the project")
    date_end = fields.Date(string="Date end the project")
    date = fields.Date(string='Expiration Date', index=True, tracking=True,
        help="Date on which this project ends. The timeframe defined on the project is taken into account when viewing its planning.")
    # Count amount here
    product_count = fields.Integer(string="Amount of Product", compute="_count_product")
    task_count = fields.Integer(string="Amount of Tasks", compute="_count_tasks")
    completed_tasks = fields.Integer(string="Amount of completed Tasks", compute="_count_completed_task")
    Incompleted_tasks = fields.Integer(string="Amount of incmopleted Tasks", compute="_count_incompleted_task")
    medium_tasks = fields.Integer(compute="_count_medium_task")
    high_tasks = fields.Integer(compute="_count_high_task")
    urgent_tasks = fields.Integer(compute="_count_urgent_task")

    description_project = fields.Html()
    product_lines_id = fields.One2many('product.ansv', 'project_id', string="Product")
    # Properties fields
    task_properties_definition = fields.PropertiesDefinition('Task Properties')

    _sql_constraints = [
        ('project_date_greater', 'check(date_end >= date_start)',
         "The project's start date must be before its end date.")
    ]

    def _count_product(self):
        for rec in self:
            rec.product_count = self.env['product.ansv'].search_count([('project_id', '=', rec.id)])

    # count DEF
    def _count_tasks(self):
        for rec in self:
            rec.task_count = self.env['task.project.ansv'].search_count([('project_id', '=', rec.id)])

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
