# -*- coding: utf-8 -*-

from odoo.addons.portal.controllers.portal import CustomerPortal, pager
from odoo.http import request
from odoo import http


class PortalAccount(CustomerPortal):
    def _prepare_home_portal_values(self, counters):
        values = super(PortalAccount, self)._prepare_home_portal_values(counters)
        # print(user_partner_id)
        values['appointment_count'] = request.env['hospital.appointment'].sudo().search_count([])
        return values
    #
    @http.route(['/my/appointment', '/my/appointment/page/<int:page>'], type="http", website=True)
    def appointment_list_view(self, page=1, **kw):
        appointment_obj = request.env['hospital.appointment']
        # Pagination
        total_appointment = appointment_obj.search_count([])
        page_detail = pager(url='/my/appointment',
                            total=total_appointment,
                            page=page,
                            step=7)

        appointments = appointment_obj.search([], limit=7, offset=page_detail['offset'])
        vals = {'appointments': appointments, 'page_name': 'appointment_list', 'pager': page_detail}
        return request.render('om_hospital.portal_ticket_list_view_customer', vals)

    # Hiện thị record theo ID
    # Record hiển thị có thể chuyển giao Pagination được
    @http.route(['/my/appointment/<int:appointment_id>'], type="http", auth="public", website=True)
    def appointment_detail_view(self, appointment_id, **kw):
        appointment = request.env['hospital.appointment'].sudo().search([('id', '=', appointment_id)])
        print(appointment)
        vals = {'appointment': appointment, 'page_name': 'appointment_detail_view'}
        # ticket_records = request.env['helpdesk.ticket'].search([])
        return request.render('om_hospital.portal_appointment_detail_view', vals)
