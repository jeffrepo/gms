from odoo import models, fields

class DatosFlete(models.Model):
    _name = 'gms.datos_flete'
    _description = 'Datos de Flete'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    follower_ids = fields.Many2many('res.users', string='Followers')
    flete_km = fields.Float(string='Flete kilometros')
    tarifa = fields.Float(string='Tarifa', digits=(16, 4))  #4 decimales

    def buscar_flete_cercano(self, kilometros_flete):
        
        rango = 5.0  
        candidatos = self.search([
            ('flete_km', '>=', kilometros_flete - rango),
            ('flete_km', '<=', kilometros_flete + rango)
        ], order='flete_km')
        
        # Encontrar el registro con kilometraje más cercano a kilometros_flete
        if candidatos:
            candidato_mas_cercano = min(candidatos, key=lambda x: abs(x.flete_km - kilometros_flete))
            return candidato_mas_cercano.tarifa
        return 0
    