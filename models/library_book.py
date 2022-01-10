import dateutil.utils
from odoo import models, fields

class LibraryBook(models.Model):
    _name = 'library.book'
    _description = 'Library Book'
    _order = 'date_release desc, name'
    _rec_name = 'short_name'

    name = fields.Char('Title', required=True)
    short_name = fields.Char('Short title', required=True, translate=True, index=True)
    notes = fields.Text('Internal Notes')
    state = fields.Selection([('draft','Not Available'),
                              ('available','Available'),
                              ('lost','Lost')],
                             'State', default='draft')
    description = fields.Html('Description', sanitize=True, strip_style=False)
    cover = fields.Binary('Book Cover')
    out_of_print = fields.Boolean('Out of Print?')
    date_release = fields.Date('Release date', default=dateutil.utils.today())
    date_updated = fields.Datetime('Last Updated')
    pages = fields.Integer('Number of Pages', groups='base.group_user', states={'lost': [('readonly', True)]}, help='Total book page count',company_dependent=False)
    reader_rating = fields.Float('reader Average Rating', digits=(14,4) #Optional precisions decimals,
    )
    author_ids = fields.Many2many('res.partner', string='Author')
    cost_price = fields.Float('Book Cost', digits='BookPrice')
    currency_id = fields.Many2one('res.currency', string='Currency')
    retail_price = fields.Monetary('Retail Price', #currency_field = 'currency_id',
    )
    publisher_id = fields.Many2one('res.partner', string='Publisher',
                                   #optional:
                                   ondelete='set null',
                                   context={},
                                   domain=[],
                                   )

class ResPartner(models.Model):
    _inherit = 'res.partner'
    publisher_book_ids = fields.One2many('library.book','publisher_id',string='published Books')
    authored_book_ids = fields.Many2many('library.book', string='Authored Books',
                                         relation='library_book_res_partner_rel' #optional
                                         )