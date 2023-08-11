from odoo import models, fields, api
import random


class Agenda(models.Model):
    _name = 'gms.agenda'
    _description = 'Agenda'

    name = fields.Char(required=True, readonly=True, copy=False, default=lambda self: 'booking' + str(random.randint(100, 999)))
    fecha = fields.Date(string='Fecha', required=True)
    fecha_viaje = fields.Date(string='Fecha de viaje', required=True)
    origen = fields.Char(string='Origen', required=True)
    destino = fields.Char(string='Destino', required=True)
    #venta_id = fields.Many2one('sale.order', string='Venta', required=True)
    state = fields.Selection([
        ('solicitud', 'Solicitud'),
        ('agendado', 'Agendado'),
        ('cancelado', 'Cancelado')
    ], string='Estado', default='solicitud', required=True)


    def action_agendar(self):
        self.write({'state': 'agendado'})

  
    def action_cancelar(self):
        self.write({'state': 'cancelado'})



class Viajes(models.Model):
    _inherit = 'gms.agenda'

    def action_agendar(self):
        super(Viajes, self).action_agendar()
        # Crear un nuevo Viaje (gms.viaje) al agendar la Agenda
        viaje = self.env['gms.viaje'].create({
            'name': self.name,
            'fecha_viaje': self.fecha_viaje
            #agregar los campos que tambien van a ir en viajes
        })
        # Actualizar el estado de la Agenda para indicar que se ha convertido en un Viaje
        self.write({'state': 'agendado'})