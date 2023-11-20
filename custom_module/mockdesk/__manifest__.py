# -*- coding: utf-8 -*-
{
    "name": "mockdesk",
    "summary": """
      This is mock help desk module """,
    "description": """
        Help contribute ,manage ticket
    """,
    "author": "THomasVu",
    "website": "",
    "sequence": -110,
    "category": "Helpdesk",
    "version": "0.1",
    # any module necessary for this one to work correctly
    "depends": ["mail", "base", "ansv__project"],
    # always loaded
    "data": [
        # khai bao group luon phai de dang truoc
        "security/security_group.xml",
        "security/ir.model.access.csv",
        "views/helpdesk_menu_view.xml",
        "views/helpdesk_all_ticket_view.xml",
        "views/helpdesk_ticket_tag_view.xml",
        "views/helpesk_stage_view.xml",
        "views/helpdesk_type_ticket_view.xml",
        "views/helpdesk_team_view.xml",
        "views/helpdesk_dashboard_view.xml",
        "views/helpdesk_sla_policy_view.xml",

    ],
    "demo": [],
    "installable": True,
    "application": True,
    "assets": {
        "web.assets_backend": [
            "mockdesk/static/src/scss/*.scss",
            "mockdesk/static/src/components/dashboard/*.js",
            "mockdesk/static/src/components/dashboard/*.xml",
            "mockdesk/static/src/components/dashboard/*.css",
        ],
    },
    "auto_install": False,
    "license": "AGPL-3",
}
