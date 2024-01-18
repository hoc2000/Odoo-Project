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

    @http.route('/', type="http", auth="public", website=True)
    def homepage(self, **kw):
        return http.request.render('mock_desk.new_homepage', {})

    @http.route('/ticket_webform', type="http", auth="public", website=True)
    def ticketWebform(self, **kw):
        print("Execution Here.........................")
        # ticket_rec = request.env['mockdesk.ticket'].sudo().search([], limit=1)
        project_rec = request.env['project.ansv'].sudo().search([])
        product_rec = request.env['product.ansv'].sudo().search([])
        # print("Ticket rec...", project_rec)
        return http.request.render('mock_desk.create_ticket', {'name': '',
                                                               'project_rec': project_rec,
                                                               'product_rec': product_rec})

    @http.route('/create/webticket', type="http", auth="public", csrf=True, website=True)
    def ticketCreate(self, **kw):
        print('Data Raw......', kw)
        # pid = kw.get('project_id')
        # project_find = request.env['project.ansv'].sudo().search([('id', '=', pid)])
        kw.update({'team_id': False})
        # Create new customer
        customer_name = kw.get('customer_name')
        customer_phone = kw.get('phone')
        customer_mail = kw.get('email')
        keys_to_remove = ['customer_name', 'phone', 'email', 'job', 'product']

        # Using a loop to remove keys
        for key in keys_to_remove:
            kw.pop(key, None)

        existed_customer = request.env['res.partner'].sudo().search([('name', '=', customer_name)], limit=1, )
        if not existed_customer:
            customer_vals = {'name': customer_name, 'phone': customer_phone, 'email': customer_mail}
            new_customer = request.env['res.partner'].sudo().create(customer_vals)
            values = {'customer_id': new_customer.id}
        else:
            values = {'customer_id': existed_customer.id, }

        kw.update(values)
        print("Data Received.....", kw)
        request.env['mockdesk.ticket'].sudo().create(kw)

        return request.render("mock_desk.special_thanks", {})

    # @http.route(auth='public', website=True)
    # def index(self, **kw):
    #     return http.request.render('mock_desk.new_homepage', {})

    @http.route(['/product'], auth="public", type="http", website=True)
    def get_product_list(self, **kw):
        product_rec = request.env['product.ansv'].sudo().search([])
        print(product_rec)
        return http.request.render("mock_desk.product_grid_view_customer", {'products': product_rec})
        pass
