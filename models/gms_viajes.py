from odoo import models, fields, api, _
from odoo.exceptions import UserError
import datetime

class Viajes(models.Model):
    _name = 'gms.viaje'
    _description = 'Viaje'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    follower_ids = fields.Many2many('res.users', string='Followers')

    name = fields.Char(
    'Name', default=lambda self: _('New'),
    copy=False, readonly=True, tracking=True)

    agenda = fields.Many2one('gms.agenda', string='Agenda', tracking="1" )

    fecha_viaje = fields.Date(string='Fecha de viaje', tracking="1")

    origen = fields.Many2one('res.partner', 
                             string='Origen', 
                             tracking="1", 
                             domain="['&',('tipo', '!=', False),('parent_id','=',solicitante_id)]")
    
    destino = fields.Many2one('res.partner', string='Destino', tracking="1")

    camion_disponible_id = fields.Many2one('gms.camiones.disponibilidad', string='Camión Disponible', tracking="1")

    camion_id = fields.Many2one('gms.camiones', string='Camion', required=True , tracking="1")

    conductor_id = fields.Many2one('res.partner', string='Chofer', compute="_compute_conductor_transportista", tracking="1")

    solicitante_id = fields.Many2one('res.partner', string='Solicitante', tracking="1")
    
    # nuevos campos 
    tipo_viaje = fields.Selection([('entrada', 'Entrada'), ('salida', 'Salida')], string="Tipo de Viaje", tracking="1")

    numero_remito = fields.Char(string="Número de remito / Guía", tracking="1")
    
    transportista_id = fields.Many2one('res.partner', string="Transportista", compute="_compute_conductor_transportista", tracking="1")

    ruta_id = fields.Many2one('gms.rutas', 
                              string="Ruta", 
                              domain=lambda self: [('direccion_origen_id', '=', self.origen.id),('direccion_destino_id', '=', self.destino.id)]
                              , tracking="1")
     
    albaran_id = fields.Many2one('stock.picking', string="Albarán", tracking="1")

    producto_transportado_id = fields.Many2one('product.product', string="Producto transportado", tracking="1")

    peso_bruto = fields.Float(string="Peso bruto", tracking="1")

    tara = fields.Float(string="Tara", tracking="1")

    peso_neto = fields.Float(string="Peso neto", compute="_compute_peso_neto", tracking="1")
    


    peso_neto_destino = fields.Float(string="Peso neto destino", tracking="1")

    peso_producto_seco = fields.Float(string="Peso producto seco", tracking="1")

    porcentaje_humedad_primer_muestra = fields.Float(string="Porcentaje humedad primer muestra", tracking="1")

    tolva = fields.Char(string="Tolva", tracking="1")

    silo = fields.Char(string="Silo", tracking="1")

    prelimpieza_entrada = fields.Selection([('si', 'Si'), ('no', 'No')], string="Prelimpieza entrada", tracking="1")

    secado_entrada = fields.Selection([('si', 'Si'), ('no', 'No')], string="Secado entrada", tracking="1")

    kilometros_flete = fields.Float(string="Kilómetros flete", tracking="1")

    kilogramos_a_liquidar = fields.Float(string="Kilogramos a liquidar", tracking="1")

    pedido_venta_id = fields.Many2one('sale.order', string="Pedido de venta", tracking="1")

    pedido_compra_id = fields.Many2one('purchase.order', string="Pedido de compra", tracking="1")

    observaciones = fields.Text(string="Observaciones", tracking="1")

    albaran_count = fields.Integer(string="Número de Albaranes", compute="_compute_albaran_count")

    def _compute_albaran_count(self):
        for record in self:
            record.albaran_count = 1 if record.albaran_id else 0



    @api.onchange('camion_id')
    def _compute_conductor_transportista(self):
        for viaje in self:
            if viaje.camion_id:
                viaje.conductor_id = viaje.camion_id.conductor_id.id
                viaje.transportista_id = viaje.camion_id.transportista_id.id
                

    @api.depends('peso_bruto', 'tara')
    def _compute_peso_neto(self):
        for record in self:
            record.peso_neto = record.peso_bruto - record.tara



    @api.onchange('ruta_id')
    def _onchange_ruta_id(self):
         if self.ruta_id:   
             self.kilometros_flete = self.ruta_id.kilometros



    state = fields.Selection([
        ('cancelado', 'Cancelado'),
        ('borrador', 'Borrador'),
        ('coordinado', 'Coordinado'),
        ('proceso', 'Proceso'),
        ('terminado', 'Terminado'),
        ('liquidado', 'Liquidado')
    ], string='Estado', default='borrador', required=True)


    gastos_ids = fields.One2many('gms.gasto_viaje', 'viaje_id', string='Gastos')


    def action_proceso(self):
        self.write({'state': 'proceso'})


    def action_cancel(self):
        self.write({'state': 'cancelado'})

    def action_terminado(self):
        self.write({'state': 'terminado'})

        # Guarda la fecha y hora actual
        fecha_hora_actual = fields.Datetime.now()

        # Busca el registro en gms.historial que tenga la misma agenda_id que el nombre del viaje
        historial = self.env['gms.historial'].search([('agenda_id.name', '=', self.name)], limit=1)

        if historial:
            # Actualiza la fecha_hora_liberacion en el registro existente
            historial.write({'fecha_hora_liberacion': fecha_hora_actual})

        # Recupera el camión asociado a este viaje (si existe)
        camion_id = self.camion_disponible_id.camion_id.id if self.camion_disponible_id else False

         # Actualiza el estado del camión a 'disponible' si existe
        self.camion_disponible_id.estado = "disponible"
        self.camion_disponible_id.fecha_hora_liberacion = fecha_hora_actual
        

        # Crear albarán de salida o entrada basado en el tipo de viaje
        picking_type = False  

        if self.tipo_viaje == 'entrada':
            location_dest_id = self.destino.ubicacion_id.id
            picking_type = self.env['stock.picking.type'].search([('default_location_dest_id', '=', location_dest_id)], limit=1)
            location_src_id = picking_type.default_location_src_id.id if picking_type else False
        else:
            location_src_id = self.origen.ubicacion_id.id
            picking_type = self.env['stock.picking.type'].search([('default_location_src_id', '=', location_src_id)], limit=1)
            location_dest_id = picking_type.default_location_dest_id.id if picking_type else False

       
        if picking_type:
            # Crear el albarán
            picking_vals = {
                'picking_type_id': picking_type.id,
                'location_id': location_src_id,
                'location_dest_id': location_dest_id,
                'origin': self.name,
            }
            picking = self.env['stock.picking'].create(picking_vals)

            # Agregar las líneas al albarán
            picking.move_ids_without_package = [(0, 0, {
                'name': self.producto_transportado_id.name,
                'product_id': self.producto_transportado_id.id,
                'product_uom_qty': self.kilogramos_a_liquidar,
                'product_uom': self.producto_transportado_id.uom_id.id,
                'location_id': location_src_id,
                'location_dest_id': location_dest_id,
            })]

            
            self.albaran_id = picking
        else:
           
            raise UserError("No se encontró un tipo de operación adecuado para crear el albarán.")


   





                
    def action_liquidado(self):
        self.write({'state': 'liquidado'})  
        
    def action_coordinado(self):
        self.write({'state': 'coordinado'})

    def action_borrador(self):
        self.write({'state': 'borrador'})

    @api.model
    def create(self, vals):
        # Creación del registro
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('gms.viaje')
        record = super().create(vals)

        # Verificar si el registro fue creado desde una 'Agenda' y agregar mensaje al chatter
        if record.agenda:
            record.message_post(body="Este viaje fue creado desde una agenda.",subtype_xmlid="mail.mt_note")

        return record
       


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
            raise UserError(_('No hay un albarán asociado a este viaje.'))
    