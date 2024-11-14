from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging


_logger = logging.getLogger(__name__)


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

    contacto_id = fields.Many2one(
        'res.partner',
        string='Contacto Auxiliar'
    )

    origen = fields.Many2one('res.partner',
                             string='Origen',
                             tracking="1",
                            domain="[('tipo', 'in', ['planta', 'chacra', 'puerto']), ('parent_id', '=', contacto_id)]"
    )

    destino = fields.Many2one('res.partner', string='Destino', tracking="1")

    camion_disponible_id = fields.Many2one('gms.camiones.disponibilidad', string='Camión Disponible', tracking="1")

    camion_id = fields.Many2one('gms.camiones', string='Camion', tracking="1")

    conductor_id = fields.Many2one('res.partner', string='Chofer', compute="_compute_conductor_transportista", tracking="1")

    solicitante_id = fields.Many2one('res.partner', string='Solicitante', tracking="1",
                                 domain="[('tipo', 'not in', ['chacra', 'planta'])]")

    # nuevos campos
    tipo_viaje = fields.Selection([('entrada', 'Entrada'), ('salida', 'Salida')], string="Tipo de Viaje", tracking="1")

    numero_remito = fields.Char(string="Número de remito / Guía", tracking="1")
    
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)

    transportista_id = fields.Many2one('res.partner', string="Transportista", compute="_compute_conductor_transportista", tracking="1", store = True)

    ruta_id = fields.Many2one('gms.rutas',
                          string="Ruta",
                          domain="[('direccion_origen_id', '=', origen),('direccion_destino_id', '=', destino)]",
                          tracking="1")






    albaran_id = fields.Many2one('stock.picking', string="Albarán", tracking="1")

    producto_transportado_id = fields.Many2one('product.product', string="Producto transportado", readonly=True, tracking="1")

    peso_bruto = fields.Float(string="Peso bruto", tracking="1")

    tara = fields.Float(string="Tara", tracking="1")

    peso_neto = fields.Float(string="Peso neto", readonly=True, compute="_compute_peso_neto", tracking="1",store=True)

    estado = fields.Char(string = "s" , tracking=True)

    peso_neto_destino = fields.Float(string="Peso neto destino", tracking="1")

    peso_producto_seco = fields.Float(string="Peso producto seco", tracking="1" , readonly=True)

    porcentaje_humedad_primer_muestra = fields.Float(string="Porcentaje humedad primer muestra", tracking="1")

    tolva_id = fields.Many2one('gms.tolva', string='Tolva', tracking="1")

    silo_id = fields.Many2one('stock.location', string="Silio", domain=[('usage', '=', 'internal')], tracking="1")

    prelimpieza_entrada = fields.Boolean(string="Prelimpieza Entrada", tracking=True)
    secado_entrada = fields.Boolean(string="Secado Entrada", tracking=True)

    kilometros_flete = fields.Float(string="Kilómetros flete", tracking="1", store=True, compute='_compute_kilometros_flete')

    kilogramos_a_liquidar = fields.Float(compute='_compute_kilogramos_a_liquidar', readonly=True, store=True, tracking=True)

    pedido_venta_id = fields.Many2one('sale.order', string="Pedido de venta", tracking="1", readonly=True)

    pedido_compra_id = fields.Many2one('purchase.order', string="Pedido de compra", tracking="1", readonly=True)

    observaciones = fields.Text(string="Observaciones", tracking="1")

    albaran_count = fields.Integer(string="Número de Albaranes", compute="_compute_albaran_count" , tracking=True)

    albaran_id = fields.Many2one('stock.picking', string="Albarán" , tracking=True)



    medidas_propiedades_ids = fields.One2many('gms.medida.propiedad', 'viaje_id', string='Medidas de Propiedades',states = {
    'cancelado': [('readonly', True), ('required', False)],
    'liquidado': [('readonly', False), ('required', True)]
}, tracking="1")

    arribo = fields.Datetime(string="Arribo", states = {
    'cancelado': [('readonly', True), ('required', False)],
    'liquidado': [('readonly', False), ('required', True)]
},
 tracking=True)


    partida = fields.Datetime(string="Partida", tracking=True)

    chacra = fields.Char(string='Chacra', tracking="1")
    remito = fields.Char(string='Remito',states = {
    'cancelado': [('readonly', True), ('required', False)],
    'liquidado': [('readonly', False), ('required', False)]

}, tracking="1")

    firma = fields.Binary(string='Firma', tracking="1")

    sale_order_id = fields.Many2one('sale.order', string='Orden de Venta' , tracking=True)

    purchase_order_id = fields.Many2one('purchase.order', string='Orden de Compra' , tracking=True)

    sale_order_id = fields.Many2one('sale.order', string='Órdenes de Venta', tracking=True)

    purchase_order_ids = fields.Many2many('purchase.order', string='Orden de Compra' , tracking=True)

    sale_order_ids = fields.Many2many('sale.order', string='Órdenes de Venta', tracking=True)


    balanza_id = fields.Many2one('gms.balanza', string='Balanza' , tracking=True)

    humedad = fields.Float(string='Humedad' , tracking=True)

    ph = fields.Float(string='PH' , tracking=True)

    proteina = fields.Float(string='Proteína'  , tracking=True)

    factura_id = fields.Many2one('account.move', string='Factura Asociada')

    picking_id = fields.Many2one('stock.picking', string='Albarán')

    creado_desde_albaran = fields.Boolean(string='Creado desde Albarán', default=False)

    mensaje_enviado = fields.Boolean(string='Mensaje Enviado', default=False)

    # prelimpieza_entrada_1 = fields.Selection([('si', 'Si'), ('no', 'No')], string="Prelimpieza entrada", tracking="1")

    # secado_entrada_1 = fields.Selection([('si', 'Si'), ('no', 'No')], string="Secado entrada", tracking="1")

    user_id = fields.Many2one('res.users', string='Usuario')

    kg_pendiente_liquidar = fields.Float(
        string='Kg Pendiente de Liquidar',
        store=True
    )


    

    def _compute_albaran_count(self):
        for record in self:
            record.albaran_count = 1 if record.albaran_id else 0



    @api.onchange('camion_id')
    def _compute_conductor_transportista(self):
        for viaje in self:
            if viaje.camion_id:
                viaje.conductor_id = viaje.camion_id.conductor_id.id
                viaje.transportista_id = viaje.camion_id.transportista_id.id
            else:
                # Limpia los campos si no hay camion_id
                viaje.conductor_id = None
                viaje.transportista_id = None



    @api.depends('peso_bruto', 'tara')
    def _compute_peso_neto(self):
        for record in self:
            record.peso_neto = record.peso_bruto - record.tara


    @api.depends('ruta_id')
    def _compute_kilometros_flete(self):
        for viaje in self:
            if viaje.ruta_id:
                viaje.kilometros_flete = viaje.ruta_id.kilometros

    @api.depends('ruta_id.kilometros')
    def _compute_kilometros_flete(self):
        for viaje in self:
            if viaje.ruta_id:
                viaje.kilometros_flete = viaje.ruta_id.kilometros



    @api.onchange('ruta_id')
    def _onchange_ruta_id(self):
        for viaje in self:

            if viaje.ruta_id:
                # Lógica para determinar y asignar el gasto del viaje
                viaje.determinar_y_asignar_gasto_viaje()

                # Asignar kilómetros de flete basados en la ruta seleccionada
                # viaje.kilometros_flete = viaje.ruta_id.kilometros

                # Eliminar gastos relacionados con la ruta anterior
                gastos_a_eliminar = viaje.gastos_ids.filtered(lambda g: g.es_de_ruta)
                viaje.gastos_ids -= gastos_a_eliminar




    state = fields.Selection([
        ('cancelado', 'Cancelado'),
        ('coordinado', 'Coordinado'),
        ('proceso', 'Proceso'),
        ('terminado', 'Terminado'),
        ('pendiente_liquidar', 'Parcialmente Liquidado'),
        ('liquidado', 'Liquidado')
    ], string='Estado', default='coordinado', required=True)


    gastos_ids = fields.One2many('gms.gasto_viaje', 'viaje_id', string='Gastos' , tracking=True)

    def action_pendiente_liquidar(self):
        self.write({'state': 'pendiente_liquidar'})
        
    def action_proceso(self):
        self._actualizar_kilogramos_a_liquidar()
        # Buscar y eliminar solo los gastos de viaje con valor 0
        gastos_viaje = self.env['gms.gasto_viaje'].search([
            ('viaje_id', '=', self.id),
            ('precio_total', '=', 0)
        ])
        gastos_viaje.unlink()  # Esto eliminará solo los gastos con valor 0
    
        self.actualizar_ubicacion_destino()
    
        self.write({'state': 'proceso'})



    def action_cancel(self):
        self.write({'state': 'cancelado'})

        if self.camion_disponible_id:
            self.camion_disponible_id.write({'estado': 'disponible'})

        return True

    def action_terminado(self):
        #self.determinar_y_asignar_gasto_viaje()
        logging.warning("ejecutando accion terminado")
        self._compute_kilogramos_a_liquidar()  
        self._actualizar_kilogramos_a_liquidar()
        logging.warning("kg a liquidar",self.kilogramos_a_liquidar)
        self.write({'state': 'terminado'})
        self.actualizar_ubicacion_destino()
        fecha_hora_actual = fields.Datetime.now()
        historial = self.env['gms.historial'].search([('agenda_id.name', '=', self.name)], limit=1)
    
        if historial:
            historial.write({'fecha_hora_liberacion': fecha_hora_actual})
    
        if self.camion_disponible_id:
            self.camion_disponible_id.estado = "disponible"
            self.camion_disponible_id.fecha_hora_liberacion = fecha_hora_actual
    
        medida_obj = self.env['gms.medida.propiedad']
        medidas = medida_obj.search([('viaje_id', '=', self.id)])
        for medida in medidas:
            medida._onchange_calculate_merma()
    
        self.partida = fecha_hora_actual
    
        if self.tipo_viaje == 'entrada':
            self.enviar_sms_solicitante()
    
        if self.tipo_viaje in ['entrada', 'salida']:
            #config = self.env['res.config.settings'].default_get([])
            # config = self.env['ir.config_parameter'].sudo().get_param('gms.track_draft_orders'))

            producto_secado_id = self.env['ir.config_parameter'].sudo().get_param('gms.producto_secado_id')
            producto_pre_limpieza_id =  self.env['ir.config_parameter'].sudo().get_param('gms.producto_pre_limpieza_id')
            producto_flete_puerto_id = self.env['ir.config_parameter'].sudo().get_param('gms.producto_flete_puerto_id')
            gasto_viaje_con_impuesto_id = self.env['ir.config_parameter'].sudo().get_param('gms.gasto_viaje_con_impuesto_id')
    
            moneda_proveedor_id = self.transportista_id.property_purchase_currency_id.id
    
            valor_medida = sum(medida.valor_medida for medida in self.medidas_propiedades_ids)
    
            tarifa_humedad = self.env['gms.datos_humedad'].buscar_humedad_cercana(valor_medida)
            _logger.info(f'Valor medida: {valor_medida}, Tarifa humedad: {tarifa_humedad}')
        
            if not isinstance(tarifa_humedad, (int, float)):
                _logger.error(f'Tarifa humedad no es un número: {tarifa_humedad}')
                tarifa_humedad = 0.0
        
            precio_total_secado = (valor_medida * tarifa_humedad) / 1000
            _logger.info(f'Precio total del secado calculado: {precio_total_secado}')

            producto_pre_limpieza = self.env['product.product'].search([("id", "=", producto_pre_limpieza_id)])
            precio_total_pre_limpieza = self.peso_neto * producto_pre_limpieza.lst_price if producto_pre_limpieza else 0
    
            kilometros_flete = self.kilometros_flete
            config_params = self.env['ir.config_parameter'].sudo()
            cantidad_kilos_flete_puerto = float(config_params.get_param('gms.cantidad_kilos_flete_puerto', 0.0))
    
            tarifa_flete = self.env['gms.datos_flete'].buscar_flete_cercano(kilometros_flete)
            precio_total_flete_puerto = cantidad_kilos_flete_puerto * self.kilogramos_a_liquidar
            precio_total_flete = self.peso_neto * tarifa_flete
    
            _logger.info(f'Precio total calculado para Flete: {precio_total_flete}')

            self._actualizar_o_crear_gasto('Secado', producto_secado_id, precio_total_secado, moneda_proveedor_id)
            self._actualizar_o_crear_gasto('Pre Limpieza', producto_pre_limpieza_id, precio_total_pre_limpieza, moneda_proveedor_id)
            self._actualizar_o_crear_gasto('Flete Puerto', producto_flete_puerto_id, precio_total_flete_puerto, moneda_proveedor_id)
    
            if self.agenda:
                _logger.info(f'El viaje {self.name} tiene agenda asociada. Creando/actualizando gasto de Flete.')
                self._crear_o_actualizar_gasto_flete('Flete', gasto_viaje_con_impuesto_id, precio_total_flete, moneda_proveedor_id, estado_compra='no_comprado')
               
            else:
                _logger.info(f'El viaje {self.name} no está asociado a ninguna agenda. No se creó ni actualizó el gasto de Flete.')

    
    def _actualizar_o_crear_gasto(self, name, producto_id, precio_total, moneda_proveedor_id, estado_compra='no_aplica'):
        if producto_id:
            gasto_viaje = self.env['gms.gasto_viaje'].search([
                ('viaje_id', '=', self.id),
                ('name', '=', name)
            ], limit=1)
        
            
            if gasto_viaje:
                if gasto_viaje.estado_compra in ['comprado']:
                    _logger.info(f'El gasto "{name}" no se actualizará porque ya tiene una orden de compra asociada.')
                    # Aquí omitimos la actualización y simplemente continuamos
                    return
                
                _logger.info(f'Actualizando gasto existente: {name}, Precio total: {precio_total}')
                gasto_viaje.write({
                    'precio_total': precio_total,
                    'moneda_id': moneda_proveedor_id
                })
            else:
                _logger.info(f'Creando nuevo gasto: {name}, Precio total: {precio_total}, Estado compra: {estado_compra}')
                new_gasto = self.env['gms.gasto_viaje'].create({
                    'name': name,
                    'producto_id': producto_id,
                    'precio_total': precio_total,
                    'viaje_id': self.id,
                    'estado_compra': estado_compra,
                    'moneda_id': moneda_proveedor_id
                    
                })
                if new_gasto:
                    _logger.info(f'Gasto "{name}" creado con éxito: ID={new_gasto.id}')
                else:
                    _logger.error(f'Error al crear el gasto "{name}". Verifique los datos de entrada y las restricciones del modelo.')



    def _crear_o_actualizar_gasto_flete(self, name, producto_id, precio_total, moneda_proveedor_id, estado_compra='no_comprado'):
        if producto_id:

            gasto_viaje = self.env['gms.gasto_viaje'].search([
                ('viaje_id', '=', self.id),
                ('name', '=', name)
            ], limit=1)
            proveedor_id = self.transportista_id.id
            _logger.debug(f'Parámetros de creación/actualización para Flete: name={name}, producto_id={producto_id}, precio_total={precio_total}, moneda_proveedor_id={moneda_proveedor_id}, proveedor_id={proveedor_id}')

            if gasto_viaje:
                if gasto_viaje.estado_compra in ['comprado']:
                    _logger.info(f'El gasto "{name}" no se actualizará porque ya tiene una orden de compra asociada.')
                    # Omitimos la actualización y continuamos
                    return
                
                _logger.info(f'Actualizando gasto de Flete existente: {name}, Precio total: {precio_total}')
                gasto_viaje.write({
                    'precio_total': precio_total,
                    'moneda_id': moneda_proveedor_id,
                    'proveedor_id': proveedor_id
                })
            else:
                _logger.info(f'Creando nuevo gasto de Flete: {name}, Precio total: {precio_total}, Estado compra: {estado_compra}')
                new_gasto = self.env['gms.gasto_viaje'].create({
                    'name': name,
                    'producto_id': producto_id,
                    'precio_total': precio_total,
                    'viaje_id': self.id,
                    'estado_compra': estado_compra,
                    'moneda_id': moneda_proveedor_id,
                    'proveedor_id': proveedor_id
                })
                if new_gasto:
                    _logger.info(f'Gasto de Flete "{name}" creado con éxito: ID={new_gasto.id}')
                else:
                    _logger.error(f'Error al crear el gasto de Flete "{name}". Verifique los datos de entrada y las restricciones del modelo.')






    def action_liquidado(self):
        self._actualizar_kilogramos_a_liquidar()
        Invoice = self.env['account.move']
        for viaje in self:
            if viaje.albaran_id and viaje.albaran_id.state != 'done':
                raise UserError("No se puede pasar el viaje a estado 'Liquidado' hasta que el albarán esté confirmado.")
            else:
                # Sumar el total de los gastos
                total_gastos = sum(gasto.precio_total for gasto in viaje.gastos_ids)

                # Preparar las líneas de la factura
                invoice_lines = []
                if viaje.tipo_viaje == 'entrada':
                    for line in viaje.purchase_order_id.order_line:
                        invoice_lines.append((0, 0, {
                            'product_id': line.product_id.id,
                            'quantity': line.product_qty,
                            'price_unit': line.price_unit,
                        }))
                else:
                    for line in viaje.sale_order_id.order_line:
                        invoice_lines.append((0, 0, {
                            'product_id': line.product_id.id,
                            'quantity': line.product_uom_qty,
                            'price_unit': line.price_unit,
                        }))

                # Agregar línea para el producto transportado y los kilogramos a liquidar, si aplica
                if viaje.producto_transportado_id and viaje.kilogramos_a_liquidar:
                    invoice_lines.append((0, 0, {
                        'product_id': viaje.producto_transportado_id.id,
                        'name': f"Viaje {viaje.name}",
                        'quantity': viaje.kilogramos_a_liquidar,
                        'price_unit': viaje.producto_transportado_id.lst_price,
                        'account_id': viaje.producto_transportado_id.categ_id.property_account_income_categ_id.id,
                    }))

                # Fecha actual para la factura
                fecha_actual = fields.Date.today()

                # Preparar valores para la factura
                usd_currency_id = self.env['res.currency'].search([('name', '=', 'USD')], limit=1).id
                invoice_vals = {
                    'partner_id': viaje.solicitante_id.id if viaje.tipo_viaje == 'entrada' else viaje.transportista_id.id,
                    'move_type': 'in_invoice' if viaje.tipo_viaje == 'entrada' else 'out_invoice',
                    'invoice_line_ids': invoice_lines,
                    'invoice_date': fecha_actual,
                    'currency_id': usd_currency_id,
                    'total_descontar': str(total_gastos),
                }

                # Agregar el ID del viaje actual a los valores de la factura
                invoice_vals['viajes_ids'] = [(4, viaje.id)]

                # Crear la factura
                if total_gastos > 0 or viaje.kilogramos_a_liquidar > 0:
                    factura_creada = Invoice.create(invoice_vals)
                    viaje.write({'factura_id': factura_creada.id, 'state': 'liquidado'})



    def action_coordinado(self):
        self.write({'state': 'coordinado'})

    def action_borrador(self):
        self.write({'state': 'borrador'})





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
            raise UserError('No hay un albarán asociado a este viaje.')



    def action_generate_purchase_order(self):
        PurchaseOrder = self.env['purchase.order']
    
        # Agrupa los viajes por transportista
        grouped_trips_by_transportista = {}
        for trip in self:
            if trip.transportista_id not in grouped_trips_by_transportista:
                grouped_trips_by_transportista[trip.transportista_id] = []
            grouped_trips_by_transportista[trip.transportista_id].append(trip)
    
        # Preparar el ID de la moneda USD
        usd_currency = self.env['res.currency'].search([('name', '=', 'USD')], limit=1)
        usd_currency_id = usd_currency.id if usd_currency else False
    
        # Por cada transportista, crea una orden de compra
        for transportista, trips in grouped_trips_by_transportista.items():
            po_vals = {
                'partner_id': transportista.id,
                'currency_id': usd_currency_id,
                'order_line': [],
            }
    
            # Guarda una relación entre gastos y líneas de compra
            gastos_and_po_lines = {}
            for trip in trips:
                for gasto in trip.gastos_ids:
                    if gasto.estado_compra == 'no_comprado':
                        if gasto.name == 'Flete':
                            tarifa_de_compra = self.env['gms.datos_flete'].buscar_tarifa_compra_cercana(trip.kilometros_flete)
                            price_unit = tarifa_de_compra
                            po_line_vals = {
                                'product_id': gasto.producto_id.id,
                                'name': f"Peso Neto: {trip.peso_neto} kg, Kilómetros Flete: {trip.kilometros_flete} km, {trip.name}",
                                'product_qty': trip.peso_neto,
                                'price_unit': price_unit,
                                'product_uom': gasto.producto_id.uom_id.id,
                                'date_planned': fields.Date.today(),
                            }
                        else:
                            po_line_vals = {
                                'product_id': gasto.producto_id.id,
                                'name': f"Peso Neto: {trip.peso_neto} kg, Kilómetros Flete: {trip.kilometros_flete} km, {trip.name}",
                                'product_qty': 1,
                                'price_unit': gasto.precio_total,
                                'product_uom': gasto.producto_id.uom_id.id,
                                'date_planned': fields.Date.today(),
                            }
                        po_vals['order_line'].append((0, 0, po_line_vals))
                        # Asociar el gasto con esta línea de orden de compra
                        gastos_and_po_lines[gasto] = po_line_vals
    
            if po_vals['order_line']:
                purchase_order = PurchaseOrder.create(po_vals)
                for trip in trips:
                    for gasto in trip.gastos_ids:
                        if gasto.estado_compra == 'no_comprado':
                            gasto.write({
                                'purchase_order_id': purchase_order.id,
                                'estado_compra': 'comprado'
                            })
    
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }








    def _actualizar_kilogramos_a_liquidar(self):
       
        _logger.info("Intentando actualizar kilogramos a liquidar en el albarán.")
        if self.albaran_id:
            _logger.info("Albarán encontrado: %s", self.albaran_id.id)
            if self.albaran_id.move_ids_without_package:
                move_line = self.albaran_id.move_ids_without_package[0]
                _logger.info("Línea de movimiento seleccionada para actualizar: %s", move_line.id)
                move_line.write({'quantity': self.kilogramos_a_liquidar})
                _logger.info("Demanda actualizada en la línea de movimiento: %s", move_line.quantity)
            else:
                _logger.info("No hay líneas de movimiento en el albarán para actualizar.")
        else:
            _logger.info("No hay albarán asociado para actualizar.")





    @api.depends('peso_neto', 'medidas_propiedades_ids.merma_kg')
    def _compute_kilogramos_a_liquidar(self):
        for record in self:
            total_mermas = sum(record.medidas_propiedades_ids.mapped('merma_kg'))
            record.kilogramos_a_liquidar = record.peso_neto - total_mermas
            _logger.info("Cálculo de kilogramos_a_liquidar para el registro %s: Peso Neto = %s, Total Merma = %s, Kilogramos a Liquidar = %s", 
                        record.id, record.peso_neto, total_mermas, record.kilogramos_a_liquidar)











    @api.model
    def _post_create_actions(self, vals):
        if vals.get('ruta_id'):
            ruta = self.env['gms.rutas'].browse(vals['ruta_id'])
            if ruta.direccion_origen_id.id != vals.get('origen') or ruta.direccion_destino_id.id != vals.get('destino'):
                raise UserError("El origen y destino de la ruta deben ser iguales al del viaje.")
        return super(Viajes, self).create(vals)

    def write(self, vals):
        # Si se actualiza la ruta, verificar que coincida con el origen y destino del viaje.
        if vals.get('ruta_id'):
            ruta = self.env['gms.rutas'].browse(vals['ruta_id'])
            origen = vals.get('origen', self.origen.id)
            destino = vals.get('destino', self.destino.id)
            if ruta.direccion_origen_id.id != origen or ruta.direccion_destino_id.id != destino:
                raise UserError("El origen y destino de la ruta deben ser iguales al del viaje.")
        return super(Viajes, self).write(vals)

    # solo debe mostrar contactos hijos del solicitante
    @api.onchange('solicitante_id')
    def _onchange_solicitante_id(self):
        if self.solicitante_id:
            return {'domain': {'origen': [('id', 'child_of', self.solicitante_id.id)]}}
        return {'domain': {'origen': []}}

    



    def actualizar_ubicacion_destino(self):   #metodo que se llama en la action proceso para ver si cambia el silo en salida, no resultando
        if self.albaran_id and self.silo_id:
            if self.tipo_viaje == "salida":
                # Actualizar la ubicación destino del albarán
                self.albaran_id.write({'location_id': self.silo_id.id})
                _logger.info(f"Ubicación destino del albarán {self.albaran_id.name} actualizada a {self.silo_id.name}")

                # Actualizar las líneas de movimiento del albarán
                move_lines = self.albaran_id.move_line_ids_without_package
                for move_line in move_lines:
                    move_line.write({'location_dest_id': self.albaran_id.location_dest_id.id})
                    move_line.write({'location_id': self.silo_id.id})
                    _logger.info(f"Ubicación destino de la línea de movimiento {move_line.id} actualizada a {self.silo_id.name}")
            else:
                # Actualizar la ubicación destino del albarán
                self.albaran_id.write({'location_dest_id': self.silo_id.id})
                _logger.info(f"Ubicación destino del albarán {self.albaran_id.name} actualizada a {self.silo_id.name}")

                # Actualizar las líneas de movimiento del albarán
                move_lines = self.albaran_id.move_line_ids_without_package
                for move_line in move_lines:
                    move_line.write({'location_id': self.albaran_id.location_id.id})
                    move_line.write({'location_dest_id': self.silo_id.id})
                    _logger.info(f"Ubicación destino de la línea de movimiento {move_line.id} actualizada a {self.silo_id.name}")
        else:
            _logger.info("Es necesario seleccionar tanto un albarán como un silo para actualizar la ubicación.")


    @api.model
    def create_post_create_actions01(self, vals):
        # Crear el viaje como normalmente
        viaje = super(Viajes, self).create(vals)
        if viaje.tipo_viaje == "entrada":
            # Si hay un albarán asociado en la agenda, asignar su destino al silo del viaje
            if viaje.agenda and viaje.agenda.picking_id and viaje.agenda.picking_id.location_dest_id:
                viaje.silo_id = viaje.agenda.picking_id.location_dest_id.id

        return viaje


    # Impedir cambiar estados anteriores cuando hay un albarán asociado

    def action_borrador(self):
        if self.albaran_id:
            raise UserError('No se puede regresar al estado anterior porque hay un albarán asociado.')
        self.write({'state': 'coordinado'})







    def determinar_y_asignar_gasto_viaje(self):
         # Verificar primero si el viaje fue creado desde un albarán
        if self.creado_desde_albaran:

            return

        # no se creen registros duplicados
        if not self.gastos_ids.filtered(lambda g: g.producto_id.id == self._get_gasto_viaje_producto_id()):
            # Obtener los productos de gasto de los ajustes
            config_params = self.env['ir.config_parameter'].sudo()
            gasto_con_impuesto_id = int(config_params.get_param('gms.gasto_viaje_con_impuesto_id'))
            gasto_sin_impuesto_id = int(config_params.get_param('gms.gasto_viaje_sin_impuesto_id'))

            # Determinar si el destino es de tipo 'puerto'
            es_destino_puerto = self.destino.tipo == 'puerto'

            # Seleccionar el producto de gasto adecuado
            producto_gasto_id = gasto_sin_impuesto_id if es_destino_puerto else gasto_con_impuesto_id

            # Obtener el producto de gasto
            producto = self.env['product.product'].browse(producto_gasto_id)

            # Obtener el precio unitario del producto
            precio_unitario = producto.standard_price

            # Obtener la moneda de compra del proveedor
            moneda_proveedor_id = self.transportista_id.property_purchase_currency_id.id if self.transportista_id else False

           


          


    def _get_gasto_viaje_producto_id(self):
        # Este método auxiliar devuelve el ID del producto de gasto de viaje correspondiente
        config_params = self.env['ir.config_parameter'].sudo()
        gasto_con_impuesto_id = int(config_params.get_param('gms.gasto_viaje_con_impuesto_id'))
        gasto_sin_impuesto_id = int(config_params.get_param('gms.gasto_viaje_sin_impuesto_id'))

        # Determinar si el destino es de tipo 'puerto'
        es_destino_puerto = self.destino.tipo == 'puerto'

        # Seleccionar el producto de gasto adecuado
        return gasto_sin_impuesto_id if es_destino_puerto else gasto_con_impuesto_id




    @api.model
    def create(self, vals):
        # Generar el nombre del viaje si es necesario
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('gms.viaje')

        # Si 'ruta_id' está presente en 'vals', actualizar 'kilometros_flete' según la ruta
        if 'ruta_id' in vals:
            ruta = self.env['gms.rutas'].browse(vals['ruta_id'])
            vals['kilometros_flete'] = ruta.kilometros
        else:
            # En caso de que no haya ruta, se podría establecer un valor por defecto o dejarlo en blanco.
            vals['kilometros_flete'] = 0.0

        # Crear el viaje
        record = super().create(vals)

        # Registrar un mensaje si el viaje fue creado desde una agenda
        if record.agenda:
            record.message_post(body="Este viaje fue creado desde una agenda.", subtype_xmlid="mail.mt_note")

        # Asignar la ruta y los gastos del viaje
        #self._asignar_ruta_y_gastos(record, vals)

        return record


    def _asignar_ruta_y_gastos(self, record, vals):
        # Buscar una ruta que coincida con el origen y destino del viaje
        ruta = self.env['gms.rutas'].search([
            ('direccion_origen_id', '=', vals.get('origen')),
            ('direccion_destino_id', '=', vals.get('destino'))
        ], limit=1)

        # Si se encuentra una ruta, asignarla al viaje
        if ruta:
            record.ruta_id = ruta.id

       




    def write(self, vals):
        # Actualiza el viaje como siempre
        result = super(Viajes, self).write(vals)

        # Asigna los gastos de viaje si se actualizó la ruta
        if 'ruta_id' in vals:
            for viaje in self:
                viaje.determinar_y_asignar_gasto_viaje()

        return result


    # actualizar al chofer
    @api.onchange('camion_id')
    def _onchange_camion_id(self):
        if self.camion_id:
            self.conductor_id = self.camion_id.conductor_id.id
        else:
            self.conductor_id = False


    def accion_calcular_tara(self):

        raise UserError(_('Esta es una acción de prueba para calcular la tara.'))



    def action_set_to_proceso(self):
        self.ensure_one()
        if self.state == 'terminado' and self.albaran_id and self.albaran_id.state != 'done':
            self.state = 'proceso'
        else:
            raise UserError("El viaje no puede pasar a estado 'Proceso' bajo las condiciones actuales.")


    
    def enviar_sms_solicitante(self):
        try:
            # Preparar el mensaje con detalles del viaje
            mensaje_sms = f"Detalles del viaje: {self.name}\n"
            
            # Agregar cada medida y el peso neto después de cada medida
            for medida in self.medidas_propiedades_ids:
                mensaje_sms += f"{medida.propiedad.cod}: {medida.valor_medida} - Peso neto: {self.peso_neto} kg\n"

            # Log para depurar el mensaje completo antes de enviarlo
            _logger.debug("Mensaje SMS completo antes de enviar: %s", mensaje_sms)

            # Obtener el número de teléfono del solicitante
            telefono_solicitante = self.solicitante_id.mobile or self.solicitante_id.phone
            if telefono_solicitante:
                _logger.info("Enviando SMS al solicitante: %s", telefono_solicitante)
                self.env['sms.sms'].create({
                    'number': telefono_solicitante,
                    'body': mensaje_sms
                }).send()
                self.message_post(body=f"SMS enviado al solicitante ({telefono_solicitante}): {mensaje_sms}")
            else:
                raise UserError("El solicitante no tiene un número de teléfono registrado.")

        except Exception as e:
            error_message = f"Error al enviar SMS: {e}"
            _logger.error(error_message)
            self.message_post(body=error_message, message_type='comment', subtype_xmlid='mail.mt_comment')








    @api.onchange('peso_neto')
    def _onchange_peso_neto(self):
        if self.peso_neto:
            # Actualizar el precio total del flete en los gastos del viaje
            for gasto in self.gastos_ids:
                if gasto.name == 'Flete':  # Asegúrate de que este sea el nombre correcto del gasto de flete
                    # Calcular el nuevo precio total del flete
                    precio_unitario = gasto.producto_id.standard_price
                    gasto.precio_total = self.peso_neto * self.kilometros_flete * precio_unitario


    def action_liquidar_viajes(self):
        if not self:
            raise UserError("No se seleccionó ningún viaje.")
        _logger.info("Iniciando el proceso de liquidación de viajes...")

         # Validar que ningún viaje esté en estado 'liquidado'
        for viaje in self:
            if viaje.state == 'liquidado':
                raise UserError(f"El viaje {viaje.name} ya está liquidado y no puede ser procesado nuevamente.")

        # Diccionario para agrupar líneas de factura por proveedor
        invoice_lines_by_partner = {}

        for viaje in self:
            invoice_line = None  
            _logger.info(f"Procesando viaje: {viaje.name}")
            
            if viaje.tipo_viaje == 'entrada':
                if not viaje.purchase_order_id:
                    _logger.warning(f"El viaje {viaje.name} no tiene una orden de compra asociada.")
                    continue
                order = viaje.purchase_order_id
                purchase_line = self.env['purchase.order.line'].search([
                    ('order_id', '=', order.id),
                    ('product_id', '=', viaje.producto_transportado_id.id),
                ], limit=1)
                if not purchase_line:
                    _logger.warning(f"No se encontró una línea de pedido de compra para el producto transportado en el viaje {viaje.name}")
                    continue
                invoice_line = (0, 0, {
                    'product_id': viaje.producto_transportado_id.id,
                    'name': f"{viaje.name} - {viaje.producto_transportado_id.name}",
                    'quantity': viaje.kilogramos_a_liquidar,
                    'price_unit': viaje.producto_transportado_id.lst_price,
                    'account_id': viaje.producto_transportado_id.categ_id.property_account_expense_categ_id.id,
                    'purchase_line_id': purchase_line.id,
                })
            else:  # 'salida'
                if not viaje.sale_order_id:
                    _logger.warning(f"El viaje {viaje.name} no tiene una orden de venta asociada.")
                    continue
                order = viaje.sale_order_id
                _logger.info(f"Orden de venta asociada al viaje {viaje.name}: {order.name}")
                # Buscar la línea de pedido de venta específica para el producto transportado
                sale_line = self.env['sale.order.line'].search([
                    ('order_id', '=', order.id),
                    ('product_id', '=', viaje.producto_transportado_id.id),
                ], limit=1)

                if not sale_line:
                    _logger.warning(f"No se encontró una línea de pedido de venta para el producto transportado en el viaje {viaje.name}")
                    continue

                invoice_line = (0, 0, {
                    'product_id': viaje.producto_transportado_id.id,
                    'name': f"{viaje.name} - {viaje.producto_transportado_id.name}",
                    'quantity': viaje.kilogramos_a_liquidar,
                    'price_unit': viaje.producto_transportado_id.lst_price,
                    'account_id' : viaje.producto_transportado_id.categ_id.property_account_income_categ_id.id,
                    'sale_line_ids': [(4, sale_line.id)], 
                })



            partner_id = order.partner_id.id
            order_type_key = 'purchase_order_ids' if viaje.tipo_viaje == 'entrada' else 'sale_order_ids'

            if partner_id not in invoice_lines_by_partner:
                invoice_lines_by_partner[partner_id] = {
                    'partner_id': partner_id,
                    'lines': [invoice_line],
                    order_type_key: {order.id},
                    'total_descontar': sum(gasto.precio_total for gasto in viaje.gastos_ids),
                }
            else:
                invoice_lines_by_partner[partner_id]['lines'].append(invoice_line)
                invoice_lines_by_partner[partner_id][order_type_key].add(order.id)
                invoice_lines_by_partner[partner_id]['total_descontar'] += sum(gasto.precio_total for gasto in viaje.gastos_ids)


        for partner_id, data in invoice_lines_by_partner.items():
            usd_currency_id = self.env['res.currency'].search([('name', '=', 'USD')], limit=1).id
            move_type = 'in_invoice' if 'purchase_order_ids' in data else 'out_invoice'
            invoice_vals = {
                'partner_id': partner_id,
                'move_type': move_type,
                'invoice_line_ids': data['lines'],
                'currency_id': usd_currency_id,
                'invoice_date_due': fields.Date.today(),
                'total_descontar': str(data['total_descontar']),
                'invoice_origin': ', '.join([str(po_id) for po_id in data.get('purchase_order_ids', [])] + [str(so_id) for so_id in data.get('sale_order_ids', [])]),
            }
            _logger.info(f"Creando factura con valores: {invoice_vals}")
            factura = self.env['account.move'].create(invoice_vals)
            _logger.info(f"Factura creada con éxito. ID de la factura: {factura.id}")

            factura.write({'viajes_ids': [(6, 0, self.ids)]})
            _logger.info(f"Viajes asociados con la factura {factura.id}.")

            for order_id in data.get('purchase_order_ids', set()) | data.get('sale_order_ids', set()):
                order_model = 'purchase.order' if 'purchase_order_ids' in data else 'sale.order'
                order = self.env[order_model].browse(order_id)
                order.invoice_ids = [(4, factura.id)]
                _logger.info(f"Factura {factura.id} asociada a la orden {order.name}.")
                order.invoice_count = len(order.invoice_ids)

            for viaje in self.filtered(lambda v: getattr(v, 'purchase_order_id' if 'purchase_order_ids' in data else 'sale_order_id').partner_id.id == partner_id):
                viaje.write({'state': 'liquidado', 'factura_id': factura.id})

        _logger.info("Proceso de liquidación de viajes finalizado.")







    def action_view_factura(self):
        self.ensure_one()
        if self.factura_id:
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'account.move',
                'view_mode': 'form',
                'res_id': self.factura_id.id,
                'target': 'current',
            }
        else:
            raise UserError('No hay una factura asociada a este viaje.')






    @api.model
    def create_pesos(self, vals):
        # Verificar si 'peso_bruto', 'peso_neto' o 'tara' son negativos
        for field in ['peso_bruto', 'peso_neto', 'tara']:
            if field in vals and vals[field] < 0:
                raise UserError(_("%s no puede ser negativo." % field))
        return super(Viajes, self).create(vals)

    def write_pesos(self, vals):
        # Verificar si 'peso_bruto', 'peso_neto' o 'tara' son negativos
        for field in ['peso_bruto', 'peso_neto', 'tara']:
            if field in vals and vals[field] < 0:
                raise UserError(_("%s no puede ser negativo." % field))
        return super(Viajes, self).write(vals)





    def actualizar_sale_order_id(self):
        # Busca todos los viajes
        viajes = self.search([])
        for viaje in viajes:
            if viaje.albaran_id and viaje.albaran_id.origin:
                # Busca la orden de venta relacionada con el campo origin del albarán
                sale_order = self.env['sale.order'].search([('name', '=', viaje.albaran_id.origin)], limit=1)
                if sale_order:
                    viaje.write({'sale_order_id': sale_order.id})


