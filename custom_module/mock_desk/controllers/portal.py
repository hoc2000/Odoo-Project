# -*- coding: utf-8 -*-

from odoo.addons.portal.controllers.portal import CustomerPortal, pager
from odoo.http import request
from odoo import http
from datetime import datetime


class PortalAccount(CustomerPortal):
    def _prepare_home_portal_values(self, counters):
        current_user = request.env.user.id
        user_partner_id = request.env.user.partner_id.id

        values = super(PortalAccount, self)._prepare_home_portal_values(counters)
        # print(user_partner_id)
        values['ticket_count'] = request.env['mockdesk.ticket'].sudo().search_count(
            ['|', ('create_uid', '=', current_user), ('customer_id', '=', user_partner_id)])
        return values

    @http.route(['/my/ticket', '/my/ticket/page/<int:page>'], type="http", website=True)
    def ticket_list_view(self, page=1, sortby='ref', search="", search_in="All", **kw):
        current_user = request.env.user.id
        user_partner_id = request.env.user.partner_id.id
        # based on which fields search
        # what search user is searching -> search value
        # Sort by features
        sorted_list = {
            'ref': {'label': 'Reference', 'order': 'ref'},
            'create_date': {'label': 'Date Created', 'order': 'create_date desc'},
        }

        search_list = {
            'All': {'label': 'All', 'input': 'All', 'domain': (1, '=', 1)},
            'Name': {'label': 'Ticket Name', 'input': 'Name', 'domain': ('name', 'ilike', search)},
            'Ref': {'label': 'Ticket Reference', 'input': 'Ref', 'domain': ('ref', 'ilike', search)},
        }

        search_domain = search_list[search_in]['domain']
        default_order_by = sorted_list[sortby]['order']

        ticket_obj = request.env['mockdesk.ticket']
        # Pagination
        total_ticket = ticket_obj.search_count(
            ['&', search_domain, '|', ('create_uid', '=', current_user), ('customer_id', '=', user_partner_id)])
        print("Total ticket get...", total_ticket)
        page_detail = pager(url='/my/ticket',
                            total=total_ticket,
                            page=page,
                            url_args={'sortby': sortby, 'search_in': search_in, 'search': search},
                            step=15)

        tickets = ticket_obj.search(
            ['&', search_domain, '|', ('create_uid', '=', current_user), ('customer_id', '=', user_partner_id)],
            limit=15, offset=page_detail['offset'], order=default_order_by)
        # for ticket in tickets:
        #     formatted_create_date = datetime.strptime(ticket.create_date, "%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y")
        #     print(formatted_create_date)

        vals = {'tickets': tickets,
                'page_name': 'ticket_list',
                'pager': page_detail,
                'sortby': sortby,
                'searchbar_sortings': sorted_list,
                'search_in': search_in,
                'searchbar_inputs': search_list,
                'search': search}
        return request.render('mock_desk.portal_ticket_list_view_customer', vals)

    # Hiện thị record theo ID
    # Record hiển thị có thể chuyển giao Pagination được
    @http.route(['/my/ticket/<int:ticket_id>'], type="http", auth="public", website=True)
    def ticketDetailView(self, ticket_id, **kw):
        current_user = request.env.user.id
        user_partner_id = request.env.user.partner_id.id

        ticket_val = request.env['mockdesk.ticket'].sudo().search([('id', '=', ticket_id)])
        vals = {'ticket': ticket_val, 'page_name': 'ticket_detail_view'}
        ticket_records = request.env['mockdesk.ticket'].search(
            ['|', ('create_uid', '=', current_user), ('customer_id', '=', user_partner_id)])
        ticket_ids = ticket_records.ids
        ticket_index = ticket_ids.index(ticket_val.id)

        if ticket_index != 0 and ticket_ids[ticket_index - 1]:
            vals['prev_record'] = '/my/ticket/{}'.format(ticket_ids[ticket_index - 1])
        if ticket_index < len(ticket_ids) - 1 and ticket_ids[ticket_index + 1]:
            vals['next_record'] = '/my/ticket/{}'.format(ticket_ids[ticket_index + 1])
        return request.render('mock_desk.portal_ticket_detail_view', vals)

    @http.route(['/my/ticket/print/<int:ticket_id>'], type="http", auth="user", website=True)
    def ticketReport(self, ticket_id, **kw):
        print("Hello this ticket is:  ", ticket_id)
        ticket_val = request.env['mockdesk.ticket'].sudo().search([('id', '=', ticket_id)])

        return self._show_report(model=ticket_val, report_type='pdf',
                                 report_ref="mock_desk.report_ticket")

    # Close by customer
    @http.route(['/my/ticket/close/<int:ticket_id>'], type="http", auth="user", website=True)
    def ticketClose(self, ticket_id, **kw):
        print("Hello this ticket is:  ", ticket_id)
        ticket_val = request.env['mockdesk.ticket'].sudo().search([('id', '=', ticket_id)])
        cancel_stage = request.env['mockdesk.stage'].sudo().search([('name', '=', 'Cancelled')], limit=1)
        ticket_val.sudo().write({'stage_id': cancel_stage.id})

        return request.redirect(f"/my/ticket/{ticket_id}")
