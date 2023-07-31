from odoo import models, fields

class GmsRutas(models.Model):
    _name = 'gms.rutas'
    _description = 'Modelo Rutas'
    
    nombre_ruta = fields.Char(string='Nombre de la ruta')
    direccion_origen = fields.Char(string='Dirección de origen')
    direccion_destino = fields.Char(string='Dirección de destino')
    kilometros = fields.Float(string='Kilómetros')
