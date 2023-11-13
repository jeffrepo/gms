from odoo import models, fields, api

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    gasto_viaje_con_impuesto = fields.Boolean(string="Gasto del viaje con impuesto")
    gasto_viaje_sin_impuesto = fields.Boolean(string="Gasto del viaje sin impuesto")

   
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param('gms.gasto_viaje_con_impuesto', self.gasto_viaje_con_impuesto)
        self.env['ir.config_parameter'].sudo().set_param('gms.gasto_viaje_sin_impuesto', self.gasto_viaje_sin_impuesto)

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res.update(
            gasto_viaje_con_impuesto=self.env['ir.config_parameter'].sudo().get_param('gms.gasto_viaje_con_impuesto'),
            gasto_viaje_sin_impuesto=self.env['ir.config_parameter'].sudo().get_param('gms.gasto_viaje_sin_impuesto'),
        )
        return res
