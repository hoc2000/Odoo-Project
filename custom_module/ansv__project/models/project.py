# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Project(models.Model):
    _name = 'project.ansv'
    _description = 'ansv__project.ansv__project'
    _rec_name = 'project_name'

    project_name = fields.Char()
    value = fields.Float()
    value2 = fields.Float(compute="_value_pc", store=True)
    color = fields.Integer(String="Color")
    description_project = fields.Html()
    product_lines_id = fields.One2many('product.in.project', 'project_product_id', string="Product")

    @api.depends('value')
    def _value_pc(self):
        for record in self:
            record.value2 = float(record.value) / 100


class ProductinProject(models.Model):
    _name = 'product.in.project'
    _description = "Product In Project"
    _rec_name = "product_id"

    product_id = fields.Many2one('product.ansv', string="Name Product")
    # Cho phần kết nối với One2Many
    project_product_id = fields.Many2one('project.ansv', string="Project")
    quantity = fields.Integer(string="Quantity")
