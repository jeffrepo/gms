
from odoo import api, fields, models, _

class SaleOrder(models.Model):
    _inherit = "sale.order"

    viaje_ids = fields.One2many('gms.viaje', compute='_compute_viajes')
    viaje_count = fields.Integer(string='Viajes', compute='_compute_viajes')

    @api.depends('name')
    def _compute_viajes(self):
        for order in self:
            viajes = self.env['gms.viaje'].search([('pedido_venta_id', '=', order.id)])
            order.viaje_ids = viajes
            order.viaje_count = len(viajes)





    def action_view_viajes(self):
        self.ensure_one()
        domain = [('pedido_venta_id', '=', self.id)]
        return {
            'name': _('Viajes asociados al Pedido'),
            'view_mode': 'tree,form',
            'res_model': 'gms.viaje',
            'type': 'ir.actions.act_window',
            'domain': domain,
        }
