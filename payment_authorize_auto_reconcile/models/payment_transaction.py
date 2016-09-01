# -*- coding: utf-8 -*-
# © 2016-TODAY LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api
#import logging
#_logger = logging.getLogger(__name__)


class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    @api.model
    def _authorize_form_validate(self, tx, data):
        before_state = tx.state
        res = super(PaymentTransaction, self)._authorize_form_validate(
            tx, data
        )
        if res and before_state != 'done' and tx.state == 'done':
            reference = data.get('x_invoice_num')
            invoice_id = self.env['account.invoice'].search([
                ('number', '=', reference)
            ], limit=1)
            if not invoice_id:
                return res
            self.env.with_context(default_invoice_ids=[(4, invoice_id, False)])
            partner_id = invoice_id.partner_id
            if partner_id.commercial_partner_id:
                partner_id = partner_id.commercial_partner_id            
            acquirer_id = tx.acquirer_id
            pay_amount = float(data.get('x_amount'))
            trans_id = data.get('x_trans_id', 0) #todo: put somewhere            
            payment = self.env['account.payment'.create({
                'communication': reference,
                'currency_id': invoice_id.currency_id.id, #todo: make sure is USD
                'partner_type': 'customer',
                'partner_id': partner_id.id,
                'payment_method_id': 1, #todo: make sure is incoming
                'payment_date': fields.Date.today(),
                'payment_difference_handling': 'open',
                'journal_id': acquirer_id.journal_id.id,
                'amount': pay_amount,
                'writeoff_account_id': False,
                'payment_type': 'inbound',
            })
            payment.post()  
        return res
