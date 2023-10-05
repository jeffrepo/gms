from odoo import fields, models, api

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
    ], string='Tipo')



    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        # Agregar el dominio para filtrar por transportista=True
        args += [('transportista', '=', True)]
        return super(ResPartner, self).search(args, offset, limit, order, count)