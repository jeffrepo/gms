from odoo import models, fields

class GmsRutas(models.Model):
    _name = 'gms.rutas'
    _description = 'Modelo Rutas'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'nombre_ruta'



    follower_ids = fields.Many2many('res.users', string='Followers', tracking ="1")
    nombre_ruta = fields.Char(string='Nombre de la ruta', tracking ="1")
    direccion_origen_id = fields.Many2one('res.partner', string='Origen', required=True, tracking="1")
    direccion_destino_id = fields.Many2one('res.partner', string='Destino', required=True, tracking="1")
    kilometros = fields.Float(string='Kilómetros', tracking ="1")

 

    # gasto_viaje_id = fields.Many2one(
    #     'product.product', 
    #     string='Gasto del Viaje', 
    #     domain=[('detailed_type', '=', 'service')],
    #     tracking="1"
    # )