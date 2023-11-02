from odoo import fields, models, api
from odoo.exceptions import UserError

class ResPartner(models.Model):
    _inherit = 'res.partner'

    transportista = fields.Boolean(string='Transportista', tracking="1")
    camiones_ids = fields.One2many(
        'gms.camiones', 
        'transportista_id', 
        string='Camiones', 
        tracking="1", 
        domain=[('transportista_id', '=', False)]
    )
    tipo = fields.Selection([
        ('chacra', 'Chacra'),
        ('planta', 'Planta'),
        ('deposito', 'Deposito'),
    ], string='Tipo')

    ubicacion_id = fields.Many2one('stock.location', string="Ubicación")

 
   

    def unlink(self):
        for record in self:
            
          #agendas buscar conductores y camiones para que no puedan ser eliminados
            agendas_as_conductor = self.env['gms.agenda'].search([('conductor_id', '=', record.id)])
            if agendas_as_conductor:
                raise UserError("No se puede eliminar el chofer porque está asociado a una o más agendas.")
            
            agendas_as_camion = self.env['gms.agenda'].search([('camion_id', '=', record.id)])
            if agendas_as_camion:
                raise UserError("No se puede eliminar el camión porque está asociado a una o más agendas.")

            #viajes buscar conductores y camiones para que no puedan ser eliminados
            viajes_as_conductor = self.env['gms.viajes'].search([('conductor_id', '=', record.id)])
            if viajes_as_conductor:
                raise UserError("No se puede eliminar el chofer  porque está asociado a uno o más viajes.")
            
           
            viajes_as_camion = self.env['gms.viajes'].search([('camion_id', '=', record.id)])
            if viajes_as_camion:
                raise UserError("No se puede eliminar el camión porque está asociado a uno o más viajes.")

        return super(ResPartner, self).unlink()