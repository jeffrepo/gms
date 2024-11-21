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

    cantidad_kilos_flete_puerto = fields.Float(
        string='Cantidad Kilos por Kilómetro para Flete Puerto',
        digits=(10, 4)
    )

    def set_values(self):
        """Guardar los valores en ir.config_parameter."""
        super(ResConfigSettings, self).set_values()
        config_params = self.env['ir.config_parameter'].sudo()
        
        config_params.set_param('gms.gasto_viaje_con_impuesto_id', self.gasto_viaje_con_impuesto_id.id or 0)
        config_params.set_param('gms.gasto_viaje_sin_impuesto_id', self.gasto_viaje_sin_impuesto_id.id or 0)
        config_params.set_param('gms.producto_secado_id', self.producto_secado_id.id or 0)
        config_params.set_param('gms.producto_pre_limpieza_id', self.producto_pre_limpieza_id.id or 0)
        config_params.set_param('gms.producto_flete_puerto_id', self.producto_flete_puerto_id.id or 0)
        config_params.set_param('gms.cantidad_kilos_flete_puerto', self.cantidad_kilos_flete_puerto or 0.0)

    @api.model
    def get_values(self):
        """Recuperar los valores desde ir.config_parameter."""
        res = super(ResConfigSettings, self).get_values()
        config_params = self.env['ir.config_parameter'].sudo()

        res.update({
            'gasto_viaje_con_impuesto_id': int(config_params.get_param('gms.gasto_viaje_con_impuesto_id', 0)),
            'gasto_viaje_sin_impuesto_id': int(config_params.get_param('gms.gasto_viaje_sin_impuesto_id', 0)),
            'producto_secado_id': int(config_params.get_param('gms.producto_secado_id', 0)),
            'producto_pre_limpieza_id': int(config_params.get_param('gms.producto_pre_limpieza_id', 0)),
            'producto_flete_puerto_id': int(config_params.get_param('gms.producto_flete_puerto_id', 0)),
            'cantidad_kilos_flete_puerto': float(config_params.get_param('gms.cantidad_kilos_flete_puerto', 0.0)),
        })
        return res
