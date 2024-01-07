# -*- coding: utf-8 -*-

from odoo.addons.portal.controllers.portal import CustomerPortal, pager
from odoo.http import request
from odoo import http


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
    def ticket_list_view(self, page=1, **kw):
        current_user = request.env.user.id
        user_partner_id = request.env.user.partner_id.id

        ticket_obj = request.env['mockdesk.ticket']
        # Pagination
        total_ticket = ticket_obj.search_count(
            ['|', ('create_uid', '=', current_user), ('customer_id', '=', user_partner_id)])
        page_detail = pager(url='/my/ticket',
                            total=total_ticket,
                            page=page,
                            step=7)

        tickets = ticket_obj.search(['|', ('create_uid', '=', current_user), ('customer_id', '=', user_partner_id)],
                                    limit=7, offset=page_detail['offset'])
        vals = {'tickets': tickets, 'page_name': 'ticket_list', 'pager': page_detail}
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
