# -*- coding: utf-8 -*-
# from odoo import http


# class Libraryapp(http.Controller):
#     @http.route('/libraryapp/libraryapp', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/libraryapp/libraryapp/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('libraryapp.listing', {
#             'root': '/libraryapp/libraryapp',
#             'objects': http.request.env['libraryapp.libraryapp'].search([]),
#         })

#     @http.route('/libraryapp/libraryapp/objects/<model("libraryapp.libraryapp"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('libraryapp.object', {
#             'object': obj
#         })
