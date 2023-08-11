from odoo import models, fields, api
import random


class Agenda(models.Model):
    _name = 'gms.agenda'
    _description = 'Agenda'

    name = fields.Char(string="Booking",required=True, readonly=True, copy=False, default=lambda self: self.env['ir.sequence'].next_by_code('gms.agenda'))
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

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                random_number = str(random.randint(100, 999))
                vals['name'] = f'booking{random_number}'
        return super().create(vals_list)
    
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
            'fecha_viaje': self.fecha_viaje,
            'origen': self.origen,
            'destino': self.destino,
        })
        # Actualizar el estado de la Agenda para indicar que se ha convertido en un Viaje
        self.write({'state': 'agendado'})