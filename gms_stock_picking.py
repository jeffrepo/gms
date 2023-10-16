from odoo import models, fields, api

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    agenda_ids = fields.One2many('gms.agenda', 'picking_id', string='Agendas')
    agenda_count = fields.Integer(string='Agenda Count', compute='_compute_agenda_count')

    
    @api.depends('agenda_ids')
    def _compute_agenda_count(self):
        for picking in self:
            picking.agenda_count = len(picking.agenda_ids)

   
    def button_schedule_trip(self):
     
        agenda_vals = {
            'fecha': fields.Date.today(),
            'fecha_viaje': fields.Date.today(),
            'solicitante_id': self.partner_id.id,
            'origen': self.picking_type_id.warehouse_id.partner_id.id,
            'destino': self.partner_shipping_id.id,
        }
        agenda = self.env['gms.agenda'].create(agenda_vals)
        return True

    
    def action_view_agenda(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Agendas',
            'res_model': 'gms.agenda',
            'view_mode': 'tree,form',
            'domain': [('picking_id', '=', self.id)],
        }
