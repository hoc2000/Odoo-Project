# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager
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

    @http.route('/ticket_webform', type="http", auth="user", website=True)
    def ticketWebform(self, **kw):
        user_partner_id = request.env.user.partner_id
        print("Execution Here.........................")
        # ticket_rec = request.env['mockdesk.ticket'].sudo().search([], limit=1)
        project_rec = request.env['project.ansv'].sudo().search([])
        product_rec = request.env['product.ansv'].sudo().search([])
        # print("Ticket rec...", project_rec)
        return http.request.render('mock_desk.create_ticket', {'country_id': user_partner_id.country_id,
                                                               'project_rec': project_rec,
                                                               'product_rec': product_rec})

    @http.route('/create/webticket', type="http", auth="user", csrf=True, website=True)
    def ticketCreate(self, **kw):
        print('Data Raw......', kw)
        # pid = kw.get('project_id')
        # project_find = request.env['project.ansv'].sudo().search([('id', '=', pid)])
        kw.update({'team_id': False})
        # Create new customer
        customer_name = kw.get('customer_name')
        customer_phone = kw.get('phone')
        customer_mail = kw.get('email')
        customer_country = kw.get('country')
        keys_to_remove = ['customer_name', 'phone', 'email', 'job', 'product', 'country', 'attachment_ids', 'company',
                          'version']

        # Using a loop to remove keys
        for key in keys_to_remove:
            kw.pop(key, None)

        existed_customer = request.env['res.partner'].sudo().search([('name', '=', customer_name)], limit=1, )
        if not existed_customer:
            customer_vals = {'name': customer_name, 'phone': customer_phone, 'email': customer_mail, }

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


class Mockdesk_Product(CustomerPortal):
    # PRODUCT
    @http.route(['/product', '/product/page/<int:page>'], auth="public", type="http", website=True)
    def get_product_list(self, page=1, **kw):
        total_product_rec = request.env['product.ansv'].sudo().search_count([])
        print(total_product_rec)
        page_detail = pager(url='/product',
                            total=total_product_rec,
                            page=page,
                            step=6)
        product_rec = request.env['product.ansv'].sudo().search([], limit=6, offset=page_detail['offset'])

        return http.request.render("mock_desk.product_grid_view_customer",
                                   {'products': product_rec, 'pager': page_detail})

    @http.route(['/product/<int:product_id>'], type="http", auth="public", website=True)
    def get_detail_product(self, product_id, **kw):
        product_val = request.env['product.ansv'].sudo().search([('id', '=', product_id)])
        vals = {'product': product_val}

        return request.render('mock_desk.product_detail_view', vals)

    # PROJECT
    @http.route(['/project', '/project/page/<int:page>'], auth="public", type="http", website=True)
    def get_project_list(self, page=1, **kw):
        total_project_rec = request.env['project.ansv'].sudo().search_count([])
        print(total_project_rec)
        page_detail = pager(url='/project',
                            total=total_project_rec,
                            page=page,
                            step=4)
        project_rec = request.env['project.ansv'].sudo().search([], limit=4, offset=page_detail['offset'])

        return http.request.render("mock_desk.project_media_view",
                                   {'projects': project_rec, 'pager': page_detail})

    @http.route(['/project/<int:project_id>'], type="http", auth="public", website=True)
    def get_detail_project(self, project_id, **kw):
        product_val = request.env['project.ansv'].sudo().search([('id', '=', project_id)])
        product_in_project = request.env['product.ansv'].sudo().search([('project_id', '=', project_id)])
        print(product_in_project)
        vals = {'project': product_val, 'products': product_in_project}

        return request.render('mock_desk.project_detail_view', vals)
