from odoo import models, fields, api
from odoo.exceptions import ValidationError
import re


def get_default_currency(self):
    default_currency = self.env['res.currency'].search([('name', '=', 'VND')])
    return default_currency


class Product(models.Model):
    _name = 'product.ansv'
    _description = 'Profuct of Project'
    _rec_name = 'product_name'

    # Cho phần kết nối với One2Many
    product_id = fields.Many2one('product.ansv','Existed Product')
    project_id = fields.Many2one('project.ansv', string="Project")
    product_name = fields.Char(help="This is the title of the product")
    detail_type = fields.Selection([('consumable', 'Consumable'),
                                    ('service', 'Service')], string="Product type", required=True)
    currency_id = fields.Many2one('res.currency', string="Currency", default=get_default_currency)
    price = fields.Monetary(string="Price", help="This is price of the product exchange to VNĐ")
    product_ref = fields.Char(string="Product Reference")
    category_id = fields.Many2one('category.product',string="Category", required=True)

    image = fields.Image(string="image")
    is_favorite = fields.Boolean(string='Show Product Favourite')

    components_list_id = fields.One2many('component.product.ansv', 'product_id', string="Components")
    count_component = fields.Integer(help="This is count the component in product", compute="_count_component")
    quantity = fields.Integer(string="Quantity")

    def _count_component(self):
        for rec in self:
            number_of_component = self.env['component.product.ansv'].search_count([('product_id', '=', rec.id)])
            rec.count_component = number_of_component

    def write(self, vals):
        for rec in self:
            if not rec.currency_id:
                vnd_cur = rec.env['res.currency'].search([('name', '=', 'VND')])
                vals.update({'currency_id': vnd_cur})
        return super(Product, self).write(vals)


class Components(models.Model):
    _name = 'component.product.ansv'
    _description = 'component of Project'
    _rec_name = 'name'

    name = fields.Char(string="Component Name")
    version_id = fields.Many2one('component.version', string="Version")
    product_id = fields.Many2one('product.ansv', string='Product', ondelete="cascade")
    is_error = fields.Boolean(string="Is Error")
    _description_error = fields.Text(string="Error reason")

    @api.onchange('is_error')
    def _check_error(self):
        if not self.is_error:
            self._description_error = ''
            self.name = self.name.replace("[error]", "")
        else:
            self.name = self.name + "[error]"


class Version(models.Model):
    _name = 'component.version'
    _description = 'version of components'
    _rec_name = 'version_number'

    version_number = fields.Char(string='Version Number')

    @api.constrains('version_number')
    def _check_version_format(self):
        for record in self:
            if record.version_number:
                # Define the pattern using a regex
                pattern = r'^\d+\.\d+\.\d+$'

                # Check if the entered value matches the pattern
                if not re.match(pattern, record.version_number):
                    raise ValidationError("Version number should be in format '0.0.0'")


class Category(models.Model):
    _name = 'category.product'
    _description = 'Category of product'
    _rec_name = 'name'

    name = fields.Char(string="Name", required=True)
