# -*- coding: utf-8 -*-
{
    'name': "Inter company Inventory Transfer",
    'version': '12.0.1.0.0',
    'summary': """
    Transfer stock between companies.
        """,

    'description': """
    
    This module helps to transfer 1 or more product from Company X to Company Y in a multi company concept.
    Module can be used, if company X and company Y is having separate product list 
    (Note : Odoo default feature can be used if you are trying to transfer stock for a product 
    having product Id shared by both company)
    
    This will be within the inventory module only (NO SO or PO process involved during the transfer)

    """,

    'author': "Klystron Global",
    'website': "http://www.klystronglobal.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Warehouse',
    'maintainer': 'Pranav P S',

    # any module necessary for this one to work correctly
    'depends': ['base','stock'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/inherited_views.xml',
        'data/data.xml',
    ],
    'images': ['static/description/banner.png'],
    'installable': True,
    'auto_install': False,
    'application': False,
}