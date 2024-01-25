# -*- coding: utf-8 -*-
{
    "name": "ANSV Project",
    "summary": """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",
    "description": """
        Long description of module's purpose
    """,
    "sequence": -1,
    "author": "My Company",
    "website": "https://www.yourcompany.com",
    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    "category": "Uncategorized",
    "version": "0.1",
    # any module necessary for this one to work correctly
    "depends": [
        "mail",
        "base",
        "web",
        "portal",
        "website",
        "contact_inheritence",
    ],
    "application": True,
    # always loaded
    "data": [
        "data/mail_template_create.xml",
        "data/sequence_data.xml",

        "security/security_access_data.xml",
        "security/ir.model.access.csv",

        "views/project_ansv_view.xml",
        "views/product_view.xml",
        "views/configure_view.xml",
        "views/tasks_view.xml",
        "views/project_stages.xml",
        "views/task_stages.xml",
        "views/team_project.xml",
        "views/mail_activity_views.xml",
        "views/dashboard_project.xml",
        "views/graphs_view.xml",
        # data
        # 'data/components_data.xml'
    ],
    # only loaded in demonstration mode
    "demo": [],
    "assets": {
        "web.assets_backend": [
            "ansv__project/static/src/**/*.css",
            # "ansv__project/static/src/components/project_task_name_with_subtask_count_char_field/*.js",
            # "ansv__project/static/src/components/project_task_name_with_subtask_count_char_field/*.xml",
            "ansv__project/static/src/components/**/*.js",
            "ansv__project/static/src/components/**/*.xml",
            "ansv__project/static/libs/**/*.js",
            "ansv__project/static/libs/**/*.css",
        ],
    },
}
