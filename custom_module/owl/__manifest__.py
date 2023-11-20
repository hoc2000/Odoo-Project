# -*- coding: utf-8 -*-
{
    "name": "owl",
    "summary": """
      """,
    "description": """
        Long description of module's purpose
    """,
    "author": "Hoc Vu Tu",
    "website": "https://www.yourcompany.com",
    "category": "OWL",
    "version": "0.1",
    # any module necessary for this one to work correctly
    "sequence": -1,
    "depends": ["base","web"],
    "installable": True,
    "application": True,
    # always loaded
    "data": [
        # security
        "security/ir.model.access.csv",
        "views/todo_list_view.xml",
        "views/res_partner.xml",
    ],
    # only loaded in demonstration mode
    "demo": [],
    "assets": {
        "web.assets_backend": [
            "owl/static/src/components/*/*.js",
            "owl/static/src/components/*/*.xml",
            "owl/static/src/components/todo_list/fonts/JosefinSans/*.css",
        ],
    },
}
