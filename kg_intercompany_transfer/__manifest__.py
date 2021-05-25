# -*- coding: utf-8 -*-
{
    'name': "Intercompany Inventory Transfer",

    'summary': """
    Inter Company Stock Transfer
        """,

    'description': """

    Create new inventory transfer method where 1 or more product is required to be transferred from Company X to Company Y. 
    This will be within the inventory module only (NO SO or PO process involved during the transfer)

    """,

    'author': "Pranav",
    'website': "http://www.klystronglobal.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Warehouse',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','stock'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/inherited_views.xml',
        'data/data.xml',
    ],
}