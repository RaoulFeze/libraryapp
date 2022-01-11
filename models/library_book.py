import dateutil.utils
from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import timedelta

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
    category_id = fields.Many2one('library.book.category', string='Category')

    ## Database Constraint
    # _sql_constraints = [('name_uniq', 'UNIQUE(name)', 'Book Title must be unique.'),
    #                     ('positive_page', 'CHECK(pages>0)', 'The number of pages must be positive')]

    ### Python Constraint [Client-side constraints]
    @api.constrains('date_release')
    def _check_release_date(self):
        for record in self:
            if record.date_release and record.date_release > fields.Date.today():
                raise models.ValidationError('Release date must be in the past!')

    @api.constrains('pages')
    def _check_book_pages(self):
        for record in self:
            if record.pages <= 0:
                raise models.ValidationError('The number of page must be greater than 0')

    ### Computing Methods
    @api.depends('date_release')
    def _compute_age(self):
        today = fields.Date.today()
        for book in self:
            if book.date_release:
                delta = today-book.date_release
                book.age_days = delta.days
            else:
                book.age_days = 0

    def _inverse_age(self):
        today = fields.Date.today()
        for book in self.filtered('date_release'):
            d = today - timedelta(days=book.age_days)
            book.date_release= d

    def _search_age(self, operator, value):
        today = fields.Date.today()
        value_days = timedelta(days=value)
        value_date = today - value_days

        #convert the operator
        #book with age . value have a date < value_date
        operator_map = {'>':'<',
                        '>=':'<=',
                        '<':'>',
                        '<=':'>=',
                        }
        new_op = operator_map.get(operator, operator)
        return [('date-release', new_op, value_date)]

    age_days = fields.Float(string='Days Since Release',
                            compute='_compute_age',
                            inverse='_inverse_age',
                            search='_search_age',
                            store=False, # Optional
                            compute_sudo=True # Optional
                            )


class ResPartner(models.Model):
    _inherit = 'res.partner'
    publisher_book_ids = fields.One2many('library.book','publisher_id',string='published Books')
    authored_book_ids = fields.Many2many('library.book', string='Authored Books',
                                         relation='library_book_res_partner_rel' #optional
                                         )