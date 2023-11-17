from odoo import models, fields, api
from odoo.exceptions import ValidationError
import re


class Product(models.Model):
    _name = 'product.ansv'
    _description = 'Profuct of Project'
    _rec_name = 'product_name'

    product_name = fields.Char()
    components_list_id = fields.One2many('component.product.ansv', 'product_id', string="Components")

    # default su dung api.model
    # @api.model
    # def default_get(self, fields_list):
    #     res = super(Product, self).default_get(fields_list)
    #     components_list = []
    #     # Lấy dữ liệu record từ Component
    #     # điêều kiện search nếu thêm '|'ở đằng trước thì sẽ là or còn nếu khng c thì sẽ là and
    #     com_rec = self.env['component.product.ansv'].search(
    #         [('product_id', '=', False)])
    #     for com in com_rec:
    #         # Gán theo fields của component với product
    #         line = (0, 0, {
    #             'name': com.name, 'version': com.version
    #         })
    #         components_list.append(line)
    #     # update giá trị default trong record
    #     res.update({
    #         'components_list_id': components_list,
    #         'product_name': 'VD Về Sản Phẩm'
    #     })
    #     return res


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
