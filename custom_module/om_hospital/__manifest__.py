{
    'name': "Hospital Management",
    'version': '1.0',
    'author': "THV",
    'category': 'Management',
    'sequence': -100,
    'website': 'https://www.ansv.vn/',
    'summary': 'Quản lý bệnh viện',
    'description': """
            Quản lý bệnh viện
    """,
    'depends': ['mail', 'product'],
    'data': [
        'security/ir.model.access.csv',

        'data/patient.tag.csv',
        'data/patient_tag_data.xml',
        'data/sequence_data.xml',
        'views/menu.xml',
        'views/patient/patient_view.xml',
        'views/patient/female_patient_view.xml',
        'views/appointment/appointment_view.xml',
        'views/patient_tag_view.xml',
        'views/wizard/cancel_appointment_view.xml',
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'AGPL-3',

}
