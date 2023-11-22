from odoo import models, fields, api
from odoo.exceptions import UserError

class CamionSeleccionAsistente(models.TransientModel):
    _name = 'gms.camion.seleccion.asistente'
    _description = 'Asistente para Seleccionar Camión Disponible'

    camion_disponible_id = fields.Many2one(
        'gms.camiones.disponibilidad', 
        string='Seleccionar Camión', 
        domain=[('estado', '=', 'disponible')],
        required=True
    )

    albaran_id = fields.Many2one('stock.picking', string='Albarán')

    def confirmar_seleccion(self):
        if not self.camion_disponible_id or not self.albaran_id:
            raise UserError("Es necesario seleccionar un camión y tener un albarán asociado.")


        producto_transportado = False
        if self.albaran_id.move_ids_without_package:
            producto_transportado = self.albaran_id.move_ids_without_package[0].product_id.id

        # Crear el viaje
        viaje_vals = {
            'albaran_id': self.albaran_id.id,
            'camion_disponible_id': self.camion_disponible_id.id,
            'camion_id': self.camion_disponible_id.camion_id.id,
            'conductor_id': self.camion_disponible_id.conductor_id.id,
            'solicitante_id': self.albaran_id.partner_id.id,
            'origen': self.albaran_id.picking_type_id.warehouse_id.partner_id.id,
            'destino': self.albaran_id.partner_id.id,
            'tipo_viaje': 'entrada' if self.albaran_id.picking_type_id.code == 'incoming' else 'salida',
            'producto_transportado_id': producto_transportado,
            'fecha_viaje': fields.Date.context_today(self),
            'arribo': fields.Datetime.now(),
            
        }
        self.env['gms.viaje'].create(viaje_vals)

        # Cambiar el estado del camión a "ocupado"
        self.camion_disponible_id.write({'estado': 'ocupado'})

        return {
            'type': 'ir.actions.act_window_close'
        }