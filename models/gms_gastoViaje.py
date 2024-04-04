from odoo import models, fields

class GastosViaje(models.Model):
    _name = 'gms.gasto_viaje'
    _description = 'Gastos de Viaje'
    _inherit = ['mail.thread', 'mail.activity.mixin']


    follower_ids = fields.Many2many('res.users', string='Followers')
    name = fields.Char(string='Descripción', required=True, tracking ="1")
    producto_id = fields.Many2one('product.product', string='Producto', tracking ="1")
    precio_total = fields.Float(string='Precio Total', tracking ="1")
    viaje_id = fields.Many2one('gms.viaje', string='Viaje', tracking ="1")
    purchase_order_id = fields.Many2one('purchase.order', string='Orden de Compra' , readonly=True)
    purchase_order_line_id = fields.Many2one('purchase.order.line', string='Línea de Orden de Compra', readonly=True)
    es_de_ruta = fields.Boolean(string='Es de Ruta', default=False)
    purchase_line_id = fields.Many2one('purchase.order.line', string='Línea de Orden de Compra')

    moneda_id = fields.Many2one('res.currency', string='Moneda')

    # ver solo aquellos partners que tienen una clasificación de proveedor 

    proveedor_id = fields.Many2one(
    'res.partner', 
    string='Proveedor',
    domain=[('supplier_rank', '>', 0)],
    context={'res_partner_search_mode': 'supplier'},
    help="Este es el proveedor del gasto."
    )

    


    estado_compra = fields.Selection([
    ('comprado', 'Comprado'),
    ('no_comprado', 'No comprado'),
    ('no_aplica', 'No Aplica')
], string='Estado de compra', default='no_aplica', tracking="1")





    def action_generate_purchase_order_from_gastos(self):
        PurchaseOrder = self.env['purchase.order']
        PurchaseOrderLine = self.env['purchase.order.line']

        # Agrupa los gastos por proveedor
        grouped_gastos_by_proveedor = {}
        for gasto in self:
            if gasto.proveedor_id not in grouped_gastos_by_proveedor:
                grouped_gastos_by_proveedor[gasto.proveedor_id] = []
            grouped_gastos_by_proveedor[gasto.proveedor_id].append(gasto)

        # Por cada proveedor, crea una orden de compra
        for proveedor, gastos in grouped_gastos_by_proveedor.items():
            po_vals = {
                'partner_id': proveedor.id,
                'order_line': [],
            }
            new_order = PurchaseOrder.create(po_vals)
            for gasto in gastos:
                if gasto.estado_compra == 'no_comprado':
                    po_line_vals = {
                        'order_id': new_order.id,
                        'product_id': gasto.producto_id.id,
                        'name': gasto.name or gasto.producto_id.name,
                        'product_qty': 1,
                        'price_unit': gasto.precio_total,
                        'product_uom': gasto.producto_id.uom_id.id,
                        'date_planned': fields.Date.today(),
                    }
                    new_order_line = PurchaseOrderLine.create(po_line_vals)
                    gasto.write({
                        'purchase_order_id': new_order.id,
                        'purchase_order_line_id': new_order_line.id,
                        'estado_compra': 'comprado'
                    })

        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }




    
