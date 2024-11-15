# -*- coding: utf-8 -*-
#############################################################################

from odoo import models, api


class ReportAccountWizard(models.AbstractModel):
    _name = "report.account_cash_flow_reports.cash_flow_pdf_report"

    @api.model
    def _get_report_values(self, docids, data=None):
        fetched_data = []
        account_res = []
        journal_res = []
        balance_res = []
        fetched = []
        account_type_id = self.env.ref('account.data_account_type_liquidity').id
        account_ids = data['account_id']
        company = data['company_id']
        # self.model = report.account_cash_flow_reports.cash_flow_pdf_report #self.env.context.get('activ_model')
        # docs = self.env[self.model].browse(self.env.context.get('active_id'))
        docs = []
        if data['levels'] == 'summary':
            state = """ WHERE am.state = 'posted' """ if data['target_move'] == 'posted' else ''
            query3 = """SELECT to_char(am.date, 'Month') as month_part, extract(YEAR from am.date) as year_part,
             sum(aml.debit) AS total_debit, sum(aml.credit) AS total_credit,
                     sum(aml.balance) AS total_balance FROM (SELECT am.date, am.id, am.state FROM account_move as am
                     LEFT JOIN account_move_line aml ON aml.move_id = am.id
                     LEFT JOIN account_account aa ON aa.id = aml.account_id
                     LEFT JOIN account_account_type aat ON aat.id = aa.user_type_id
                     WHERE am.date BETWEEN '""" + str(data['date_from']) + """' and '""" + str(
                data['date_to']) + """' AND aat.id='""" + str(account_type_id) + """' ) am
                                 LEFT JOIN account_move_line aml ON aml.move_id = am.id
                                 LEFT JOIN account_account aa ON aa.id = aml.account_id
                                 LEFT JOIN account_account_type aat ON aat.id = aa.user_type_id
                                 """ + state + """GROUP BY month_part,year_part"""
            cr = self._cr
            cr.execute(query3)
            fetched_data = cr.dictfetchall()
        #
        # elif data['levels'] == 'consolidated':
        #     state = """ WHERE am.state = 'posted' """ if data['target_move'] == 'posted' else ''
        #     query2 = """SELECT aat.name, sum(aml.debit) AS total_debit, sum(aml.credit) AS total_credit,
        #      sum(aml.balance) AS total_balance FROM (  SELECT am.id, am.state FROM account_move as am
        #      LEFT JOIN account_move_line aml ON aml.move_id = am.id
        #      LEFT JOIN account_account aa ON aa.id = aml.account_id
        #      LEFT JOIN account_account_type aat ON aat.id = aa.user_type_id
        #      WHERE am.date BETWEEN '""" + str(data['date_from']) + """' and '""" + str(
        #         data['date_to']) + """' AND aat.id='""" + str(account_type_id) + """' ) am
        #                  LEFT JOIN account_move_line aml ON aml.move_id = am.id
        #                  LEFT JOIN account_account aa ON aa.id = aml.account_id
        #                  LEFT JOIN account_account_type aat ON aat.id = aa.user_type_id
        #                  """ + state + """GROUP BY aat.name"""
        #     cr = self._cr
        #     cr.execute(query2)
        #     fetched_data = cr.dictfetchall()
        # elif data['levels'] == 'detailed':
        #     state = """ WHERE am.state = 'posted' """ if data['target_move'] == 'posted' else ''
        #     query1 = """SELECT aa.name,aa.code, sum(aml.debit) AS total_debit, sum(aml.credit) AS total_credit,
        #      sum(aml.balance) AS total_balance FROM (SELECT am.id, am.state FROM account_move as am
        #      LEFT JOIN account_move_line aml ON aml.move_id = am.id
        #      LEFT JOIN account_account aa ON aa.id = aml.account_id
        #      LEFT JOIN account_account_type aat ON aat.id = aa.user_type_id
        #      WHERE am.date BETWEEN '""" + str(data['date_from']) + """' and '""" + str(
        #         data['date_to']) + """' AND aat.id='""" + str(account_type_id) + """' ) am
        #                  LEFT JOIN account_move_line aml ON aml.move_id = am.id
        #                  LEFT JOIN account_account aa ON aa.id = aml.account_id
        #                  LEFT JOIN account_account_type aat ON aat.id = aa.user_type_id
        #                  """ + state + """GROUP BY aa.name, aa.code"""
        #     cr = self._cr
        #     cr.execute(query1)
        #     fetched_data = cr.dictfetchall()
        #     for account in self.env['account.account'].search([]):
        #         child_lines = self._get_journal_lines(account, data)
        #         if child_lines:
        #             journal_res.append(child_lines)

        else:
            account_type_id = self.env.ref('account.data_account_type_liquidity').id
            state = """AND am.state = 'posted' """
            sql = """SELECT DISTINCT aa.name,aa.code, sum(aml.debit) AS total_debit,
                         sum(aml.credit) AS total_credit FROM (SELECT am.* FROM account_move as am
                         LEFT JOIN account_move_line aml ON aml.move_id = am.id
                         LEFT JOIN account_account aa ON aa.id = aml.account_id
                         LEFT JOIN account_account_type aat ON aat.id = aa.user_type_id
                         WHERE am.company_id = """ + company + """ AND am.date BETWEEN '""" + str(
                data['date_from']) + """' and '""" + str(
                data['date_to']) + """' AND aat.id='""" + str(account_type_id) + """' """ + state + """) am
                                     LEFT JOIN account_move_line aml ON aml.move_id = am.id
                                     LEFT JOIN account_account aa ON aa.id = aml.account_id
                                     LEFT JOIN account_account_type aat ON aat.id = aa.user_type_id
                                     GROUP BY aa.name, aa.code"""
            cr = self._cr
            cr.execute(sql)
            fetched = cr.dictfetchall()
            for account in self.env['account.account'].search([('company_id','=',int(company)),
                                                                ('id', '=', int(account_ids))]):
                print(str(account_ids))
                child_lines = self._get_lines(account, data)
                balance_lines = self._get_account_balance(account, data)
                if child_lines:
                    account_res.append(child_lines)
                    balance_res.append(balance_lines)

        return {
            'date_from': data['date_from'],
            'date_to': data['date_to'],
            'levels': data['levels'],
            'doc_ids': docids,
            'doc_model': 'account.move',
            'docs': docs,
            'fetched_data': fetched_data,
            'account_res': account_res,
            'journal_res': journal_res,
            'balance_res': balance_res,
            'fetched': fetched,
        }

    def _get_lines(self, account, data):
        account_type_id = self.env.ref('account.data_account_type_liquidity').id

        state = """AND am.state = 'posted' """ if data['target_move'] == 'posted' else ''

        query = """SELECT 
                            am.date AS line_date, 
                            aml.account_id,
                            aj.name, 
                            am.name as move_name, 
                            am.ref as line_ref,
                            par.name AS line_partner,
                            SUM(COALESCE(aml.debit, 0)) AS total_debit,
                            SUM(COALESCE(aml.credit, 0)) AS total_credit 
                            FROM  account_move as am
                            JOIN account_move_line aml ON aml.move_id = am.id
                            LEFT JOIN account_account aa ON aa.id = aml.account_id
                            LEFT JOIN account_account_type aat ON aat.id = aa.user_type_id
                            LEFT JOIN account_journal aj ON aj.id = am.journal_id
                            LEFT JOIN res_partner par ON par.id = am.partner_id
                            WHERE aa.id = """ + str(account.id) + """ and aj.type = 'cash' """ + """and  am.date BETWEEN '""" + str(
            data['date_from']) + """' and '""" + str(
            data['date_to']) + """' AND aat.id='""" + str(account_type_id) + """' """ + state + """ 
                             GROUP BY am.date,am.name, aml.account_id, aj.name,par.name,am.ref"""

        cr = self._cr
        cr.execute(query)
        fetched_data = cr.dictfetchall()

        sql2 = """SELECT am.date AS line_date, aa.name as account_name, aj.id, aj.name, sum(aml.debit) AS total_debit,
                 sum(aml.credit) AS total_credit FROM (SELECT am.* FROM account_move as am
                     LEFT JOIN account_move_line aml ON aml.move_id = am.id
                     LEFT JOIN account_account aa ON aa.id = aml.account_id
                     LEFT JOIN account_account_type aat ON aat.id = aa.user_type_id
                     LEFT JOIN res_partner par ON par.id = am.partner_id
                     WHERE am.date BETWEEN '""" + str(data['date_from']) + """' and '""" + str(
            data['date_to']) + """' AND aat.id='""" + str(account_type_id) + """' """ + state + """) am
                                         LEFT JOIN account_move_line aml ON aml.move_id = am.id
                                         LEFT JOIN account_account aa ON aa.id = aml.account_id
                                         LEFT JOIN account_journal aj ON aj.id = am.journal_id
                                         
                                         WHERE aa.id = """ + str(account.id) + """
                                         GROUP BY am.date,aa.name, aj.name, aj.id"""

        cr = self._cr
        cr.execute(sql2)
        fetch_data = cr.dictfetchall()
        if fetched_data:
            return {
                'account': account.name,
                'code': account.code,
                'move_lines': fetched_data,
                'journal_lines': fetch_data,
            }

    def _get_journal_lines(self, account, data):
        account_type_id = self.env.ref('account.data_account_type_liquidity').id
        state = """AND am.state = 'posted' """ if data['target_move'] == 'posted' else ''
        sql2 = """SELECT aa.name as account_name, aj.id, aj.name, sum(aml.debit) AS total_debit,
         sum(aml.credit) AS total_credit FROM (SELECT am.* FROM account_move as am
             LEFT JOIN account_move_line aml ON aml.move_id = am.id
             LEFT JOIN account_account aa ON aa.id = aml.account_id
             LEFT JOIN account_account_type aat ON aat.id = aa.user_type_id
             WHERE am.company_id =""" + company + """ AND am.date BETWEEN '""" + str(
            data['date_from']) + """' and '""" + str(
            data['date_to']) + """' AND aat.id='""" + str(account_type_id) + """' """ + state + """) am
                                 LEFT JOIN account_move_line aml ON aml.move_id = am.id
                                 LEFT JOIN account_account aa ON aa.id = aml.account_id
                                 LEFT JOIN account_journal aj ON aj.id = am.journal_id
                                 WHERE aa.id = """ + str(account.id) + """
                                 GROUP BY aa.name, aj.name, aj.id"""

        cr = self._cr
        cr.execute(sql2)
        fetched_data = cr.dictfetchall()
        if fetched_data:
            return {
                'account': account.name,
                'journal_lines': fetched_data,
            }

    def _get_account_balance(self, account, data):
        account_type_id = self.env.ref('account.data_account_type_liquidity').id
        state = """ AND am.state = 'posted' """ if data['target_move'] == 'posted' else ''
        sql2 = """SELECT aa.name as account_name, sum(aml.debit) - sum(aml.credit) AS account_balance FROM account_move as am 
        LEFT JOIN account_move_line aml ON aml.move_id = am.id
        LEFT JOIN account_account aa ON aa.id = aml.account_id
        LEFT JOIN account_account_type aat ON aat.id = aa.user_type_id
        LEFT JOIN account_journal aj ON aj.id = am.journal_id 
        WHERE 
        aa.id = """ + str(account.id) + """ AND am.date <= '""" + str(data['date_to']) + """' AND 
        aat.id=""" + str(account_type_id) + state + """ AND aj.type = 'cash'  
        GROUP BY aa.name"""
        print(sql2)
        cr = self._cr
        cr.execute(sql2)
        fetched_data = cr.dictfetchall()
        if fetched_data:
            return {
                'account': account.name,
                'account_balance': fetched_data,
            }
