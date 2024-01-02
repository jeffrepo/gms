from odoo import models, fields, api

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    gasto_viaje_con_impuesto_id = fields.Many2one(
        'product.product',
        string='Gasto del Viaje con Impuesto',
    )

    gasto_viaje_sin_impuesto_id = fields.Many2one(
        'product.product',
        string='Gasto del Viaje sin Impuesto',
    )

    producto_secado_id = fields.Many2one(
        'product.product', 
        string='Producto Secado'
    )
    producto_pre_limpieza_id = fields.Many2one(
        'product.product', 
        string='Producto Pre Limpieza'
    )
    producto_flete_puerto_id = fields.Many2one(
        'product.product', 
        string='Producto Flete Puerto'
    )
   
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param('gms.gasto_viaje_con_impuesto_id', self.gasto_viaje_con_impuesto_id.id)
        self.env['ir.config_parameter'].sudo().set_param('gms.gasto_viaje_sin_impuesto_id', self.gasto_viaje_sin_impuesto_id.id)
        self.env['ir.config_parameter'].sudo().set_param('gms.producto_secado_id', self.producto_secado_id.id)
        self.env['ir.config_parameter'].sudo().set_param('gms.producto_pre_limpieza_id', self.producto_pre_limpieza_id.id)
        self.env['ir.config_parameter'].sudo().set_param('gms.producto_flete_puerto_id', self.producto_flete_puerto_id.id)

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        config_params = self.env['ir.config_parameter'].sudo()
        res.update(
            gasto_viaje_con_impuesto_id=int(config_params.get_param('gms.gasto_viaje_con_impuesto_id', 0)),
            gasto_viaje_sin_impuesto_id=int(config_params.get_param('gms.gasto_viaje_sin_impuesto_id', 0)),
            producto_secado_id=int(config_params.get_param('gms.producto_secado_id', 0)),
            producto_pre_limpieza_id=int(config_params.get_param('gms.producto_pre_limpieza_id', 0)),
            producto_flete_puerto_id=int(config_params.get_param('gms.producto_flete_puerto_id', 0)),
        )
        return res

