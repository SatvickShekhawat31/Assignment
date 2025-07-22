from celery import shared_task
from datetime import datetime
import pandas as pd
from capp.models import Customer, Loan

@shared_task
def load_customer_and_loan_data(customer_path, loan_path):
    # Load Customer Data
    customer_df = pd.read_excel(customer_path)
    for _, row in customer_df.iterrows():
        Customer.objects.update_or_create(
            phone_number=row['Phone Number'],
            defaults={
                'first_name': row['First Name'],
                'last_name': row['Last Name'],
                'age': row['Age'],
                'monthly_income': row['Monthly Salary'],
                'approved_limit': row['Approved Limit'],
            }
        )

    # Load Loan Data
    loan_df = pd.read_excel(loan_path)
    for _, row in loan_df.iterrows():
        try:
            customer = Customer.objects.get(id=row['Customer ID'])
            Loan.objects.update_or_create(
                customer=customer,
                loan_amount=row['Loan Amount'],
                interest_rate=row['Interest Rate'],
                tenure=row['Tenure'],
                monthly_installment=row['Monthly payment'],
                emis_paid_on_time=row['EMIs paid on Time'],
                start_date=row['Date of Approval'] if not pd.isnull(row['Date of Approval']) else datetime.now().date(),
                end_date=row['End Date'] if not pd.isnull(row['End Date']) else datetime.now().date()
            )
        except Customer.DoesNotExist:
            print(f"Customer with ID {row['Customer ID']} does not exist.")

from celery import shared_task

@shared_task
def add(x, y):
    return x + y
