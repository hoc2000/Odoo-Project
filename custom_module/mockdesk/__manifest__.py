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
    "sequence": 99,
    "category": "Helpdesk",
    "version": "0.1",
    # any module necessary for this one to work correctly
    "depends": ["ansv__project","rating","portal"],
    # always loaded
    "data": [
        # khai bao group luon phai de dang truoc
        "security/security_group.xml",
        "security/ir.model.access.csv",

        "data/sequence_data.xml",
        "data/mail_template.xml",
        "data/cron.xml",

        "views/helpdesk_menu_view.xml",
        "views/helpdesk_all_ticket_view.xml",
        "views/helpdesk_my_ticket_view.xml",
        "views/helpdesk_ticket_tag_view.xml",
        "views/helpesk_stage_view.xml",
        "views/helpdesk_type_ticket_view.xml",
        "views/helpdesk_team_view.xml",
        "views/helpdesk_dashboard_view.xml",
        "views/helpdesk_sla_policy_view.xml",
        "views/graphs_view.xml",
        "views/mail_activity_views.xml",
        "views/potal_template.xml",
        "views/website_form.xml",
        "views/website_homepage.xml",

    ],
    "demo": [],
    "installable": True,
    "application": True,
    "auto_install": False,
    "license": "AGPL-3",
    "assets": {
        "web.assets_backend": [
            "mockdesk/static/src/**/*.js",
            "mockdesk/static/src/**/*.xml",
            "mockdesk/static/src/**/*.css",
            "mockdesk/static/src/scss/*.scss",
        ],
    },

}
