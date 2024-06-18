from odoo import models, fields
import logging

_logger = logging.getLogger(__name__)

class DatosFlete(models.Model):
    _name = 'gms.datos_flete'
    _description = 'Datos de Flete'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    follower_ids = fields.Many2many('res.users', string='Followers')
    flete_km = fields.Float(string='Flete kilometros')
    tarifa = fields.Float(string='Tarifa', digits=(16, 4))  # 4 decimales
    tarifa_de_compra = fields.Float(string='Tarifa de Compra', digits=(16, 4))  # Nuevo campo

    def buscar_flete_cercano(self, kilometros_flete):
        candidatos = self.search([], order='flete_km')
        
        if not candidatos:
            _logger.warning('No hay datos de flete disponibles.')
            return 0
        
        # Obtener los kilómetros mínimos y máximos en la tabla
        km_min = min(candidatos.mapped('flete_km'))
        km_max = max(candidatos.mapped('flete_km'))

        # Selección de la tarifa
        if kilometros_flete <= km_min:
            tarifa_seleccionada = self.search([('flete_km', '=', km_min)], limit=1).tarifa
            _logger.info(f'Kilómetros ({kilometros_flete}) es menor que el mínimo en la tabla. Tarifa seleccionada: {tarifa_seleccionada} para {km_min} km.')
        elif kilometros_flete >= km_max:
            tarifa_seleccionada = self.search([('flete_km', '=', km_max)], limit=1).tarifa
            _logger.info(f'Kilómetros ({kilometros_flete}) es mayor que el máximo en la tabla. Tarifa seleccionada: {tarifa_seleccionada} para {km_max} km.')
        else:
            candidato_mas_cercano = min(candidatos.filtered(lambda x: x.flete_km >= kilometros_flete), key=lambda x: x.flete_km - kilometros_flete)
            tarifa_seleccionada = candidato_mas_cercano.tarifa
            _logger.info(f'Kilómetros ({kilometros_flete}) dentro del rango. Tarifa seleccionada: {tarifa_seleccionada} para {candidato_mas_cercano.flete_km} km.')

        return tarifa_seleccionada




    def buscar_tarifa_compra_cercana(self, kilometros_flete):
        candidatos = self.search([], order='flete_km')
        
        if not candidatos:
            _logger.warning('No hay datos de flete disponibles.')
            return 0
        
        # Obtener los kilómetros mínimos y máximos en la tabla
        km_min = min(candidatos.mapped('flete_km'))
        km_max = max(candidatos.mapped('flete_km'))

        # Selección de la tarifa de compra
        if kilometros_flete <= km_min:
            tarifa_seleccionada = self.search([('flete_km', '=', km_min)], limit=1).tarifa_de_compra
            _logger.info(f'Kilómetros ({kilometros_flete}) es menor que el mínimo en la tabla. Tarifa de compra seleccionada: {tarifa_seleccionada} para {km_min} km.')
        elif kilometros_flete >= km_max:
            tarifa_seleccionada = self.search([('flete_km', '=', km_max)], limit=1).tarifa_de_compra
            _logger.info(f'Kilómetros ({kilometros_flete}) es mayor que el máximo en la tabla. Tarifa de compra seleccionada: {tarifa_seleccionada} para {km_max} km.')
        else:
            candidato_mas_cercano = min(candidatos.filtered(lambda x: x.flete_km >= kilometros_flete), key=lambda x: x.flete_km - kilometros_flete)
            tarifa_seleccionada = candidato_mas_cercano.tarifa_de_compra
            _logger.info(f'Kilómetros ({kilometros_flete}) dentro del rango. Tarifa de compra seleccionada: {tarifa_seleccionada} para {candidato_mas_cercano.flete_km} km.')
            
        return tarifa_seleccionada
