# -*- coding: utf-8 -*-
# from odoo import http


# class OnOdooInheritence(http.Controller):
#     @http.route('/on_odoo_inheritence/on_odoo_inheritence', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/on_odoo_inheritence/on_odoo_inheritence/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('on_odoo_inheritence.listing', {
#             'root': '/on_odoo_inheritence/on_odoo_inheritence',
#             'objects': http.request.env['on_odoo_inheritence.on_odoo_inheritence'].search([]),
#         })

#     @http.route('/on_odoo_inheritence/on_odoo_inheritence/objects/<model("on_odoo_inheritence.on_odoo_inheritence"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('on_odoo_inheritence.object', {
#             'object': obj
#         })
