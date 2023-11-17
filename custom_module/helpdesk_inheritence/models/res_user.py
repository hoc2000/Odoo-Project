from odoo import models, fields


class ResUsers(models.Model):
    _inherit = ['res.users']

    def name_get(self):
        result = []
        for user in self:
            # Customize how you want the user's name to be displayed
            # name = f"{user.name} ({user.login})"
            if user.has_group('mockdesk.group_TASC_helpdesk'):
                name = f" [TASC] {user.name}"
            elif user.has_group('mockdesk.group_DO_helpdesk'):
                name = f"[DO] {user.name}"
            elif user.has_group('mockdesk.group_AM_helpdesk'):
                name = f"[AM] {user.name}"
            elif user.has_group('mockdesk.group_BGD_helpdesk'):
                name = f"[BGD] {user.name}"
            else:
                name = f"{user.name}"
            result.append((user.id, name))
        return result
