# -*- coding: utf-8 -*-
{
    "name": "Mockdesk",
    "summary": """
      This is mock help desk module """,
    "description": """
        Help contribute ,manage ticket
    """,
    "author": "TuHocVu",
    "website": "",
    "sequence": -120,
    "category": "Helpdesk",
    "version": "1.0",
    # any module necessary for this one to work correctly
    "depends": ["mail",
                "base",
                "web",
                "rating",
                "portal",
                "ansv__project",
                "contact_inheritence",
                "contacts",
                "website",
                "web_responsive"
                ],
    # always loaded
    "data": [
        # data fixed
        # "data/default_stages.xml",

        # khai bao group luon phai de dang truoc
        "security/security_group.xml",
        "security/ir.model.access.csv",
        #
        "data/sequence_data.xml",
        "data/mail_template.xml",
        "data/cron.xml",
        #
        "views/overview_team_view.xml",
        "views/menu_view.xml",
        "views/dashboard.xml",
        "views/all_ticket_view.xml",
        "views/my_ticket_view.xml",
        "views/stage_view.xml",
        "views/ticket_tag_view.xml",
        "views/type_ticket_view.xml",
        "views/team_view.xml",
        "views/sla_policy_view.xml",
        "views/project_and_product.xml",
        "views/graphs_view.xml",
        "views/mail_activity_views.xml",
        "views/potal_template.xml",
        "views/website_form.xml",
        "views/website_homepage.xml",
        "views/website_product.xml",
        "views/website_project.xml",

        # Reports
        "reports/ticket_reports.xml",
        "reports/ticket_card.xml",

    ],
    "demo": [],
    "installable": True,
    "application": True,
    "auto_install": False,
    "license": "AGPL-3",
    "assets": {
        "web.assets_backend": [
            "mock_desk/static/src/components/*/*.js",
            "mock_desk/static/src/components/*/*.xml",
            "mock_desk/static/src/components/*/*.css",
            "mock_desk/static/src/scss/*.scss",
            "mock_desk/static/src/newfont/newfont2/fonts/JosefinSans/*.css",
        ],
        "web.assets_frontend": [
            "mock_desk/static/src/css/*.css",
            "mock_desk/static/src/newfont/newfont2/fonts/JosefinSans/*.css",
            "mock_desk/static/src/js/*.js",
        ]
    },

}
