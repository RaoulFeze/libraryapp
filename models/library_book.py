import dateutil.utils
import requests
from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError
from datetime import timedelta
from odoo.tools.translate import _

class BaseArchive(models.AbstractModel):
    _name = 'base.archive'
    active = fields.Boolean(default=True)
    def do_archive(self):
        for record in self:
            record.active = not record.active

class LibraryBook(models.Model):

    # Database Constraint
    _sql_constraints = [('name_uniq', 'UNIQUE(name)', 'Book Title must be unique.'),
                        ('positive_page', 'CHECK(pages>0)', 'The number of pages must be positive')]

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

    @api.constrains('age_days')
    def _check_age_days(self):
        for record in self:
            if record.age_days < 0:
                raise models.ValidationError('The Release Date should not be in the Future.')

    ### Computing Methods
    @api.depends('date_release')
    def _compute_age(self):
        today = fields.Date.today()
        for book in self:
            # if book.date_release:
            #     delta = today-book.date_release
            #     book.age_days = delta.days
            # else:
            #     book.age_days = 0
            book.age_days = (today - book.date_release).days if book.date_release else 0

    # @api.constrains('age_days')
    def _inverse_age(self):
        today = fields.Date.today()
        for book in self.filtered('date_release'):
            d = today - timedelta(days=book.age_days)
            release_date = d

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

    @api.model
    def _referencable_models(self):
        models = self.env['ir.model'].search([('field_id.name', '=', 'message_ids')])
        return [(x.model, x.name) for x in models]

    @api.depends('authored_book_ids')
    def _compute_count_books(self):
        for r in self:
            r.count_book = len(r.authored_book_ids)

    @api.model
    def is_allowed_transition(self, old_state, new_state):
        allowed = [('draft','available'),
                   ('available','borrowed'),
                   ('borrowed','available'),
                   ('available','lost'),
                   ('borrowed','lost'),
                   ('lost','available')]
        return (old_state, new_state) in allowed

    def change_state(self, new_state):
        for book in self:
            if book.is_allowed_transition(book.state,new_state):
                book.state = new_state
            else:
                msg = _('Moving from %s to %s is not allowed') % (book.state, new_state)
                raise UserError(msg)

    def make_available(self):
        self.change_state('available')

    def make_borrowed(self):
        self.change_state('borrowed')

    def make_lost(self):
        self.change_state('lost')

    def post_to_webservice(self, data):
        try:
            req = requests.post('http://my-test-service.com', data=data, timeout=10)
            content = req.json()
        except IOError:
            error_msg = _('Something went wrong during data submission')
            raise UserError(error_msg)
        return content

    def log_all_library_members(self):
        # library.member
        library_member_model = self.env['library.member']

        all_members = library_member_model.search([])
        print('ALL MEMBERS:', all_members)
        return True

    def create_categories(self): # Chapter 5
        categ1 = {'name':'Child category 1',
                  'description':'Description for child 1'}
        categ2 = {'name':'Child category 2',
                  'description':'Description for child 2'}
        parent_category_val = {'name':'Parent category',
                               'description':'Description for parent category',
                               'child_ids':[(0, 0, categ1),(0,0,categ2),]}
        record = self.env['library.book.category'].create(parent_category_val)

    def change_update_date(self):
        self.ensure_one() # Ensures that self contains anly one record. It avoids the modification of many records by raising an exception
        self.date_release = fields.Date.today()

    def find_book(self):
        domain = ['|',
                  '&',
                  ('name','ilike','Book Name'),
                  ('category_id.name','ilike','Category Name'),
                  '&',
                  ('name','ilike','Book Name 2'),
                  ('category_id.name','ilike','Category Name 2')]
        books = self.search(domain)

    @api.model
    def books_with_multiple_authors(self, all_books):
        def predicate(book):
            if len(book.author_ids) > 1:
                return True
            return False
        return all_books.filter(predicate)

    @api.model
    def get_author_names(self, books):
        return books.mapped('author_ids.name')

    @api.model
    def sort_books_by_date(self,books):
        return books.sorted(key='release_date')

    # overrinding the create method and raising and exception
    @api.model
    def create(self,values):
        if not self.user_has_groups('my_library.acl_book_librarian'):
            if 'manager_remarks' in values:
                raise UserError(('You are not allowed to modify %s ')% ('manager_remarks'))
        return super(LibraryBook,self).create(values)

    # Overriding the write() method and deleting the new value
    def write(self, values):
        if not self.user_has_groups('my_library.acl_book_librarian'): # user_has_groups also allows to set restriction on a specific field
            if 'manager_remarks' in values:
                del values['manager_remarks']
        return super(LibraryBook,self).write(values)

    def name_get(self):
        result = []
        for book in self:
            authors = book.author_ids.mapped('name')
            name = '%s (%s)' % (book.name, ', '.join(authors))
            result.append((book.id, name))
            return result

    @api.model
    def _name_search(self, name='',args=None,operator='ilike',limit=100,name_get_uid=None):
        args = [] if args is None else args.copy()
        if not(name == '' and operator == 'ilike'):
            args += ['|', '|',
                     ('name', operator, name),
                     ('isbn', operator, name),
                     ('author_ids.name', operator, name)]
            return super(LibraryBook,self)._name_search(name=name,args=args,operator=operator,limit=limit,name_get_uid=name_get_uid)

    @api.model
    def _get_average_cost(self):
        grouped_result = self.read_group(['cost_price','!=',False], # Domain (the where close)
                                       [('category_id','cost_price:avg')], # Fields to access (the select close)
                                       ['category_id'] # group_by
                                       )
        return grouped_result

    _name = 'library.book'
    _description = 'Library Book'
    _order = 'date_release desc, name'
    _rec_name = 'short_name'
    _inherit = ['base.archive']

    name = fields.Char('Title', required=True)
    short_name = fields.Char('Short title', # required=True,
                             translate=True, index=True)
    isbn = fields.Char('ISBN')
    notes = fields.Text('Internal Notes')
    state = fields.Selection([('draft','Not Available'),
                              ('available','Available'),
                              ('borrowed','Borrowed'),
                              ('lost','Lost')],
                             'State', default='draft')
    description = fields.Html('Description', sanitize=True, strip_style=False)
    cover = fields.Binary('Book Cover')
    out_of_print = fields.Boolean('Out of Print?')
    date_release = fields.Date('Release date', default=dateutil.utils.today())
    # computed_date = fields.Date(string='Computed Date', compute='_inverse_age', store=True, compute_sudo=True)
    date_updated = fields.Datetime('Last Updated')
    cost_price = fields.Float('Book Cost')
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
    # With the RELATED attribute, we can access all the fields in the related table.
    #   The related model (res.partner i.e. publisher) must be must be declared beforehand
    publisher_city = fields.Char('Publisher City', related='publisher_id.city', readonly=True)
    category_id = fields.Many2one('library.book.category', string='Category')

    age_days = fields.Float(string='Days Since Release',
                            compute='_compute_age',
                            inverse='_inverse_age',
                            search='_search_age',
                            store=False, # Optional
                            compute_sudo=True # Optional
                            )
    ref_doc_id = fields.Reference(selection ='_referencable_models', string='Reference Document')
    manager_remarks = fields.Text('Manager Remarks')
    old_edition = fields.Many2one('library.book', string='Old Edition')


class ResPartner(models.Model):
    _inherit = 'res.partner'
    _order = 'name'
    publisher_book_ids = fields.One2many('library.book','publisher_id',string='published Books')
    authored_book_ids = fields.Many2many('library.book', string='Authored Books',
                                         relation='library_book_res_partner_rel' #optional
                                         )
    count_books = fields.Integer('Number of Authored Books', compute='_compute_count_books')

