from odoo import models, fields
import logging

_logger = logging.getLogger(__name__)

class DatosHumedad(models.Model):
    _name = 'gms.datos_humedad'
    _description = 'Datos de Humedad'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    follower_ids = fields.Many2many('res.users', string='Followers')

    humedad = fields.Float(string='Humedad')
    tarifa = fields.Float(string='Tarifa',  digits=(16, 7))
    tarifa_de_compra = fields.Float(string='Tarifa de Compra',  digits=(16, 7))


   
    def buscar_humedad_cercana(self, valor_medida):
        candidatos = self.search([], order='humedad')
        
        if not candidatos:
            _logger.warning('No hay datos de humedad disponibles.')
            return 0.0  # Retornar 0.0 como float para tarifa
        
        # Obtener los valores de humedad mínimos y máximos en la tabla
        humedad_min = min(candidatos.mapped('humedad'))
        humedad_max = max(candidatos.mapped('humedad'))
    
        # Selección de la tarifa
        if valor_medida <= humedad_min:
            tarifa_seleccionada = self.search([('humedad', '=', humedad_min)], limit=1)
            _logger.info(f'Valor de medida ({valor_medida}) es menor que el mínimo en la tabla. Tarifa seleccionada: {tarifa_seleccionada.tarifa} para {humedad_min} de humedad.')
        elif valor_medida >= humedad_max:
            tarifa_seleccionada = self.search([('humedad', '=', humedad_max)], limit=1)
            _logger.info(f'Valor de medida ({valor_medida}) es mayor que el máximo en la tabla. Tarifa seleccionada: {tarifa_seleccionada.tarifa} para {humedad_max} de humedad.')
        else:
            candidato_mas_cercano = min(candidatos.filtered(lambda x: x.humedad >= valor_medida), key=lambda x: x.humedad - valor_medida)
            tarifa_seleccionada = candidato_mas_cercano
            _logger.info(f'Valor de medida ({valor_medida}) dentro del rango. Tarifa seleccionada: {tarifa_seleccionada.tarifa} para {tarifa_seleccionada.humedad} de humedad.')
    
        # Asegurarse de que la tarifa sea float
        tarifa = float(tarifa_seleccionada.tarifa) if tarifa_seleccionada.tarifa else 0.0
        
        return tarifa

