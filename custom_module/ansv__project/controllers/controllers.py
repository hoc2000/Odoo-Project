# -*- coding: utf-8 -*-
# from odoo import http


# class AnsvProject(http.Controller):
#     @http.route('/ansv__project/ansv__project', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/ansv__project/ansv__project/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('ansv__project.listing', {
#             'root': '/ansv__project/ansv__project',
#             'objects': http.request.env['ansv__project.ansv__project'].search([]),
#         })

#     @http.route('/ansv__project/ansv__project/objects/<model("ansv__project.ansv__project"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('ansv__project.object', {
#             'object': obj
#         })
