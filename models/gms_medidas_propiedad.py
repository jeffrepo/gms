from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.tools import safe_eval
import logging
_logger = logging.getLogger(__name__)


class MedidaPropiedad(models.Model):
    _name = 'gms.medida.propiedad'
    _description = 'Medida de Propiedad'

    viaje_id = fields.Many2one('gms.viaje', string='Viaje', ondelete='cascade' , readonly=True, tracking="1")
    propiedad = fields.Many2one('gms.propiedades', string='Propiedad', domain="[('id', 'in', propiedades_disponibles_ids)]", tracking="1")

    valor_medida = fields.Float(string='Valor Medida (%)', digits=(6, 4))

    parametro = fields.Float(string='Parámetro', compute='_compute_parametro', digits=(6, 4), tracking="1")
    
    merma_kg = fields.Float(string='Merma (kg)' , readonly=True,  tracking="1")

  

    propiedades_disponibles_ids = fields.Many2many('gms.propiedades', compute='_compute_propiedades_disponibles', store=False,)

    @api.depends('viaje_id')
    def _compute_propiedades_disponibles(self):
        for record in self:
            if record.viaje_id and record.viaje_id.producto_transportado_id:
                producto = record.viaje_id.producto_transportado_id
                propiedades_lineas = producto.propiedades_ids
                propiedades_ids = propiedades_lineas.mapped('propiedades_id.id')
                record.propiedades_disponibles_ids = [(6, 0, propiedades_ids)]
            else:
                record.propiedades_disponibles_ids = [(6, 0, [])]




    @api.depends('valor_medida')
    def _compute_parametro(self):
        for record in self:
            record.parametro = record.valor_medida / 100


    @api.onchange('propiedad', 'viaje_id', 'valor_medida')
    def _onchange_calculate_merma(self):
        for record in self:
            _logger.info("Iniciando cálculo de merma...")
            _logger.info("Propiedad: %s", record.propiedad)
            _logger.info("Viaje ID: %s", record.viaje_id)

            if not (record.propiedad and record.viaje_id):
                continue  # Salta el cálculo si falta algún dato clave

            producto = record.viaje_id.producto_transportado_id
            _logger.info("Producto Transportado ID: %s", producto)

            # Obtener propiedad específica y valores adicionales
            propiedad_linea = producto.propiedades_ids.filtered(lambda p: p.propiedades_id == record.propiedad)
            valor_extra = propiedad_linea.mapped('valor_extra')[0] if propiedad_linea else 0
            umbral_tolerancia = propiedad_linea.mapped('umbral_tolerancia')[0] if propiedad_linea else 0

            _logger.info("Valor extra: %s", valor_extra)
            _logger.info("Umbral de Tolerancia: %s", umbral_tolerancia)

            parametro = record.parametro
            peso_neto = record.viaje_id.peso_neto
            valor_medida = record.valor_medida

            # Evaluación de la fórmula o cálculo directo
            if record.propiedad.formula:
                try:
                    localdict = {
                        'parametro': parametro,
                        'peso_neto': peso_neto,
                        'valor_medida': valor_medida,
                        'umbral_tolerancia': umbral_tolerancia,
                        'valor_extra': valor_extra,
                        'resultado': record.merma_kg  
                    }
                    _logger.info("Antes de evaluar la fórmula, localdict: %s", localdict)
                    
                    # Evaluar la fórmula
                    safe_eval.safe_eval(record.propiedad.formula, localdict, mode="exec", nocopy=True)
                    
                    _logger.info("Después de evaluar la fórmula, localdict: %s", localdict)
                    record.merma_kg = max(0, localdict.get('resultado', record.merma_kg))
                except Exception as e:
                    _logger.error("Error al evaluar la fórmula: %s", e)
            else:
                # Cálculo directo sin fórmula
                record.merma_kg = max(0, (peso_neto * parametro) / 100.0)

            _logger.info("Merma KG Calculada: %s", record.merma_kg)
             # Comprobación final para verificar si el registro sigue existiendo
            _logger.info("Registro después del cálculo de merma (ID: %s): %s", record.id, record.exists())


    @api.model
    def create(self, vals):
        if 'viaje_id' in vals and 'propiedad' in vals:
            existent_records = self.search([
                ('viaje_id', '=', vals['viaje_id']),
                ('propiedad', '=', vals['propiedad'])
            ])
            if existent_records:
                raise UserError("La propiedad seleccionada ya está asignada a este viaje. Por favor, seleccione una propiedad diferente.")
        return super(MedidaPropiedad, self).create(vals)

    def write(self, vals):
        if 'propiedad' in vals:
            for record in self:
                if record.viaje_id:
                    existent_records = self.search([
                        ('viaje_id', '=', record.viaje_id.id),
                        ('propiedad', '=', vals['propiedad']),
                        ('id', '!=', record.id)  # Excluir el registro actual de la búsqueda
                    ])
                    if existent_records:
                        raise UserError("La propiedad seleccionada ya está asignada a este viaje. Por favor, seleccione una propiedad diferente.")
        return super(MedidaPropiedad, self).write(vals)


