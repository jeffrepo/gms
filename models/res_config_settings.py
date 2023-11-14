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
   
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param('gms.gasto_viaje_con_impuesto_id', self.gasto_viaje_con_impuesto_id.id)
        self.env['ir.config_parameter'].sudo().set_param('gms.gasto_viaje_sin_impuesto_id', self.gasto_viaje_sin_impuesto_id.id)

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        config_params = self.env['ir.config_parameter'].sudo()
        res.update(
            gasto_viaje_con_impuesto_id=int(config_params.get_param('gms.gasto_viaje_con_impuesto_id', 0)),
            gasto_viaje_sin_impuesto_id=int(config_params.get_param('gms.gasto_viaje_sin_impuesto_id', 0)),
        )
        return res

