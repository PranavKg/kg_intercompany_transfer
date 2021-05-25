# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import AccessError, UserError, ValidationError

'''

Prefix "s_" stands for source
Prefix "d_" stands for destination

'''

class intercompany_transfer(models.Model):
    _name = 'intercompany.transfer'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Inter Company Transfer"

    name = fields.Char('Name', default='/', readonly=1)
    date = fields.Date(string="Date", default=fields.Date.today, required=True)
    s_company_id = fields.Many2one('res.company', string="Source Company", required=True, default=lambda self: self.env.user.company_id,
        help="Company from which stock is transfered.")
    d_company_id = fields.Many2one('res.company', string="Destination Company", required=True,
        help="Company to which stock is transfered.")
    transfer_products_ids = fields.One2many('intercompany.transfer.line', 'intercompany_id', string='Inter Company Lines')
    state = fields.Selection([
            ('draft','Draft'),
            ('confirm', 'Confirmed')
        ], string='Status', index=True, readonly=True, default='draft',
        track_visibility='onchange', copy=False,
        help=" * The 'Draft' status is used when a user is encoding a new and unconfirmed Inter Company Transfer.\n"
             " * The 'Confirmed' status is used when an Inter Company Transfer is processed.")


    s_picking_id = fields.Many2one('stock.picking', 'Source Company Picking Out', readnly=1)
    d_picking_id = fields.Many2one('stock.picking', 'Destination Company Picking In', readnly=1)
    s_picking_type_id = fields.Many2one('stock.picking.type', string="Source Company Picking Type", required=True,
        help="Picking Type should be Delivery order.")
    d_picking_type_id = fields.Many2one('stock.picking.type', string="Dest. Company Picking Type", required=True,
        help="Picking Type should be Receipts.")

    @api.onchange('s_company_id')
    def onchange_scompany(self):
        if self.s_company_id:
            self.s_picking_type_id = self.env['stock.picking.type'].search([('code', '=', 'outgoing')], limit=1).id

    @api.onchange('d_company_id')
    def onchange_dcompany(self):
        if self.d_company_id:
            self.d_picking_type_id = self.env['stock.picking.type'].sudo().search([('warehouse_id.company_id','=',self.d_company_id.id),('code', '=', 'incoming')], limit=1).id

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('intercompany.transfer')
        rslt = super(intercompany_transfer, self).create(vals)
        return rslt

    @api.constrains('s_company_id', 'd_company_id')
    def validate_companies(self):
        for rec in self:
            if rec.s_company_id == rec.d_company_id:
                raise ValidationError(_("Source and Destination company should be different"))


    @api.multi
    def confirm(self):
        self.write({
        's_picking_id' : self.create_picking(),
        'd_picking_id' : self.create_picking(source=False),
        'state':'confirm',
        })


    def create_picking(self, source=True):
        if source:
            context = {"default_picking_type_id": self.s_picking_type_id.id}
            picking_type_id = self.s_picking_type_id
            partner_id = self.d_company_id.partner_id
            company_id = self.s_company_id
        else:
            context = {"default_picking_type_id": self.d_picking_type_id.id}
            picking_type_id = self.d_picking_type_id
            partner_id = self.s_company_id.partner_id
            company_id = self.d_company_id
        picking = (
            self.env["stock.picking"]
            .with_context(context)
            .sudo()
            .create({"company_id": company_id.id,"picking_type_id": picking_type_id.id, "date": self.date, "partner_id": partner_id.id})
        )
        for line in self.transfer_products_ids:
            if source:
                self.add_picking_line(company=self.s_company_id, picking=picking, product=line.product_id, quantity=line.qty, uom=line.uom_id)
            else:
                self.add_picking_line(company=self.d_company_id, picking=picking, product=line.d_product_id, quantity=line.qty, uom=line.d_uom_id)

        if picking.move_lines and source:
            picking.action_assign()
            picking.button_validate()
            if picking.state == "assigned":
                for move in picking.move_lines:
                    for move_line in move.move_line_ids:
                        move_line.qty_done = move_line.product_uom_qty
            picking.action_done()
        return picking.id

        

    def add_picking_line(self, company, picking, product, quantity, uom):
        move = self.env["stock.move"].search(
            [("picking_id", "=", picking.id), ("product_id", "=", product.id), ("product_uom", "=", uom.id)]
        )
        if move:
            qty = move.product_uom_qty + quantity
            move.write({"product_uom_qty": qty})
        else:
            values = {
                "state": "confirmed",
                "company_id":company.id,
                "product_id": product.id,
                "product_id": product.id,
                "product_uom": uom.id,
                "product_uom_qty": quantity,
                "name": product.name,
                "picking_id": picking.id,
                "location_id": picking.location_id.id,
                "location_dest_id": picking.location_dest_id.id,
            }

            move = self.env["stock.move"].sudo().create(values)
        return move


class intercompany_transfer_line(models.Model):
    _name = 'intercompany.transfer.line'
    _description = "Inter Company Transfer Products"

    product_id = fields.Many2one('product.product', string="Product", required=True)
    d_product_id = fields.Many2one('product.product', string="Dest. Product", required=True)
    intercompany_id = fields.Many2one('intercompany.transfer', string="Inter Company Id")
    qty = fields.Float(string='Initial Demand')
    uom_id = fields.Many2one("uom.uom", "Unit of Measure", required=True)
    d_uom_id = fields.Many2one("uom.uom", "Dest. Unit of Measure", required=True)

    @api.onchange("product_id")
    def onchange_product_id(self):
        self.uom_id = self.product_id.uom_id

    @api.onchange("d_product_id")
    def onchange_d_product_id(self):
        self.d_uom_id = self.d_product_id.uom_id
