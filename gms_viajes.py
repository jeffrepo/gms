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

    agenda_count = fields.Integer(string="Número de Agendas", compute="_compute_agenda_count")

    @api.depends('agenda')
    def _compute_agenda_count(self):
        for record in self:
            record.agenda_count = 1 if record.agenda else 0

    def action_view_agenda(self):
        self.ensure_one() 
        if self.agenda:
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'gms.agenda',
                'view_mode': 'form',
                'res_id': self.agenda.id,
                'target': 'current',
            }
        else:
            raise UserError('No hay una agenda asociada a este viaje.')

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
                          domain="[('direccion_origen_id', '=', origen),('direccion_destino_id', '=', destino)]",
                          tracking="1")

    albaran_id = fields.Many2one('stock.picking', string="Albarán", tracking="1")

    producto_transportado_id = fields.Many2one('product.product', string="Producto transportado", tracking="1")

    peso_bruto = fields.Float(string="Peso bruto", tracking="1")

    tara = fields.Float(string="Tara", tracking="1")

    peso_neto = fields.Float(string="Peso neto", compute="_compute_peso_neto", tracking="1")
    


    peso_neto_destino = fields.Float(string="Peso neto destino", tracking="1")

    peso_producto_seco = fields.Float(string="Peso producto seco", tracking="1")

    porcentaje_humedad_primer_muestra = fields.Float(string="Porcentaje humedad primer muestra", tracking="1")

    tolva = fields.Char(string="Tolva", tracking="1")

    silo_id = fields.Many2one('stock.location', string="Silio", domain=[('usage', '=', 'internal')], tracking="1")

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
        

        # Buscar la ubicación 'Partners/Vendors'
        location_supplier_id = self.env['stock.location'].search([('usage', '=', 'supplier')], limit=1).id

        # Buscar la ubicación 'Partners/Customers'
        location_customer_id = self.env['stock.location'].search([('usage', '=', 'customer')], limit=1).id

        if not location_supplier_id or not location_customer_id:
            raise UserError("No se encontraron las ubicaciones necesarias para crear el albarán.")

        if self.tipo_viaje == 'entrada':
            location_id = location_supplier_id
            location_dest_id = self.silo_id.id  
            owner = self.solicitante_id

            # Buscar el tipo de operación "recepción" con el silo correspondiente
            picking_type = self.env['stock.picking.type'].search([
                ('code', '=', 'incoming'),
                ('default_location_dest_id', '=', self.silo_id.id)
            ], limit=1)
        else:  # salida
            location_id = self.silo_id.id
            location_dest_id = location_customer_id

            # Buscar el tipo de operación "entrega" con el silo correspondiente
            picking_type = self.env['stock.picking.type'].search([
                ('code', '=', 'outgoing'),
                ('default_location_src_id', '=', self.silo_id.id)
            ], limit=1)

        if not picking_type:
            raise UserError("No se encontró el tipo de operación necesario para crear el albarán.")

        # Crear el albarán
        picking_vals = {
            'location_id': location_id,
            'location_dest_id': location_dest_id,
            'origin': self.name,
            'picking_type_id': picking_type.id,
            'owner_id': owner.id if self.tipo_viaje == 'entrada' else False
        }   

        picking = self.env['stock.picking'].create(picking_vals)

        # Agregar las líneas al albarán
        picking.move_ids_without_package = [(0, 0, {
            'name': self.producto_transportado_id.name,
            'product_id': self.producto_transportado_id.id,
            'product_uom_qty': self.kilogramos_a_liquidar,
            'product_uom': self.producto_transportado_id.uom_id.id,
            'location_id': location_id,
            'location_dest_id': location_dest_id,
        })]

        self.albaran_id = picking

   





                
    def action_liquidado(self):
        self.write({'state': 'liquidado'})  
        
    def action_coordinado(self):
        self.write({'state': 'coordinado'})

    def action_borrador(self):
        self.write({'state': 'borrador'})

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('gms.viaje')
        record = super().create(vals)

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
    