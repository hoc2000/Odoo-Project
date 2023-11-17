# -*- coding: utf-8 -*-

from odoo import models, fields, api


class owl(models.Model):
    _name = "owl.todo.list"
    _description = "owl.owl"

    name = fields.Char(string="Task name")
    completed = fields.Boolean()
    color = fields.Char()
