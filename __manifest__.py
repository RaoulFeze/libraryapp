# -*- coding: utf-8 -*-
{
    'name': "libraryapp",

    'summary': """
        Test Case of a Library Application with Odoo""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Raoul",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        'security/groups.xml',
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'views/library_book.xml',  # Each a new view is created, we should add it to the manifest
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
