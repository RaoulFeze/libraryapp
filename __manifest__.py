# -*- coding: utf-8 -*-
{
    'name': "libraryapp",

    'summary': """
        Test Case of a Library Application with Odoo""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Thinksoft Inc.",
    'website': "http://www.thinksoft.ca",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'product'],

    # always loaded
    'data': [
        # Each a new view is created, we should add it to the manifest
        'security/groups.xml',
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'views/library_category.xml',
        'views/library_book.xml',
        'views/library_book_copy.xml',
        'views/library_member.xml',
        'views/library_book_rent.xml',
        'data/data.xml',
        'data/demo.xml',
        'wizard/library_rent_wizard.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
