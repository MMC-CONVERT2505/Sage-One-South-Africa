from apps.home.data_util import update_task_execution_status, write_task_execution_step
from apps.myob.delete_apis import *
from apps.excel.excel_reader.bank_transfer import get_excel_bank_transfer
from apps.excel.excel_reader.chart_of_account import get_excel_chart_of_account
from apps.excel.excel_reader.customer import get_excel_customer
from apps.excel.excel_reader.item import get_excel_item,get_excel_item_to_update
from apps.excel.excel_reader.job import get_excel_job
from apps.excel.excel_reader.journal import get_excel_journal
from apps.excel.excel_reader.invoice import get_excel_invoice
from apps.excel.excel_reader.invoice1 import get_excel_invoice_new
from apps.excel.excel_reader.creditnote import get_excel_creditnote
from apps.excel.excel_reader.vendorcredit import get_excel_vendorcredit
from apps.excel.excel_reader.bill import get_excel_bill 
from apps.excel.excel_reader.invoice_payment import get_excel_invoice_payment
from apps.excel.excel_reader.bill_payment import get_excel_bill_payment
from apps.excel.excel_reader.receive_money import get_excel_receive_money
from apps.excel.excel_reader.spend_money import get_excel_spend_money
from apps.excel.excel_reader.supplier import get_excel_supplier
from apps.myob.myob_reader.taxcode import get_taxcode
from apps.excel.excel_writer.add_chart_of_account import add_excel_chart_of_account
from apps.myob.myob_reader.job import get_myob_job

from apps.qbo.account.add_item_bill import add_item_bill
from apps.qbo.account.add_service_bill1 import add_service_bill1
from apps.qbo.account.get_COA_classification import get_classified_coa
from apps.qbo.reader.QBO_combined_tax import get_qbo_tax
from apps.qbo.reader.qbo_data_reader import read_qbo_data
from apps.qbo.reader.taxrate import get_qbo_taxrate
from apps.excel.excel_writer.add_bank_transfer import add_excel_bank_transfer
from apps.excel.excel_writer.add_customer import add_excel_customer
from apps.excel.excel_writer.add_creditnote import add_excel_creditnote
from apps.excel.excel_writer.add_vendorcredit import add_excel_vendorcredit 
from apps.excel.excel_writer.add_item import add_excel_item,update_excel_item
from apps.excel.excel_writer.add_job import add_excel_job
from apps.excel.excel_writer.add_journal import add_excel_journal
from apps.excel.excel_writer.add_invoice import add_excel_invoice
from apps.excel.excel_writer.add_invoice_payment import add_excel_invoice_payment
from apps.excel.excel_writer.add_bill_payment import add_excel_bill_payment
from apps.excel.excel_writer.add_bill import add_excel_bill
from apps.excel.excel_writer.add_spend_money import add_excel_spend_money
from apps.excel.excel_writer.add_receive_money import add_excel_receive_money
from apps.excel.excel_writer.add_supplier import add_excel_supplier

from apps.myob.myob_reader.chart_of_account import get_chart_of_account
from apps.myob.myob_reader.customer import get_customer
from apps.myob.myob_reader.all_bill import get_all_bill
from apps.myob.myob_reader.all_invoice import get_all_invoice
from apps.myob.myob_reader.all_invoice_for_payment import get_all_invoice_for_payments
from apps.myob.myob_reader.all_bill_for_payment import get_all_bill_for_payments
from apps.myob.myob_reader.supplier import get_supplier
from apps.myob.myob_reader.item import get_item


class ExcelToMyob(object):
    @staticmethod
    def read_data(job_id, task):
        step_name = None
        try:

            if "COA" == task.function_name:
                update_task_execution_status(task.id, status=2, task_type="read")
                
                step_name = "Reading data from taxcode"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_taxcode(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)
                
                step_name = "Reading data from chart of account myob"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_chart_of_account(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)

                step_name = "Reading data from chart_of_account"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_excel_chart_of_account(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)

                update_task_execution_status(task.id, status=1, task_type="read")

            if "Bank Transfer" == task.function_name:
                update_task_execution_status(task.id, status=2, task_type="read")

                step_name = "Reading data from myob chart_of_account"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_chart_of_account(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)

                step_name = "Reading data from Bank Transfer"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_excel_bank_transfer(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)

                update_task_execution_status(task.id, status=1, task_type="read")

            if "Job" == task.function_name:
                update_task_execution_status(task.id, status=2, task_type="read")

                step_name = "Reading data from Job"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_excel_job(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)

                update_task_execution_status(task.id, status=1, task_type="read")

            if "Customer" == task.function_name:
                update_task_execution_status(task.id, status=2, task_type="read")

                step_name = "Reading data from Customer"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_excel_customer(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)

                update_task_execution_status(task.id, status=1, task_type="read")

                
            if "Supplier" == task.function_name:
            
                step_name = "Reading data from Supplier"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_excel_supplier(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)

                update_task_execution_status(task.id, status=1, task_type="read")

          
            if "Item" == task.function_name:
                update_task_execution_status(task.id, status=2, task_type="read")

                step_name = "Reading data from myob chart_of_account"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_chart_of_account(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)

                step_name = "Reading data from myob Item"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_item(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)

                step_name = "Reading data from myob Supplier"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_supplier(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)

                step_name = "Reading data from Item"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_excel_item(job_id,task.id)
                # get_excel_item_to_update(job_id, task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)

                update_task_execution_status(task.id, status=1, task_type="read")

            if "Spend Money" == task.function_name:
                update_task_execution_status(task.id, status=2, task_type="read")
                
                step_name = "Reading data from Supplier"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_supplier(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)

                step_name = "Reading data from Customer"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_customer(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)

                step_name = "Reading data from taxcode"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_taxcode(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)

                step_name = "Reading data from chart_of_account"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_chart_of_account(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)

                step_name = "Reading myob job"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_myob_job(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)

                step_name = "Reading data from Spend Money"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_excel_spend_money(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)

                update_task_execution_status(task.id, status=1, task_type="read")

            if "Receive Money" == task.function_name:
                update_task_execution_status(task.id, status=2, task_type="read")

                step_name = "Reading data from Customer"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_customer(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)

                step_name = "Reading data from Supplier"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_supplier(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)

                step_name = "Reading data from taxcode"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_taxcode(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)

                step_name = "Reading data from chart_of_account"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_chart_of_account(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)

                step_name = "Reading myob job"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_myob_job(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)

                step_name = "Reading data from Receive Money"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_excel_receive_money(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)

                update_task_execution_status(task.id, status=1, task_type="read")

            if "Invoice" == task.function_name:
                update_task_execution_status(task.id, status=2, task_type="read")

                step_name = "Reading data from Customer"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_customer(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)

                step_name = "Reading data from taxcode"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_taxcode(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)

                step_name = "Reading data from chart_of_account"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_chart_of_account(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)

                step_name = "Reading myob job"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_myob_job(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)

                step_name = "Reading myob Item"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_item(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)

                step_name = "Reading data from Invoice"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_excel_invoice_new(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)
                
                update_task_execution_status(task.id, status=1, task_type="read")
            
            if "Customer return" == task.function_name:
                update_task_execution_status(task.id, status=2, task_type="read")
                
                step_name = "Reading data from Customer"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_customer(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)


                step_name = "Reading data from taxcode"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_taxcode(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)

                step_name = "Reading data from chart_of_account"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_chart_of_account(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)

                step_name = "Reading myob job"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_myob_job(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)

                step_name = "Reading myob Item"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_item(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)

                step_name = "Reading data from CreditNote"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_excel_creditnote(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)
                
                update_task_execution_status(task.id, status=1, task_type="read")

            if "Bills" == task.function_name:
                update_task_execution_status(task.id, status=2, task_type="read")
                
                step_name = "Reading data from Supplier"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_supplier(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)


                step_name = "Reading data from taxcode"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_taxcode(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)

                step_name = "Reading data from chart_of_account"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_chart_of_account(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)

                step_name = "Reading myob job"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_myob_job(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)

                step_name = "Reading myob Item"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_item(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)

                step_name = "Reading data from all bill"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_excel_bill(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)

                update_task_execution_status(task.id, status=1, task_type="read")

            if "Supplier return" == task.function_name:
                update_task_execution_status(task.id, status=2, task_type="read")

                step_name = "Reading data from Supplier"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_supplier(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)


                step_name = "Reading data from taxcode"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_taxcode(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)

                step_name = "Reading data from chart_of_account"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_chart_of_account(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)

                step_name = "Reading myob job"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_myob_job(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)

                step_name = "Reading myob Item"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_item(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)

                step_name = "Reading data from vendorcredit"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_excel_vendorcredit(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)

                update_task_execution_status(task.id, status=1, task_type="read")
            
            if "Journals" == task.function_name:
                update_task_execution_status(task.id, status=2, task_type="read")
                
                step_name = "Reading data from taxcode"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_taxcode(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)

                step_name = "Reading data from chart_of_account"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_chart_of_account(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)

                step_name = "Reading myob job"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_myob_job(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)

                step_name = "Reading data from Journal"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_excel_journal(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)

                update_task_execution_status(task.id, status=1, task_type="read")

            if "Customer payment" == task.function_name:
                update_task_execution_status(task.id, status=2, task_type="read")

                step_name = "Reading data from chart_of_account"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_chart_of_account(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)

                step_name = "Reading data from customers"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_customer(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)

                step_name = "Reading data from all Invoice"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_all_invoice_for_payments(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)


                step_name = "Reading data from invoice payments"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_excel_invoice_payment(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)

                update_task_execution_status(task.id, status=1, task_type="read")

            if "Supplier Payment" == task.function_name:
                update_task_execution_status(task.id, status=2, task_type="read")

                step_name = "Reading data from chart_of_account"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_chart_of_account(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)

                step_name = "Reading data from Myob Supplier"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_supplier(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)

                step_name = "Reading data from all Bill"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_all_bill_for_payments(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)

                step_name = "Reading data from bill payments"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_excel_bill_payment(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)

                update_task_execution_status(task.id, status=1, task_type="read")

        except Exception as ex:
            write_task_execution_step(
                job_id, task.id, status=0, step=step_name)
            update_task_execution_status(
                task.id, status=0, task_type="read")
            raise ex

    @staticmethod
    def write_data(job_id, task):
                
        step_name = None
        try:
            if "COA" == task.function_name:
                
                update_task_execution_status(task.id, status=2, task_type="write")

                step_name = "Adding chart_of_account data"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                add_excel_chart_of_account(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)

                update_task_execution_status(task.id, status=1, task_type="write")

            if "Bank Transfer" == task.function_name:
                update_task_execution_status(task.id, status=2, task_type="write")

                step_name = "Add Bank Transfer Data"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                add_excel_bank_transfer(job_id,task.id)
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

                step_name = "Add Customer Data"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                add_excel_customer(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)

                update_task_execution_status(task.id, status=1, task_type="write")

            if "Supplier" == task.function_name:
                update_task_execution_status(task.id, status=2, task_type="write")

                step_name = "Add Supplier Data"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                add_excel_supplier(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)

                update_task_execution_status(task.id, status=1, task_type="write")

            if "Item" == task.function_name:
                update_task_execution_status(task.id, status=2, task_type="write")

                step_name = "Add Item Data"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                add_excel_item(job_id,task.id)
                # update_excel_item(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)

                update_task_execution_status(task.id, status=1, task_type="write")

            if "Spend Money" == task.function_name:
                update_task_execution_status(task.id, status=2, task_type="write")

                step_name = "Add Spend Money Data"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                add_excel_spend_money(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)

                update_task_execution_status(task.id, status=1, task_type="write")

            if "Receive Money" == task.function_name:
                update_task_execution_status(task.id, status=2, task_type="write")

                step_name = "Add Received Money Data"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                add_excel_receive_money(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)

                update_task_execution_status(task.id, status=1, task_type="write")

            if "Invoice" == task.function_name:
                update_task_execution_status(task.id, status=2, task_type="write")

                step_name = "Add Invoice"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                add_excel_invoice(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)

                update_task_execution_status(task.id, status=1, task_type="write")

            if "Customer return" == task.function_name:
                update_task_execution_status(task.id, status=2, task_type="write")

                step_name = "Add Creditnote"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                add_excel_creditnote(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)

                update_task_execution_status(task.id, status=1, task_type="write")

            if "Bills" == task.function_name:
                update_task_execution_status(task.id, status=2, task_type="write")

                step_name = "Add Bill"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                add_excel_bill(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)

                update_task_execution_status(task.id, status=1, task_type="write")

            if "Supplier return" == task.function_name:
                update_task_execution_status(task.id, status=2, task_type="write")

                step_name = "Add vendorcredit"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                add_excel_vendorcredit(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)

                update_task_execution_status(task.id, status=1, task_type="write")

            if "Journals" == task.function_name:
                update_task_execution_status(task.id, status=2, task_type="write")

                step_name = "Add Journal data"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                add_excel_journal(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)

                update_task_execution_status(task.id, status=1, task_type="write")

            if "Customer payment" == task.function_name:
                update_task_execution_status(task.id, status=2, task_type="write")

                step_name = "Add Invoice Payment Data"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                add_excel_invoice_payment(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)

                update_task_execution_status(task.id, status=1, task_type="write")

            if "Supplier Payment" == task.function_name:
                update_task_execution_status(task.id, status=2, task_type="write")

                step_name = "Add Bill Payment Data"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                add_excel_bill_payment(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)

                update_task_execution_status(task.id, status=1, task_type="write")

        except Exception as ex:
            write_task_execution_step(
                job_id, task.id, status=0, step=step_name)
            update_task_execution_status(
                task.id, status=0, task_type="write")
            raise ex
