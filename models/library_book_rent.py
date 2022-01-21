from odoo import models, fields, api
from datetime import timedelta
from odoo.exceptions import ValidationError, UserError
from odoo.tools.translate import _

class LibraryBookRent(models.Model):
    def book_rent(self):
        self.ensure_one()
        if self.state == 'available':
            raise UserError(_('Book is not available for renting'))
        rent_as_superuser = self.env['library.book.rent'].sudo()
        rent_as_superuser.create({'book_id':self.id,
                                  'borrower_id':self.env.user.partner_id.id,})
    _name = 'library.book.rent'
    book_id = fields.Many2one('library.book', 'Book', required=True)
    borrower_id = fields.Many2one('res.partner', 'Borrower', required=True)
    state = fields.Selection([('available','Available'),
                              ('ongoing','Ongoing'),
                              ('returned','Returned')],
                             'State', default='ongoing', required=True)
    rent_date = fields.Date(default=fields.Date.today)
    return_date = fields.Date()