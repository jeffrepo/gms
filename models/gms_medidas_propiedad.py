from odoo import models, fields, api, _

class MedidaPropiedad(models.Model):
    _name = 'gms.medida.propiedad'
    _description = 'Medida de Propiedad'

    viaje_id = fields.Many2one('gms.viaje', string='Viaje', ondelete='cascade')
    propiedad = fields.Many2one('gms.propiedades', string='Propiedad')
    valor_medida = fields.Float(string='Valor Medida (%)')
    parametro = fields.Float(string='Parámetro')
    merma_kg = fields.Float(string='Merma (kg)')
    formula_dentro_del_producto = fields.Text(string='Fórmula dentro del Producto')
    producto_id = fields.Many2one('product.product', string='Producto')