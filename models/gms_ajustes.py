from odoo import models, fields, api, _

class Ajustes(models.Model):
    _name = 'gms.ajustes'
    _description = 'Modelo para Ajustes'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(required=True, default=lambda self: _('New'), copy=False, readonly=True, tracking=True)
    date_order = fields.Date('Fecha de Ajuste')
    partner_id = fields.Many2one('res.partner', string='Cliente')

    state = fields.Selection([
        ('draft', 'Borrador'),
        ('confirmed', 'Confirmado'),
        ('done', 'Realizado'),
        ('cancel', 'Cancelado')
    ], string='Estado', default='draft')
    
    total = fields.Float('Total')
    follower_ids = fields.Many2many('res.users', string='Followers')


    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('gms.ajustes')
        return super().create(vals_list)
   

    def action_confirm(self):
        self.state = 'confirmed'

    def action_done(self):
        self.state = 'done'

    def action_cancel(self):
        self.state = 'cancelled'

    def action_draft(self):
        self.state = 'draft'