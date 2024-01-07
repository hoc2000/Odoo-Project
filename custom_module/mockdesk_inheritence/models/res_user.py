from odoo import models, fields


class ResUsers(models.Model):
    _inherit = ['res.users']

    def name_get(self):
        result = []
        for user in self:
            # Customize how you want the user's name to be displayed
            # name = f"{user.name} ({user.login})"
            if user.has_group('mock_desk.group_manager_mockdesk'):
                name = f"[Manager]{user.name}"
            else:
                name = f"{user.name}"
            result.append((user.id, name))
        return result
