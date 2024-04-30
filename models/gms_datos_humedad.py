from odoo import models, fields

class DatosHumedad(models.Model):
    _name = 'gms.datos_humedad'
    _description = 'Datos de Humedad'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    follower_ids = fields.Many2many('res.users', string='Followers')

    humedad = fields.Float(string='Humedad')
    tarifa = fields.Float(string='Tarifa', digits=(16, 4)) 


   
    def buscar_humedad_cercana(self, valor_medida):
        # rango razonable alrededor del valor de medida
        rango = 5.0
        candidatos = self.search([
            ('humedad', '>=', valor_medida - rango),
            ('humedad', '<=', valor_medida + rango)
        ], order='humedad')
        
        # Encontrar el registro con humedad más cercana a valor_medida
        if candidatos:
            candidato_mas_cercano = min(candidatos, key=lambda x: abs(x.humedad - valor_medida))
            return candidato_mas_cercano.tarifa
        return 0