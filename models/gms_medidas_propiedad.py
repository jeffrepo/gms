from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.tools import safe_eval
import logging
_logger = logging.getLogger(__name__)


class MedidaPropiedad(models.Model):
    _name = 'gms.medida.propiedad'
    _description = 'Medida de Propiedad'

    viaje_id = fields.Many2one('gms.viaje', string='Viaje', ondelete='cascade')
    propiedad = fields.Many2one('gms.propiedades', string='Propiedad')
    valor_medida = fields.Float(string='Valor Medida (%)')
    parametro = fields.Float(string='Parámetro', compute='_compute_parametro')
    merma_kg = fields.Float(string='Merma (kg)')
   

    @api.depends('valor_medida')
    def _compute_parametro(self):
        for record in self:
            record.parametro = record.valor_medida / 100


    @api.onchange('propiedad', 'viaje_id')
    def _onchange_calculate_merma(self):
        for record in self:
            _logger.info("Iniciando cálculo de merma...")
            _logger.info("Propiedad: %s", record.propiedad)
            _logger.info("Viaje ID: %s", record.viaje_id)
            
            if record.propiedad and record.viaje_id:
                producto = record.viaje_id.producto_transportado_id
                _logger.info("Producto Transportado ID: %s", producto)
                
                if producto and producto.propiedades_ids:
                    propiedad_linea = producto.propiedades_ids.filtered(
                        lambda p: p.propiedades_id == record.propiedad
                    )
                    _logger.info("Propiedad Filtrada: %s", propiedad_linea)
                    
                    if propiedad_linea:
                        parametro = record.parametro  
                        _logger.info("Parámetro: %s", parametro)
                        peso_neto = record.viaje_id.peso_neto
                        _logger.info("Peso Neto: %s", peso_neto)
                        
                        # Si la propiedad tiene una fórmula, evaluarla
                        if record.propiedad.formula:
                            localdict = {
                                'parametro': parametro,
                                'peso_neto': peso_neto,
                                'resultado': record.merma_kg  # Aquí cambiamos la clave a 'resultado'
                            }
                            safe_eval.safe_eval(record.propiedad.formula, localdict, mode="exec", nocopy=True)
                            record.merma_kg = localdict.get('resultado', record.merma_kg)  # Aquí también cambiamos la clave a 'resultado'
                        else:
                            record.merma_kg = (peso_neto * parametro) / 100.0
                        _logger.info("Merma KG Calculada: %s", record.merma_kg)
