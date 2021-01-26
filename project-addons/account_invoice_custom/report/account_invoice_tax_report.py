# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models, fields, api, tools


class AccountInvoiceTaxReport(models.Model):

    _name = "account.invoice.tax.report"
    _description = "Invoice Taxes Statistics"
    _auto = False
    _rec_name = 'date'

    tax_id = fields.Many2one("account.tax", "Tax", readonly=True)
    account_id = fields.Many2one("account.account", "Account", readonly=True)
    base = fields.Float("Base", digits=(16, 2), readonly=True)
    amount = fields.Float("Amount", digits=(16, 2), readonly=True)
    invoice_id = fields.Many2one("account.invoice", "Invoice", readonly=True)
    journal_id = fields.Many2one("account.journal", "Journal", readonly=True)
    partner_id = fields.Many2one("res.partner", "Partner", readonly=True)
    date = fields.Date("Date", readonly=True)
    type = fields.Selection([
        ('out_invoice', 'Customer Invoice'),
        ('in_invoice', 'Vendor Bill'),
        ('out_refund', 'Customer Credit Note'),
        ('in_refund', 'Vendor Credit Note'),
        ], readonly=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('open', 'Open'),
        ('paid', 'Paid'),
        ('cancel', 'Cancelled')
        ], string='Invoice Status', readonly=True)
    company_id = fields.Many2one("res.company", "Company", required=True)
    fiscal_position_id = fields.Many2one('account.fiscal.position',
                                         'Fiscal Position', readonly=True)

    _order = 'date desc'

    _depends = {
        'account.invoice.tax': [
            'tax_id', 'account_id', 'base', 'amount',
            'invoice_id', 'company_id'
        ],
        'account.invoice': [
            'commercial_partner_id', 'fiscal_position_id',
            'journal_id', 'state', 'type', 'user_id', 'date'
        ],
    }

    def _select(self):
        select_str = """
            SELECT sub.id, sub.date, sub.partner_id, sub.journal_id,
                sub.fiscal_position_id, sub.company_id, sub.type, sub.state,
                sub.account_id, sub.base, sub.amount, sub.tax_id,
                sub.invoice_id
        """
        return select_str

    def _sub_select(self):
        select_str = """
                SELECT ait.id AS id, ai.date,
                    ai.commercial_partner_id as partner_id,
                    ai.journal_id, ai.fiscal_position_id, ait.company_id,
                    ai.type, ai.state, ait.account_id,
                    SUM(invoice_type.sign_qty *
                        (ait.amount + ait.amount_rounding)) AS amount,
                    SUM(invoice_type.sign_qty * ait.base) as base,
                    ait.tax_id, ait.invoice_id
        """
        return select_str

    def _from(self):
        from_str = """
                FROM account_invoice_tax ait
                JOIN account_invoice ai ON ai.id = ait.invoice_id
                JOIN (
                    -- Temporary table to decide if the qty should be added
                    -- or retrieved (Invoice vs Credit Note)
                    SELECT id,(CASE
                         WHEN ai.type::text = ANY
                             (ARRAY['in_refund'::character varying::text,
                                    'in_invoice'::character varying::text])
                            THEN -1
                            ELSE 1
                        END) AS sign,(CASE
                         WHEN ai.type::text = ANY
                             (ARRAY['out_refund'::character varying::text,
                                    'in_invoice'::character varying::text])
                            THEN -1
                            ELSE 1
                        END) AS sign_qty
                    FROM account_invoice ai
                ) AS invoice_type ON invoice_type.id = ai.id
        """
        return from_str

    def _group_by(self):
        group_by_str = """
                GROUP BY ait.id, ai.date, ait.invoice_id,
                    ai.commercial_partner_id, ai.journal_id,
                    ai.fiscal_position_id, ait.company_id, ai.type, ai.state,
                    ait.account_id, ait.tax_id
        """
        return group_by_str

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""CREATE or REPLACE VIEW %s as (
            %s
            FROM (
                %s %s %s) AS sub
        )""" % (
                self._table, self._select(), self._sub_select(), self._from(),
                self._group_by()))
