from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime, timedelta

class Agenda(models.Model):
    _name = 'gms.agenda'
    _description = 'Agenda'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = "name"
    name = fields.Char(
    'Name', )


    name = fields.Char(required=True, default=lambda self: _('New'), copy=False, readonly=True, tracking=True)

    fecha = fields.Date(string='Fecha', required=True, tracking="1", default=fields.Date.today())

    fecha_viaje = fields.Date(string='Fecha de viaje', required=True, tracking="1")

    origen = fields.Many2one('res.partner', 
                             string='Origen', 
                             required=True, 
                             tracking="1", 
                             domain="['&',('tipo', '!=', False),('parent_id','=',solicitante_id)]", 
                             ondelete='cascade',context="{'default_parent_id': solicitante_id}") 
    

    destino = fields.Many2one('res.partner', 
                              string='Destino', 
                              required=True, 
                              tracking="1", 
                              domain="[('tipo', '!=', False)]")
    
    transportista_id = fields.Many2one('res.partner', 
                                       string='Trasportista', 
                                       readonly=True, 
                                       states={'cancelado': [('readonly', True)]}, 
                                       tracking="1")
    
    camion_disponible_id = fields.Many2one('gms.camiones.disponibilidad',
                                           string='Disponibilidad Camión',
                                           states={'cancelado': [('readonly', True)]},
                                           tracking="1",
                                           domain="[('estado', '=', 'disponible'), ('camion_id.disponible_zafra', '=', True)]",
                                           attrs="{'invisible': [('state', '=', 'solicitud')]}")  
    

    camion_id = fields.Many2one('gms.camiones', string='Camion', readonly=True , tracking="1")

    conductor_id = fields.Many2one('res.partner', string='Chofer', readonly=True, tracking="1")

    solicitante_id = fields.Many2one('res.partner', 
                                     string='Solicitante', 
                                     required=True, 
                                     tracking="1", 
                                     domain="[('tipo', '!=', 'chacras'), ('tipo', '!=', 'planta'), ('tipo', '=', False)]")

    viaje_count = fields.Integer(string="Número de viajes", compute="_compute_viaje_count", tracking="1")

    picking_id = fields.Many2one('stock.picking', string='Stock Picking', required=True, readonly=True)

    tipo_viaje = fields.Selection([('entrada', 'Entrada'), ('salida', 'Salida')], string="Tipo de Viaje", tracking="1")

    albaran_id = fields.Many2one('stock.picking', string="Albarán", compute="_compute_albaran", store=True, readonly=True)

    order_id = fields.Many2one('purchase.order', string='Orden de Compra')

    @api.depends('name')
    def _compute_albaran(self):
        for record in self:
            viaje = self.env['gms.viaje'].search([('agenda', '=', record.id)], limit=1)
            if viaje:
                record.albaran_id = viaje.albaran_id


    


    @api.depends('name') 
    def _compute_viaje_count(self):
        for record in self:
            record.viaje_count = self.env['gms.viaje'].search_count([('agenda', '=', record.id)])



    state = fields.Selection([
        ('solicitud', 'Solicitud'),
        ('proceso', 'Proceso'),
        ('confirmado', 'Confirmado'),
        ('cancelado', 'Cancelado')
    ], string='Estado', default='solicitud', required=True)

    follower_ids = fields.Many2many('res.users', string='Followers')

    @api.onchange('camion_disponible_id')
    def _onchange_camion_disponible_id(self):
        if self.camion_disponible_id:
            self.transportista_id = self.camion_disponible_id.transportista_id.id
            self.conductor_id = self.camion_disponible_id.conductor_id.id
            self.camion_id = self.camion_disponible_id.camion_id.id
            

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('gms.agenda')
        return super().create(vals_list)

    def action_cancel(self):
        self.write({'state': 'cancelado'})

    def action_proceso(self):
        self.write({'state': 'proceso'})

    def action_view_scheduled_trips(self):
        self.ensure_one()  # Asegura que solo se está trabajando con un registro a la vez
        viaje = self.env['gms.viaje'].search([('agenda', '=', self.id)], limit=1)
        if viaje:
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'gms.viaje',
                'view_mode': 'form',
                'res_id': viaje.id,
                'target': 'current',
            }
        else:
            raise UserError('No hay un viaje asociado a esta agenda.')

    def _check_fecha_viaje(self):
        for agenda in self:
            if agenda.fecha_viaje:
                fecha_viaje = fields.Date.from_string(agenda.fecha_viaje)
                fecha_actual = fields.Date.from_string(fields.Date.today())
                dias_diferencia = (fecha_viaje - fecha_actual).days
                if dias_diferencia > 1:
                    raise UserError("No se puede confirmar: La fecha de viaje es mayor a 1 día desde la fecha actual.")

    def action_confirm(self):
       
        self._check_fecha_viaje()
        
        if self.camion_disponible_id:
            self.camion_disponible_id.write({'estado': 'ocupado'})

        # Determinando el pedido de compra relacionado con el stock.picking
        purchase_orders = self.env['purchase.order'].search([('name', '=', self.picking_id.origin)], limit=1)
        purchase_order_id = purchase_orders.id if purchase_orders else False

        # Determinando el producto transportado
        if purchase_order_id:
        # Si es una orden de compra
            producto_transportado_id = purchase_orders.order_line[0].product_id.id if purchase_orders.order_line else False
            cantidad = purchase_orders.order_line[0].product_qty if purchase_orders.order_line else 0.0

        else:
            # Si es una transferencia de stock
            producto_transportado_id = self.picking_id.move_line_ids_without_package[0].product_id.id if self.picking_id.move_line_ids_without_package else False
            cantidad = self.picking_id.move_line_ids_without_package[0].product_uom_qty if self.picking_id.move_line_ids_without_package else 0.0


        viaje = self.env['gms.viaje'].create({
            'agenda': self.id,
            'fecha_viaje': self.fecha_viaje,
            'origen': self.origen.id,
            'destino': self.destino.id,
            'camion_disponible_id': self.camion_disponible_id.id,
            'camion_id': self.camion_disponible_id.camion_id.id,  
            'conductor_id': self.camion_disponible_id.conductor_id.id,
            'solicitante_id': self.solicitante_id.id,
            'tipo_viaje': self.tipo_viaje,
            'transportista_id': self.transportista_id.id,    
            'state': 'proceso',
            'pedido_venta_id': self.picking_id.sale_id.id,
            'pedido_compra_id': purchase_order_id,
            'producto_transportado_id': producto_transportado_id,
            'albaran_id': self.picking_id.id,
            'kilogramos_a_liquidar':cantidad 
            
            
            
            
        })

        if self.camion_disponible_id:
            self.env['gms.historial'].create({
                'fecha': self.fecha,
                'camion_id': self.camion_disponible_id.camion_id.id,
                'agenda_id': self.id,
            })

        self.write({'state': 'confirmado'})



    def unlink(self):
        for record in self:
            if record.state in ['proceso', 'confirmado', 'cancelado']:
                raise UserError(_('No puedes eliminar una agenda en el estado %s.') % record.state)
        return super(Agenda, self).unlink()
    

    @api.onchange('origen', 'destino')
    def _check_origen_destino(self):
        if self.origen and self.destino and self.origen == self.destino:
            raise UserError("Origen y Destino no pueden ser iguales.")
        


    #ver albaran asociado 
    def action_view_picking(self):
        self.ensure_one()
        if self.albaran_id:
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'stock.picking',
                'view_mode': 'form',
                'res_id': self.albaran_id.id,
                'target': 'current',
            }
        else:
            raise UserError(_('No hay un albarán asociado a esta agenda.'))
        