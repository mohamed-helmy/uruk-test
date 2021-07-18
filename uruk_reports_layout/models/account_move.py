import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)





class AccountMove(models.Model):

    _inherit = 'account.move'



    def amount_to_text(self, amount):

        return self.env.user.currency_id.amount_to_text(amount)









    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):



      #  _logger.debug("//////////////////////////////////////// is_usool {}".format(self.env.user.company_id.is_usool))



        res = super(AccountMove, self).fields_view_get(



            view_id=view_id,



            view_type=view_type,



            toolbar=toolbar,



            submenu=submenu)



        if self.env.user.company_id.is_usool == False:

            if res.get('toolbar', False) and res.get('toolbar').get('print', False):

                reports = res.get('toolbar').get('print')

                for report in reports:

                    if report.get('report_file', False) and report.get('report_file') == 'uruk_reports_layout.usool_report_english_invoice' :

                        res['toolbar']['print'].remove(report)

                   

                    if report.get('report_file', False) and report.get('report_file') == 'uruk_reports_layout.usool_report_arabic_invoice' :

                        res['toolbar']['print'].remove(report)



        

        if self.env.user.company_id.is_usool:

            if res.get('toolbar', False) and res.get('toolbar').get('print', False):

                reports = res.get('toolbar').get('print')

                #_logger.debug("//////////////////////////////////////// reports {}".format(reports))

                for report in reports:

                    #| report.get('report_file') == 'uruk_reports_layout.report_english_invoice' 

                    if report.get('report_file', False) and report.get('report_file') == 'uruk_reports_layout.report_arabic_invoice' :

                        #_logger.debug("//////////////////////////////////////// report {}".format(report.get('report_file')))

                        res['toolbar']['print'].remove(report)



                    if report.get('report_file', False) and report.get('report_file') == 'uruk_reports_layout.report_english_invoice' :

                        #_logger.debug("//////////////////////////////////////// report {}".format(report.get('report_file')))

                        res['toolbar']['print'].remove(report)





        return res









class AccountMoveLine(models.Model):

    _inherit = 'account.move.line'



    barcode = fields.Char(string="Barcode", compute='compute_product_barcode', readonly=False)



    @api.depends('product_id')

    def compute_product_barcode(self):

        for line in self:

            if line.product_id:

                line.barcode = line.product_id.barcode

            else:

                line.barcode = False







   







        

