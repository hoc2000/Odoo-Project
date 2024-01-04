# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from odoo.addons.website.controllers.main import Website


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

    @http.route('/ticket_webform', type="http", auth="public", website=True)
    def patient_webform(self, **kw):
        print("Execution Here.........................")
        ticket_rec = request.env['helpdesk.ticket'].sudo().search([], limit=1)
        project_rec = request.env['project.ansv'].sudo().search([])
        print("Ticket rec...", project_rec)
        return http.request.render('mockdesk.create_ticket', {'name': 'Ticket Customer test',
                                                              'project_rec': project_rec})

    @http.route('/create/webticket', type="http", auth="public", csrf=True, website=True)
    def create_webpatient(self, **kw):
        pid = kw.get('project_id')
        project_find = request.env['project.ansv'].sudo().search([('id', '=', pid)])

        # Create new customer
        customer_name = kw.get('customer_name')
        customer_phone = kw.get('phone')
        customer_mail = kw.get('email')
        keys_to_remove = ['customer_name', 'phone', 'email']

        # Using a loop to remove keys
        for key in keys_to_remove:
            kw.pop(key, None)

        existed_customer = request.env['res.partner'].sudo().search([('name', '=', customer_name)], limit=1, )
        if not existed_customer:
            customer_vals = {'name': customer_name, 'phone': customer_phone, 'email': customer_mail}
            new_customer = request.env['res.partner'].sudo().create(customer_vals)
            project_val = {'project_name': project_find.project_name, 'customer_id': new_customer.id}
        else:
            project_val = {'project_name': project_find.project_name, 'customer_id': existed_customer.id}

        kw.update(project_val)
        print("Data Received.....", kw)
        request.env['helpdesk.ticket'].sudo().create(kw)

        return request.render("mockdesk.special_thanks", {})

    @http.route(auth='public', website=True)
    def index(self, **kw):
        return http.request.render('mockdesk.new_homepage',{})
