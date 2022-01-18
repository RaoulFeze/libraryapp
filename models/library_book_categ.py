from odoo import models, fields, api
from odoo.exceptions import ValidationError


class BookCategory(models.Model):
    _name = 'library.book.category'
    _parent_store = True # Needed to support the HIERARCHY
    _parent_name ="parent_id" # optional field parent_id; Needed to support the HIERARCHY

    name = fields.Char('Category')
    description = fields.Text('Description')
    parent_id = fields.Many2one('library.book.category',
                                string='Parent Category',
                                ondelete='restrict',
                                index=True) # Adds a field to reference the parent record
    child_ids = fields.One2many('library.book.category',
                                'parent_id', # Provides a shortcut to access all the records with this record as their parent
                                string='Child Categories')
    parent_path = fields.Char(index=True) # Needed to support the HIERARCHY.

    @api.constrains('parent_id')
    def _check_hierarchy(self):
        if not self._check_recursion():
            raise models.ValidationError('Error! You cannot create recurcive Catagory')

