from odoo import api, fields, models, _

class SaleOrder(models.Model):
    _inherit = "sale.order"

    viaje_ids = fields.One2many('gms.viaje', 'sale_order_id', string='Viajes')
    viaje_count = fields.Integer(string='Número de Viajes', compute='_compute_viaje_count')

    @api.depends('viaje_ids')
    def _compute_viaje_count(self):
        for order in self:
            order.viaje_count = len(order.viaje_ids)

    def action_view_viajes(self):
        self.ensure_one()
        domain = [('sale_order_id', '=', self.id)]  # Cambio aquí para que coincida con el campo relacional
        return {
            'name': _('Viajes asociados al Pedido'),
            'view_mode': 'tree,form',
            'res_model': 'gms.viaje',
            'type': 'ir.actions.act_window',
            'domain': domain,
        }
