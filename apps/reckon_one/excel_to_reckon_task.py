from apps.home.data_util import update_task_execution_status, write_task_execution_step
from apps.myob.delete_apis import *
from apps.reckonone_payroll.excel_payroll_reader.chart_of_account import get_reckon_chart_of_account
from apps.reckonone_payroll.excel_payroll_reader.get_payroll_allowance import get_excel_payroll_allowance
from apps.reckonone_payroll.excel_payroll_reader.get_pay_schedules import get_excel_payroll_payschedules
from apps.reckonone_payroll.excel_payroll_reader.get_emplyee_details import get_excel_payroll_employee_details
from apps.reckonone_payroll.excel_payload_writer.write_employee_details import add_excel_reckon_employee_payroll
from apps.reckonone_payroll.excel_payroll_reader.get_superannuation_funds import get_excel_payroll_superannuation_funds
from apps.reckonone_payroll.excel_payload_writer.write_superannuation_funds import add_excel_reckon_superannuation_funds_payroll
from apps.reckonone_payroll.excel_payload_writer.write_leave_entitlement import add_excel_leave_entitlement
from apps.reckonone_payroll.excel_payroll_reader.get_Leave_entitlements import get_excel_payroll_Leaveentitlements
from apps.reckonone_payroll.excel_payroll_reader.get_payroll_earning_new import get_excel_payroll_earning_new
from apps.reckonone_payroll.excel_payload_writer.write_master_earning import add_excel_reckon_earning_payroll
from apps.reckonone_payroll.excel_payload_writer.write_all_employee_functions import write_all_employee_functions
from apps.reckonone_payroll.excel_payroll_reader.chart_of_account import get_reckon_chart_of_account
from apps.reckonone_payroll.excel_payload_writer.write_pay_schedules import add_excel_reckon_pay_schedules_payroll
from apps.reckonone_payroll.excel_payload_writer.write_master_allowance import add_excel_reckon_allowance_payroll
# from apps.reckonone_payroll.excel_payroll_reader.put_other_detailes import update_excel_payroll_other_details
# from apps.reckonone_payroll.excel_payroll_reader.get_payroll_reimbursement import get_excel_reimbursement
from apps.reckonone_payroll.excel_payload_writer.write_master_reimbursement import add_excel_reckon_reimbursement_payroll
from apps.reckonone_payroll.excel_payroll_reader.get_payroll_deduction import get_excel_payroll_deduction
from apps.reckonone_payroll.excel_payload_writer.write_master_deductions import add_excel_reckon_deduction_payroll
from apps.reckonone_payroll.excel_payroll_reader.get_payroll_superannuation import get_excel_payroll_superannuation
from apps.reckonone_payroll.excel_payroll_reader.get_payroll_reimbursement import get_excel_payroll_reimbursement
from apps.reckonone_payroll.excel_payload_writer.write_master_reimbursement import add_excel_reckon_reimbursement_payroll
from apps.reckonone_payroll.excel_payload_writer.write_master_leave import add_excel_reckon_payroll_leave
from apps.reckonone_payroll.excel_payroll_reader.get_payroll_leave import get_excel_payroll_leave
from apps.reckonone_payroll.excel_payload_writer.write_master_superannuation import add_excel_reckon_superannuation_payroll
from apps.reckonone_payroll.excel_payroll_reader.get_other_details import get_excel_payroll_other_details
from apps.reckonone_payroll.excel_payroll_reader.get_pay_setup import get_excel_payroll_pay_setup
from apps.reckonone_payroll.excel_payroll_reader.get_company_contributions import get_excel_payroll_company_contribution
from apps.reckonone_payroll.excel_payload_writer.write_company_contribution import add_excel_reckon_company_contribution_payroll
from apps.reckonone_payroll.excel_payroll_reader.get_other_details_new import get_excel_payroll_other_details
#   from apps.reckonone_payroll.excel_payload_writer.put_write_otherdetails import update_excel_reckon_employee_payroll
from apps.reckonone_payroll.excel_payroll_reader.update_leavebalance import get_excel_Leave_balance
from apps.reckonone_payroll.excel_payload_writer.write_leave_balance import add_excel_reckon_leave_balance
from apps.reckonone_payroll.excel_payroll_reader.get_ytd_earning import get_excel_ytds_earning_leave
from apps.reckonone_payroll.excel_payload_writer.write_ytd_earning_leave import add_excel_reckon_ytd_earning_leave
from apps.reckonone_payroll.excel_payroll_reader.get_ytd_leave import get_excel_ytds_leave
from apps.reckonone_payroll.excel_payload_writer.write_ytd_leave import add_excel_reckon_ytd_leave
from apps.reckonone_payroll.excel_payroll_reader.get_ytd_allowance import get_excel_ytds_allowance
from apps.reckonone_payroll.excel_payload_writer.write_ytd_allowance import add_excel_reckon_ytd_allowance
from apps.reckonone_payroll.excel_payroll_reader.get_ytd_deduction import get_excel_ytds_deduction
from apps.reckonone_payroll.excel_payload_writer.write_ytd_deduction import add_excel_reckon_ytd_deduction
from apps.reckonone_payroll.excel_payroll_reader.get_ytd_reimbursement import get_excel_ytds_reimbursement
from apps.reckonone_payroll.excel_payload_writer.write_ytd_reimbursement import add_excel_reckon_ytd_reimbursement
from apps.reckonone_payroll.excel_payroll_reader.get_ytd_company_cont import get_excel_ytds_company_contributions
from apps.reckonone_payroll.excel_payload_writer.write_ytd_company import add_excel_reckon_ytd_company_contributions
from apps.reckonone_payroll.excel_payroll_reader.get_ytd_tax import get_excel_ytds_tax
from apps.reckonone_payroll.excel_payload_writer.write_ytd_tax import add_excel_reckon_ytd_tax
from apps.reckonone_payroll.excel_payroll_reader.get_ytd_superannuation import get_excel_ytds_superannuation
from apps.reckonone_payroll.excel_payroll_reader.get_ytd_benifies import get_excel_ytds_Fringe_benefits
from apps.reckonone_payroll.excel_payload_writer.write_ytd_benefits import add_excel_reckon_ytd_Fringe_benefits
from apps.reckonone_payroll.excel_payload_writer.write_ytd_superannuation import add_excel_reckon_ytd_superannuation





#excel to reckon task function 
from apps.home.data_util import update_task_execution_status, write_task_execution_step
from apps.myob.delete_apis import *
from apps.reckon_one.excel_reader.bank_transfer import get_excel_reckon_bank_transfer
from apps.reckon_one.excel_reader.chart_of_account import get_reckon_chart_of_account,get_excel_reckon_chart_of_account,get_reckon_bank_account
from apps.reckon_one.excel_reader.customer import get_excel_reckon_customer,get_excel_reckon_supplier
from apps.reckon_one.excel_reader.item import get_excel_reckon_item, get_reckon_item
# from apps.reckon_one.excel_reader.invoice_items import get_excel_reckon_invoice_item
from apps.reckon_one.excel_reader.contact import get_reckon_contact
from apps.reckon_one.excel_reader.term import get_reckon_term
# from apps.reckon_one.excel_reader.job import get_excel_reckon_job
from apps.reckon_one.excel_reader.journal import get_excel_reckon_journal
from apps.reckon_one.excel_reader.invoice1 import get_excel_reckon_invoice,get_reckon_invoice, get_inactive_customers,get_new_items_from_excel_invoice
from apps.reckon_one.excel_reader.reckon_tax import get_reckon_taxcode
from apps.reckon_one.excel_reader.vendorcredit_template import get_reckon_vendorcredit_template
from apps.reckon_one.excel_reader.payment_method import get_reckon_payment_method
from apps.reckon_one.excel_reader.chart_of_account import get_reckon_chart_of_account
from apps.reckon_one.excel_reader.creditnote import get_excel_reckon_creditnote
from apps.reckon_one.excel_reader.vendorcredit import get_excel_reckon_vendorcredit
from apps.reckon_one.excel_reader.bill import get_excel_reckon_bill,get_reckon_bill,get_inactive_suppliers,get_new_items_from_excel_bill
from apps.reckon_one.excel_reader.invoice_payment import get_excel_reckon_invoice_payment
from apps.reckon_one.excel_reader.bill_payment import get_excel_reckon_bill_payment 
# from apps.reckon_one.excel_reader.bill_payment import get_excel_reckon_bill_payment
# from apps.reckon_one.excel_reader.receive_money import get_excel_receive_money
from apps.reckon_one.excel_reader.spend_money import get_excel_reckon_spend_money
from apps.reckon_one.excel_reader.receive_money import get_excel_reckon_receive_money
from apps.reckon_one.excel_reader.overpayment import get_excel_reckon_bill_overpayment,get_excel_reckon_invoice_overpayment
# from apps.reckon_one.excel_reader.supplier import get_excel_reckon_supplier
from apps.reckon_one.excel_reader.employee import get_excel_reckon_employee
from apps.reckon_one.reckon_writer.add_chart_of_account import add_excel_reckon_chart_of_account
from apps.reckon_one.reckon_writer.add_bank_transfer import add_excel_reckon_bank_transfer
from apps.reckon_one.reckon_writer.add_customer import add_excel_reckon_customer 
from apps.reckon_one.reckon_writer.add_supplier import add_excel_reckon_supplier 
from apps.reckon_one.reckon_writer.add_employee import add_excel_reckon_employee 
from apps.excel.excel_writer.add_creditnote import add_excel_creditnote
from apps.excel.excel_writer.add_vendorcredit import add_excel_vendorcredit 
from apps.reckon_one.reckon_writer.add_item import add_excel_reckon_item
from apps.reckon_one.reckon_writer.add_spend_money import add_excel_reckon_spend_money
from apps.reckon_one.reckon_writer.add_receive_money import add_excel_reckon_receive_money
from apps.reckon_one.reckon_writer.add_overpayment import add_excel_reckon_invoice_overpayment,add_excel_reckon_bill_overpayment
from apps.reckon_one.reckon_writer.add_invoice import add_excel_reckon_invoice
from apps.reckon_one.reckon_writer.add_creditnote import add_excel_reckon_creditnote
from apps.reckon_one.reckon_writer.add_bill import add_excel_reckon_bill
from apps.reckon_one.reckon_writer.add_vendorcredit import add_excel_reckon_vendorcredit
from apps.excel.excel_writer.add_job import add_excel_job
from apps.reckon_one.reckon_writer.add_journal import add_excel_reckon_journal
from apps.reckon_one.reckon_writer.add_invoice_payment import add_excel_reckon_invoice_payment
from apps.reckon_one.reckon_writer.add_bill_payment import add_excel_reckon_bill_payment

class ExcelToReckon(object):
    @staticmethod
    def read_data(job_id, task):
        step_name = None
        try:

            if task.function_name == "Account":
                update_task_execution_status(task.id, status=2, task_type="read")
                
                step_name = "Reading data from taxcode"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_reckon_taxcode(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)
                
                step_name = "Reading data from chart of account myob"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_reckon_chart_of_account(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)

                step_name = "Reading data from chart_of_account"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_excel_reckon_chart_of_account(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)

                update_task_execution_status(task.id, status=1, task_type="read")

            if "Bank Transfer" == task.function_name:
                update_task_execution_status(task.id, status=2, task_type="read")

                step_name = "Reading data from reckon chart_of_account"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_reckon_chart_of_account(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)
                
                step_name = "Reading data from reckon bank account"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_reckon_bank_account(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)

                step_name = "Reading data from Bank Transfer"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_excel_reckon_bank_transfer(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)

                update_task_execution_status(task.id, status=1, task_type="read")

            if "Job" == task.function_name:
                update_task_execution_status(task.id, status=2, task_type="read")

                step_name = "Reading data from Job"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                # get_excel_job(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)

                update_task_execution_status(task.id, status=1, task_type="read")


            if "Customer" == task.function_name:
                update_task_execution_status(task.id, status=2, task_type="read")

                step_name = "Reading data from Contact"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_excel_reckon_customer(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)
                
                update_task_execution_status(task.id, status=1, task_type="read")

            if "Supplier" == task.function_name:
                update_task_execution_status(task.id, status=2, task_type="read")

                step_name = "Reading data from Contact"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_excel_reckon_supplier(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)
                
                update_task_execution_status(task.id, status=1, task_type="read")

            if "Employee" == task.function_name:
                update_task_execution_status(task.id, status=2, task_type="read")

                step_name = "Reading data from Employee"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_excel_reckon_employee(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)
                
                update_task_execution_status(task.id, status=1, task_type="read")

            if "Item" == task.function_name:
                update_task_execution_status(task.id, status=2, task_type="read")

                step_name = "Reading data from reckon chart_of_account"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_reckon_chart_of_account(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)

                step_name = "Reading data from reckon tax"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_reckon_taxcode(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)

                step_name = "Reading data from excel Item"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_excel_reckon_item(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)

                update_task_execution_status(task.id, status=1, task_type="read")

            if "Spend Money" == task.function_name:
                update_task_execution_status(task.id, status=2, task_type="read")
                
                step_name = "Reading data from contact"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_reckon_contact(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)

                step_name = "Reading data from taxcode"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_reckon_taxcode(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)
                
                step_name = "Reading data payment method"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_reckon_payment_method(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)

                step_name = "Reading data from chart_of_account"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_reckon_chart_of_account(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)
                
                step_name = "Reading data from chart_of_account"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_reckon_bank_account(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)

                step_name = "Reading myob job"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_reckon_term(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)

                step_name = "Reading data from Spend Money"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_excel_reckon_spend_money(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)

                update_task_execution_status(task.id, status=1, task_type="read")

            if "Receive Money" == task.function_name:
                update_task_execution_status(task.id, status=2, task_type="read")

                step_name = "Reading data from Customer"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_reckon_contact(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)

                step_name = "Reading reckon Item"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_reckon_item(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)

                step_name = "Reading data payment method"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_reckon_payment_method(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)

                step_name = "Reading data from taxcode"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_reckon_taxcode(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)

                step_name = "Reading data from chart_of_account"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_reckon_chart_of_account(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)

                step_name = "Reading data from chart_of_account"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_reckon_bank_account(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)

                
                step_name = "Reading data from Receive Money"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_excel_reckon_receive_money(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)

                update_task_execution_status(task.id, status=1, task_type="read")

            if "Invoice Over Payment" == task.function_name:
                update_task_execution_status(task.id, status=2, task_type="read")

                step_name = "Reading data from Customer"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_reckon_contact(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)

                step_name = "Reading reckon Item"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_reckon_item(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)

                step_name = "Reading data payment method"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_reckon_payment_method(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)

                step_name = "Reading data from taxcode"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_reckon_taxcode(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)

                step_name = "Reading data from chart_of_account"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_reckon_chart_of_account(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)

                step_name = "Reading data from bank account"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_reckon_bank_account(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)

                
                step_name = "Reading data from Over Payment"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_excel_reckon_invoice_overpayment(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)

                update_task_execution_status(task.id, status=1, task_type="read")

            if "Bill Over Payment" == task.function_name:
                update_task_execution_status(task.id, status=2, task_type="read")

                step_name = "Reading data from Customer"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_reckon_contact(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)

                step_name = "Reading reckon Item"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_reckon_item(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)

                step_name = "Reading data payment method"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_reckon_payment_method(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)

                step_name = "Reading data from taxcode"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_reckon_taxcode(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)

                step_name = "Reading data from chart_of_account"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_reckon_chart_of_account(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)

                step_name = "Reading data from bank account"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_reckon_bank_account(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)

                
                step_name = "Reading data from Over Payment"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_excel_reckon_bill_overpayment(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)

                update_task_execution_status(task.id, status=1, task_type="read")

            if "Invoice" == task.function_name:
                update_task_execution_status(task.id, status=2, task_type="read")

                step_name = "Reading data from Customer"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_reckon_contact(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)

                step_name = "Reading data from Term"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_reckon_term(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)
                
                step_name = "Reading data from taxcode"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_reckon_taxcode(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)

                step_name = "Reading data from chart_of_account"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_reckon_chart_of_account(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)

                step_name = "Reading reckon Item"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_reckon_item(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)

                # step_name = "Reading data from excel Invoice"
                # write_task_execution_step(
                #     task.id, status=2, step=step_name)
                # get_excel_reckon_invoice(job_id,task.id)
                # write_task_execution_step(
                #     task.id, status=1, step=step_name)

                # step_name = "Reading data of inactive customers from excel Invoice"
                # write_task_execution_step(
                #     task.id, status=2, step=step_name)
                # get_inactive_customers(job_id,task.id)
                # write_task_execution_step(
                #     task.id, status=1, step=step_name)

                # step_name = "Reading data of Items from excel Invoice"
                # write_task_execution_step(
                #     task.id, status=2, step=step_name)
                # get_new_items_from_excel_invoice(job_id,task.id)
                # write_task_execution_step(
                #     task.id, status=1, step=step_name)
                
                # step_name = "Reading data from excel Invoice"
                # write_task_execution_step(
                #     task.id, status=2, step=step_name)
                # delete_excel_reckon_invoice(job_id,task.id)
                # delete_reckon_item(job_id,task.id)
                # write_task_execution_step(
                #     task.id, status=1, step=step_name)
                
                # step_name = "Reading reckon Item"
                # write_task_execution_step(
                #     task.id, status=2, step=step_name)
                # get_reckon_item(job_id,task.id)
                # write_task_execution_step(
                #     task.id, status=1, step=step_name)
                
                step_name = "Reading data from excel Invoice"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_excel_reckon_invoice(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)

                update_task_execution_status(task.id, status=1, task_type="read")
            
            if "Credit Memo" == task.function_name:
                update_task_execution_status(task.id, status=2, task_type="read")
                
                step_name = "Reading data from Customer"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_reckon_contact(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)

                step_name = "Reading data from Term"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_reckon_term(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)
                
                step_name = "Reading data from taxcode"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_reckon_taxcode(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)

                step_name = "Reading data from chart_of_account"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_reckon_chart_of_account(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)

                step_name = "Reading reckon Item"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_reckon_item(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)

                step_name = "Reading data from CreditNote"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_excel_reckon_creditnote(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)
                
                update_task_execution_status(task.id, status=1, task_type="read")

            if "Bills" == task.function_name:
                update_task_execution_status(task.id, status=2, task_type="read")
                
                step_name = "Reading data from Supplier"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_reckon_contact(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)

                step_name = "Reading data from Customer"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_reckon_term(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)
                
                step_name = "Reading data from taxcode"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_reckon_taxcode(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)

                step_name = "Reading data from chart_of_account"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_reckon_chart_of_account(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)

                step_name = "Reading reckon Item"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_reckon_item(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)

                
                step_name = "Reading data of inactive customers from excel Invoice"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_inactive_suppliers(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)

                step_name = "Reading data of Items from excel Invoice"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_new_items_from_excel_bill(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)
                
                step_name = "Reading data from excel Invoice"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                delete_excel_reckon_bill(job_id,task.id)
                delete_reckon_item(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)
                
                step_name = "Reading reckon Item"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_reckon_item(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)
                
                step_name = "Reading data from excel Invoice"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_excel_reckon_bill(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)


                update_task_execution_status(task.id, status=1, task_type="read")

            if "Supplier return" == task.function_name:
                update_task_execution_status(task.id, status=2, task_type="read")

                step_name = "Reading data from Supplier"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_reckon_contact(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)


                step_name = "Reading data from taxcode"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_reckon_taxcode(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)
                
                step_name = "Reading data from Templates"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_reckon_vendorcredit_template(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)

                step_name = "Reading data from chart_of_account"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_reckon_chart_of_account(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)

                
                step_name = "Reading Reckon Item"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_reckon_item(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)


                step_name = "Reading data from vendorcredit"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_excel_reckon_vendorcredit(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)

                update_task_execution_status(task.id, status=1, task_type="read")
            
            if "Journals" == task.function_name:
                update_task_execution_status(task.id, status=2, task_type="read")
                
                step_name = "Reading data from taxcode"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_reckon_taxcode(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)
                
                step_name = "Reading data from chart of account Reckon"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_reckon_chart_of_account(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)

                step_name = "Reading data from bank account Reckon"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_reckon_bank_account(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)

                step_name = "Reading data from Item Reckon"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_reckon_item(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)

                step_name = "Reading data from Item Reckon"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_reckon_contact(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)
                
                step_name = "Reading data from Journal"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_excel_reckon_journal(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)

                update_task_execution_status(task.id, status=1, task_type="read")

            if "Customer payment" == task.function_name:
                update_task_execution_status(task.id, status=2, task_type="read")

                step_name = "Reading data from bank accounts"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_reckon_bank_account(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)
                
                step_name = "Reading data from chart of accounts"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_reckon_chart_of_account(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)

                step_name = "Reading data from customers"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_reckon_contact(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)

                step_name = "Reading data from all Invoice"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_reckon_invoice(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)

                step_name = "Reading data from invoice payments"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_excel_reckon_invoice_payment(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)

                update_task_execution_status(task.id, status=1, task_type="read")

            if "Supplier Payment" == task.function_name:
                update_task_execution_status(task.id, status=2, task_type="read")

                step_name = "Reading data from chart_of_account"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_reckon_chart_of_account(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)

                step_name = "Reading data from bank account"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_reckon_bank_account(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)
                
                step_name = "Reading data from reckon contact"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_reckon_contact(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)

                step_name = "Reading data from all Bill"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_reckon_bill(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)

                step_name = "Reading data from bill payments"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_excel_reckon_bill_payment(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)

                update_task_execution_status(task.id, status=1, task_type="read")


            
            if task.function_name == "Pay Item Earning":

                update_task_execution_status(task.id, status=2, task_type="read")
                step_name = "Reading data from pay earnings"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_reckon_chart_of_account(job_id,task.id)
                get_excel_payroll_earning_new(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)
                
                update_task_execution_status(task.id, status=1, task_type="read")
               
                
                             
            if task.function_name == "Payitem Allowance":
                update_task_execution_status(task.id, status=2, task_type="read")
                
                step_name = "Reading data from chart of account "
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_reckon_chart_of_account(job_id,task.id)
                
                step_name = "Reading data from payroll allowance "
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_excel_payroll_allowance(job_id,task.id)

                write_task_execution_step(
                    task.id, status=1, step=step_name)

                update_task_execution_status(task.id, status=1, task_type="read")


            if task.function_name == 'Payroll Deduction':
                update_task_execution_status(task.id, status=2, task_type="read")

                step_name = "Reading data from payroll deduction"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                
                get_excel_payroll_deduction(job_id,task.id)
                
                write_task_execution_step(
                    task.id, status=1, step=step_name)
                update_task_execution_status(task.id, status=1, task_type="read")
                
            
            if task.function_name == 'Pay Item Reimbursement':
                update_task_execution_status(task.id, status=2, task_type="read")
                step_name = "Reading data from chart of account"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_reckon_chart_of_account(job_id,task.id)
                step_name = "Reading data from pay item reimbursement"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_excel_payroll_reimbursement(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)
                update_task_execution_status(task.id, status=1, task_type="read")
                
                
                
            if task.function_name == 'Pay Item Superannuation':

                update_task_execution_status(task.id, status=2, task_type="read")
                step_name = "Reading data from chart of account"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_reckon_chart_of_account(job_id,task.id)
                
                step_name = "Reading data from pay item superannuation"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                
                get_excel_payroll_superannuation(job_id,task.id)
                
                write_task_execution_step(
                    task.id, status=1, step=step_name)
                update_task_execution_status(task.id, status=1, task_type="read")
                

                
            if task.function_name == 'Pay Item Leave':

                update_task_execution_status(task.id, status=2, task_type="read")
                step_name = "Reading data from chart of account"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_reckon_chart_of_account(job_id,task.id)

                step_name = "Reading data from pay item leave"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_excel_payroll_leave(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)
                update_task_execution_status(task.id, status=1, task_type="read")


            if task.function_name == "Pay Item Company contribution":
                update_task_execution_status(task.id, status=2, task_type="read")
                step_name = "Reading data from chart of account"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_reckon_chart_of_account(job_id,task.id)
                step_name = "Reading data from company contribution"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_excel_payroll_company_contribution(job_id,task.id)
                
                write_task_execution_step(
                    task.id, status=1, step=step_name)
                update_task_execution_status(task.id, status=1, task_type="read")


            if task.function_name == "Pay Schedules":
               
                update_task_execution_status(task.id, status=2, task_type="read")
                step_name = "Reading data from pay schedules"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_excel_payroll_payschedules(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)
                update_task_execution_status(task.id, status=1, task_type="read")
            

            if task.function_name =="Superannuation funds":
               
                update_task_execution_status(task.id, status=2, task_type="read")
                step_name = "Reading data from superannuation funds"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_excel_payroll_superannuation_funds(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)
                update_task_execution_status(task.id, status=1, task_type="read")

               

            if task.function_name == "Employee details":
               
                update_task_execution_status(task.id, status=2, task_type="read")
                step_name = "Reading data from employee details"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_excel_payroll_employee_details(job_id,task.id)
                # add_excel_reckon_employee_payroll(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)
                update_task_execution_status(task.id, status=1, task_type="read")
                
                
            if task.function_name == "Leave entitlements":
                update_task_execution_status(task.id, status=2, task_type="read")
                step_name = "Reading data from leave entitlements"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_excel_payroll_Leaveentitlements(job_id,task.id)
                # add_excel_leave_entitlement(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)
                update_task_execution_status(task.id, status=1, task_type="read")
            

            if task.function_name == "Other details":
                update_task_execution_status(task.id, status=2, task_type="read")
                step_name = "Reading data from Other details"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_excel_payroll_other_details(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)
                update_task_execution_status(task.id, status=1, task_type="read")
                

            if task.function_name == "Pay Setup":
                update_task_execution_status(task.id, status=2, task_type="read")
                step_name = "Reading data from Pay Setup"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_excel_payroll_pay_setup(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)
                update_task_execution_status(task.id, status=1, task_type="read")

            # if task.function_name == "Update Other details":
            #     print("------>update other")
            #     update_task_execution_status(task.id, status=2, task_type="read")
            #     step_name = "Reading data from Update Other details"
            #     # write_task_execution_step(
            #         # task.id, status=2, step=step_name)
            #     update_excel_payroll_other_details(job_id,task.id)
            #     # write_task_execution_step(
            #         # task.id, status=1, step=step_name)
            #     update_task_execution_status(task.id, status=1, task_type="read")

            if task.function_name == "Leave Balance":
                print("------>inside leave balance")
                update_task_execution_status(task.id, status=2, task_type="read")
                step_name = "Reading data from leave balance"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_excel_Leave_balance(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)
                update_task_execution_status(task.id, status=1, task_type="read")

            if task.function_name == "YTDS Earning":
                print("------>inside ytds earning leave")
                update_task_execution_status(task.id, status=2, task_type="read")
                step_name = "Reading data from Update YTDS Earning Leave"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_excel_ytds_earning_leave(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)
                update_task_execution_status(task.id, status=1, task_type="read")


            if task.function_name == "YTDS Leave":
                print("------>inside ytds leave")
                update_task_execution_status(task.id, status=2, task_type="read")
                step_name = "Reading data from Update YTDS Leave"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_excel_ytds_leave(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)
                update_task_execution_status(task.id, status=1, task_type="read")

            
            if task.function_name == "YTDS Allowance":
                print("------>inside ytds allowance")
                update_task_execution_status(task.id, status=2, task_type="read")
                step_name = "Reading data from Update YTDS allowance"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_excel_ytds_allowance(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)
                update_task_execution_status(task.id, status=1, task_type="read")


            if task.function_name == "YTDS Deduction":
                print("------>inside ytds Deduction")
                update_task_execution_status(task.id, status=2, task_type="read")
                step_name = "Reading data from Update YTDS Deduction"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_excel_ytds_deduction(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)
                update_task_execution_status(task.id, status=1, task_type="read")


            if task.function_name == "YTDS Reimbursement":
                print("------>inside ytds reimbursement")
                update_task_execution_status(task.id, status=2, task_type="read")
                step_name = "Reading data from Update YTDS Reimbursement"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_excel_ytds_reimbursement(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)
                update_task_execution_status(task.id, status=1, task_type="read")


            if task.function_name == "YTDS Company contributions":
                print("------>inside ytds company contributions")
                update_task_execution_status(task.id, status=2, task_type="read")
                step_name = "Reading data from Update YTDS company contributions"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_excel_ytds_company_contributions(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)
                update_task_execution_status(task.id, status=1, task_type="read")


            if task.function_name == "YTDS Tax":
                print("------>inside ytds Tax")
                update_task_execution_status(task.id, status=2, task_type="read")
                step_name = "Reading data from Update ytds Tax"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_excel_ytds_tax(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)
                update_task_execution_status(task.id, status=1, task_type="read")
          

            if task.function_name == "YTDS Superannuation":
                update_task_execution_status(task.id, status=2, task_type="read")
                step_name = "Reading data from YTDS Superannuation"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_excel_ytds_superannuation(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)
                update_task_execution_status(task.id, status=1, task_type="read")


            if task.function_name == "YTDS Fringe benefits":
                update_task_execution_status(task.id, status=2, task_type="read")
                step_name = "Reading data from YTDS Fringe benefits"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_excel_ytds_Fringe_benefits(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)
                update_task_execution_status(task.id, status=1, task_type="read")



        except Exception as ex:
            write_task_execution_step(
                task.id, status=0, step=step_name)
            update_task_execution_status(
                task.id, status=0, task_type="read")
            raise ex

    @staticmethod
    def write_data(job_id, task):
                
        step_name = None
        try:
            if task.function_name in ["COA","Account"]:
                
                update_task_execution_status(task.id, status=2, task_type="write")

                step_name = "Adding chart_of_account data"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                add_excel_reckon_chart_of_account(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)

                update_task_execution_status(task.id, status=1, task_type="write")

            if "Bank Transfer" == task.function_name:
                update_task_execution_status(task.id, status=2, task_type="write")

                step_name = "Add Bank Transfer Data"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                add_excel_reckon_bank_transfer(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)

                update_task_execution_status(task.id, status=1, task_type="write")

            if "Job" == task.function_name:
                update_task_execution_status(task.id, status=2, task_type="write")

                step_name = "Add Job Data"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                add_excel_job(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)

                update_task_execution_status(task.id, status=1, task_type="write")

            if "Customer" == task.function_name:
                update_task_execution_status(task.id, status=2, task_type="write")

                step_name = "Add Contact Data"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                add_excel_reckon_customer(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)

                update_task_execution_status(task.id, status=1, task_type="write")

            if "Supplier" == task.function_name:
                update_task_execution_status(task.id, status=2, task_type="write")

                step_name = "Add Contact Data"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                add_excel_reckon_customer(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)

                update_task_execution_status(task.id, status=1, task_type="write")
            
            if "Employee" == task.function_name:
                update_task_execution_status(task.id, status=2, task_type="write")

                step_name = "Add EMployee Data"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                add_excel_reckon_employee(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)

                update_task_execution_status(task.id, status=1, task_type="write")

            if "Item" == task.function_name:
                update_task_execution_status(task.id, status=2, task_type="write")

                step_name = "Add Item Data"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                add_excel_reckon_item(job_id,task.id)
                # update_excel_item(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)

                update_task_execution_status(task.id, status=1, task_type="write")

            if "Spend Money" == task.function_name:
                update_task_execution_status(task.id, status=2, task_type="write")

                step_name = "Add Spend Money Data"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                add_excel_reckon_spend_money(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)

                update_task_execution_status(task.id, status=1, task_type="write")

            if "Receive Money" == task.function_name:
                update_task_execution_status(task.id, status=2, task_type="write")

                step_name = "Add Received Money Data"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                add_excel_reckon_receive_money(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)

                update_task_execution_status(task.id, status=1, task_type="write")

            if "Invoice Over Payment" == task.function_name:
                update_task_execution_status(task.id, status=2, task_type="write")

                step_name = "Add Over Payment Data"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                add_excel_reckon_invoice_overpayment(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)

                update_task_execution_status(task.id, status=1, task_type="write")
            
            if "Bill Over Payment" == task.function_name:
                update_task_execution_status(task.id, status=2, task_type="write")

                step_name = "Add Over Payment Data"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                add_excel_reckon_bill_overpayment(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)

                update_task_execution_status(task.id, status=1, task_type="write")
            
            if "Invoice" == task.function_name:
                update_task_execution_status(task.id, status=2, task_type="write")

                step_name = "Add Invoice"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                add_excel_reckon_invoice(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)

                update_task_execution_status(task.id, status=1, task_type="write")

            if "Credit Memo" == task.function_name:
                update_task_execution_status(task.id, status=2, task_type="write")

                step_name = "Add Creditnote"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                add_excel_reckon_creditnote(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)

                update_task_execution_status(task.id, status=1, task_type="write")

            if "Bills" == task.function_name:
                update_task_execution_status(task.id, status=2, task_type="write")

                step_name = "Add Bill"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                add_excel_reckon_bill(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)

                update_task_execution_status(task.id, status=1, task_type="write")

            if "Supplier return" == task.function_name:
                update_task_execution_status(task.id, status=2, task_type="write")

                step_name = "Add vendorcredit"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                add_excel_reckon_vendorcredit(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)

                update_task_execution_status(task.id, status=1, task_type="write")

            if "Journals" == task.function_name:
                update_task_execution_status(task.id, status=2, task_type="write")

                step_name = "Add Journal data"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                add_excel_reckon_journal(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)

                update_task_execution_status(task.id, status=1, task_type="write")

            if "Customer payment" == task.function_name:
                update_task_execution_status(task.id, status=2, task_type="write")

                step_name = "Add Invoice Payment Data"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                add_excel_reckon_invoice_payment(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)

                update_task_execution_status(task.id, status=1, task_type="write")

            if "Supplier Payment" == task.function_name:
                update_task_execution_status(task.id, status=2, task_type="write")

                step_name = "Add Bill Payment Data"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                add_excel_reckon_bill_payment(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)

                update_task_execution_status(task.id, status=1, task_type="write")

            

            if task.function_name == "Pay Item Earning":
                update_task_execution_status(task.id, status=2, task_type="write")

                step_name = "Add Pay Item Earning Data"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                add_excel_reckon_earning_payroll(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)

                update_task_execution_status(task.id, status=1, task_type="write")



            if task.function_name == "Payitem Allowance":

                update_task_execution_status(task.id, status=2, task_type="write")
                step_name = "Add Payitem Allowance Data"
                write_task_execution_step(
                    task.id, status=2, step=step_name)

                add_excel_reckon_allowance_payroll(job_id,task.id)

                write_task_execution_step(
                    task.id, status=1, step=step_name)

                update_task_execution_status(task.id, status=1, task_type="write")

            if task.function_name == 'Payroll Deduction':

                update_task_execution_status(task.id, status=2, task_type="write")
                step_name = "Add Payroll Deduction Data"
                write_task_execution_step(
                    task.id, status=2, step=step_name)

                add_excel_reckon_deduction_payroll(job_id,task.id)

                write_task_execution_step(
                    task.id, status=1, step=step_name)

                update_task_execution_status(task.id, status=1, task_type="write")

            if task.function_name == 'Pay Item Reimbursement':
                update_task_execution_status(task.id, status=2, task_type="write")
                step_name = "Add Pay Item Reimbursement Data"
                write_task_execution_step(
                    task.id, status=2, step=step_name)

                add_excel_reckon_reimbursement_payroll(job_id,task.id)

                write_task_execution_step(
                    task.id, status=1, step=step_name)

                update_task_execution_status(task.id, status=1, task_type="write")

            if task.function_name == 'Pay Item Superannuation':
                update_task_execution_status(task.id, status=2, task_type="write")
                step_name = "Add Pay Item Superannuation Data"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                add_excel_reckon_superannuation_payroll(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)
                update_task_execution_status(task.id, status=1, task_type="write")


            if task.function_name == 'Pay Item Leave':

                update_task_execution_status(task.id, status=2, task_type="write")
                step_name = "Add Pay Item Leave Data"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                add_excel_reckon_payroll_leave(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)
                update_task_execution_status(task.id, status=1, task_type="write")

            if task.function_name == "Pay Item Company contribution":

                update_task_execution_status(task.id, status=2, task_type="write")
                step_name = "Add Pay Item Leave Data"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                add_excel_reckon_company_contribution_payroll(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)
                update_task_execution_status(task.id, status=1, task_type="write")


            if task.function_name == "Pay Schedules":
                update_task_execution_status(task.id, status=2, task_type="write")
                step_name = "Add Pay Schedules Data"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                add_excel_reckon_pay_schedules_payroll(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)
                update_task_execution_status(task.id, status=1, task_type="write")

            if task.function_name =="Superannuation funds":
                
                update_task_execution_status(task.id, status=2, task_type="write")
                step_name = "Add Superannuation funds data"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                add_excel_reckon_superannuation_funds_payroll(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)
                update_task_execution_status(task.id, status=1, task_type="write")


            if task.function_name == "Pay Setup":
                update_task_execution_status(task.id, status=2, task_type="write")
                step_name = "Write all employee function"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                write_all_employee_functions(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)
                update_task_execution_status(task.id, status=1, task_type="write")

          
            # if task.function_name == "Update Other details":
            #     update_task_execution_status(task.id, status=2, task_type="write")
            #     step_name = "Write Put Other details"
            #     write_task_execution_step(
            #         task.id, status=2, step=step_name)
            #     update_excel_reckon_employee_payroll(job_id,task.id)
            #     write_task_execution_step(
            #         task.id, status=1, step=step_name)
            #     update_task_execution_status(task.id, status=1, task_type="write")

            
            
            if task.function_name == "Leave Balance":
                update_task_execution_status(task.id, status=2, task_type="write")
                step_name = "Write Leave Balance"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                add_excel_reckon_leave_balance(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)
                update_task_execution_status(task.id, status=1, task_type="write")


            if task.function_name == "YTDS Earning":
                update_task_execution_status(task.id, status=2, task_type="write")
                step_name = "Write YTDS Earning"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                add_excel_reckon_ytd_earning_leave(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)
                update_task_execution_status(task.id, status=1, task_type="write")


            if task.function_name == "YTDS Leave":
                update_task_execution_status(task.id, status=2, task_type="write")
                step_name = "Write YTDS Earning"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                add_excel_reckon_ytd_leave(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)
                update_task_execution_status(task.id, status=1, task_type="write")

            
            if task.function_name == "YTDS Allowance":
                update_task_execution_status(task.id, status=2, task_type="write")
                step_name = "Write YTDS Allowance"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                add_excel_reckon_ytd_allowance(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)
                update_task_execution_status(task.id, status=1, task_type="write")


            if task.function_name == "YTDS Deduction":
                update_task_execution_status(task.id, status=2, task_type="write")
                step_name = "Write YTDS Deduction"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                add_excel_reckon_ytd_deduction(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)
                update_task_execution_status(task.id, status=1, task_type="write")


            if task.function_name == "YTDS Reimbursement":
                update_task_execution_status(task.id, status=2, task_type="write")
                step_name = "Write YTDS Reimbursement"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                add_excel_reckon_ytd_reimbursement(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)
                update_task_execution_status(task.id, status=1, task_type="write")


            if task.function_name == "YTDS Company contributions":
                update_task_execution_status(task.id, status=2, task_type="write")
                step_name = "Write YTDS company contributions"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                add_excel_reckon_ytd_company_contributions(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)
                update_task_execution_status(task.id, status=1, task_type="write")

            if task.function_name == "YTDS Tax":
                update_task_execution_status(task.id, status=2, task_type="write")
                step_name = "Write YTDS Tax"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                add_excel_reckon_ytd_tax(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)
                update_task_execution_status(task.id, status=1, task_type="write")


            if task.function_name == "YTDS Fringe benefits":
                update_task_execution_status(task.id, status=2, task_type="write")
                step_name = "Write YTDS Fringe benefits"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                add_excel_reckon_ytd_Fringe_benefits(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)
                update_task_execution_status(task.id, status=1, task_type="write")



            if task.function_name == "YTDS Superannuation":
                update_task_execution_status(task.id, status=2, task_type="write")
                step_name = "Write YTDS Superannuation"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                add_excel_reckon_ytd_superannuation(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)
                update_task_execution_status(task.id, status=1, task_type="write")


        except Exception as ex:
            write_task_execution_step(
                task.id, status=0, step=step_name)
            update_task_execution_status(
                task.id, status=0, task_type="write")
            raise ex
