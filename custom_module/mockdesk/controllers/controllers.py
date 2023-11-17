# -*- coding: utf-8 -*-
from odoo import http


class Mockdesk(http.Controller):
    @http.route('/mockdesk/tickets', auth='user', type="json")
    def team_ticket_banner(self, **kw):
        return {
            'html': """
            <div>
                <center>
                <h1>TU HOC VU TEST</h1>
                </center>            
            </div>
            """
        }

#     @http.route('/mockdesk/mockdesk/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('mockdesk.listing', {
#             'root': '/mockdesk/mockdesk',
#             'objects': http.request.env['mockdesk.mockdesk'].search([]),
#         })

#     @http.route('/mockdesk/mockdesk/objects/<model("mockdesk.mockdesk"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('mockdesk.object', {
#             'object': obj
#         })
