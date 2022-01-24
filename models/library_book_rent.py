from odoo import models, fields, api
from datetime import timedelta
from odoo.exceptions import ValidationError, UserError
from odoo.tools.translate import _

class LibraryBookRent(models.Model):
    _name = 'library.book.rent'
    book_id = fields.Many2one('library.book', string='Book', required=True)
    borrower_id = fields.Many2one('res.partner', string='Borrower', required=True)
    state = fields.Selection([('available','Available'),
                              ('ongoing','Ongoing'),
                              ('returned','Returned'),
                              ('lost','Lost')],
                             'State', default='ongoing', required=True)
    rent_date = fields.Date(default=fields.Date.today)
    return_date = fields.Date()

    @api.model
    def create(self, vals):
        book_rec = self.env['library.book'].browse(vals['book_id'])  # returns record set from for given id
        book_rec.make_borrowed()
        return super(LibraryBookRent, self).create(vals)

    def book_rent(self):
        self.ensure_one()
        if self.state == 'available':
            raise UserError(_('Book is not available for renting'))
        rent_as_superuser = self.env['library.book.rent'].sudo()
        rent_as_superuser.create({'book_id':self.id,
                                  'borrower_id':self.env.user.partner_id.id,})

    def book_lost(self):
        self.ensure_one
        self.sudo().state = 'lost'
        book_with_different_context = self.book_id.with_context(avoid_deactivate=True)
        book_with_different_context.sudo().make_lost()