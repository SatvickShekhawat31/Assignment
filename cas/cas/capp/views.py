from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import CustomerRegisterSerializer

from django.utils import timezone
from .models import Customer, Loan
from django.db.models import Sum
from datetime import datetime
import math
from django.utils import timezone

class RegisterCustomerView(APIView):
    def post(self, request):
        serializer = CustomerRegisterSerializer(data=request.data)
        if serializer.is_valid():
            customer = serializer.save()
            return Response({
                'customer_id': customer.id,
                'name': f"{customer.first_name} {customer.last_name}",
                'age': customer.age,
                'monthly_income': customer.monthly_income,
                'approved_limit': customer.approved_limit,
                'phone_number': customer.phone_number
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class CheckEligibilityView(APIView):
    def post(self, request):
        try:
            customer_id = request.data.get("customer_id")
            loan_amount = float(request.data.get("loan_amount"))
            interest_rate = float(request.data.get("interest_rate"))
            tenure = int(request.data.get("tenure"))

            customer = Customer.objects.get(id=customer_id)
            loans = Loan.objects.filter(customer=customer)

            on_time_loans = loans.filter(emis_paid_on_time__gte=loans.count() / 2).count()
            total_loans = loans.count()
            current_year = timezone.now().year
            current_year_loans = loans.filter(start_date__year=current_year).count()
            total_loan_amount = loans.aggregate(total=Sum("loan_amount"))["total"] or 0
            current_loans_sum = loans.aggregate(total=Sum("loan_amount"))["total"] or 0

            credit_score = 100
            if total_loans > 0:
                credit_score -= (total_loans - on_time_loans) * 10
            credit_score -= current_year_loans * 5
            credit_score -= int(total_loan_amount / 100000) * 5
            if current_loans_sum > customer.approved_limit:
                credit_score = 0

            emi = (loan_amount * (1 + (interest_rate / 100)) ** tenure) / tenure

            monthly_emis = loans.aggregate(total=Sum("monthly_installment"))["total"] or 0
            if monthly_emis + emi > 0.5 * customer.monthly_income:
                return Response({
                    "customer_id": customer.id,
                    "approval": False,
                    "interest_rate": interest_rate,
                    "corrected_interest_rate": interest_rate,
                    "tenure": tenure,
                    "monthly_installment": emi
                }, status=status.HTTP_200_OK)

            approval = False
            corrected_interest_rate = interest_rate
            if credit_score > 50:
                approval = True
            elif 30 < credit_score <= 50 and interest_rate >= 12:
                approval = True
            elif 10 < credit_score <= 30 and interest_rate >= 16:
                approval = True
            elif credit_score <= 10:
                approval = False

            if credit_score <= 50 and interest_rate < 12:
                corrected_interest_rate = 12.0
            if credit_score <= 30 and interest_rate < 16:
                corrected_interest_rate = 16.0
            if credit_score <= 10:
                corrected_interest_rate = 0.0

            if corrected_interest_rate != interest_rate:
                emi = (loan_amount * (1 + (corrected_interest_rate / 100)) ** tenure) / tenure

            return Response({
                "customer_id": customer.id,
                "approval": approval,
                "interest_rate": interest_rate,
                "corrected_interest_rate": corrected_interest_rate,
                "tenure": tenure,
                "monthly_installment": emi
            }, status=status.HTTP_200_OK)

        except Customer.DoesNotExist:
            return Response({"error": "Customer not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class CreateLoanView(APIView):
    def post(self, request):
        customer_id = request.data.get("customer_id")
        loan_amount = request.data.get("loan_amount")
        interest_rate = request.data.get("interest_rate")
        tenure = request.data.get("tenure")

        try:
            customer = Customer.objects.get(id=customer_id)
        except Customer.DoesNotExist:
            return Response({"message": "Customer not found"}, status=404)

        loans = Loan.objects.filter(customer=customer)
        total_emi = sum(loan.monthly_installment for loan in loans)
        monthly_salary = customer.monthly_income
        new_emi = (loan_amount * (interest_rate / 100) * (1 + interest_rate / 100) ** tenure) / ((1 + interest_rate / 100) ** tenure - 1)

        if total_emi + new_emi > 0.5 * monthly_salary or sum(loan.loan_amount for loan in loans) > customer.approved_limit:
            return Response({
                "loan_id": None,
                "customer_id": customer.id,
                "loan_approved": False,
                "message": "Loan cannot be approved due to salary or limit restrictions.",
                "monthly_installment": new_emi
            }, status=200)

        loan = Loan.objects.create(
            customer=customer,
            loan_amount=loan_amount,
            interest_rate=interest_rate,
            tenure=tenure,
            monthly_installment=new_emi,
            emis_paid_on_time=0,
            start_date=timezone.now().date(),
            end_date=timezone.now().date().replace(year=timezone.now().year + tenure // 12)
        )

        return Response({
            "loan_id": loan.id,
            "customer_id": customer.id,
            "loan_approved": True,
            "message": "Loan approved successfully.",
            "monthly_installment": new_emi
        }, status=201)
    
class ViewLoanDetail(APIView):
    def get(self, request, loan_id):
        try:
            loan = Loan.objects.get(id=loan_id)
            customer = loan.customer
        except Loan.DoesNotExist:
            return Response({"message": "Loan not found"}, status=404)

        return Response({
            "loan_id": loan.id,
            "customer": {
                "id": customer.id,
                "first_name": customer.first_name,
                "last_name": customer.last_name,
                "phone_number": customer.phone_number,
                "age": customer.age
            },
            "loan_amount": loan.loan_amount,
            "interest_rate": loan.interest_rate,
            "monthly_installment": loan.monthly_installment,
            "tenure": loan.tenure
        }, status=200)


class ViewLoansByCustomer(APIView):
    def get(self, request, customer_id):
        try:
            customer = Customer.objects.get(id=customer_id)
        except Customer.DoesNotExist:
            return Response({"error": "Customer not found."}, status=status.HTTP_404_NOT_FOUND)

        loans = Loan.objects.filter(customer=customer)
        loan_list = []
        for loan in loans:
            repayments_left = loan.tenure - loan.emis_paid_on_time
            loan_list.append({
                "loan_id": loan.id,
                "loan_amount": loan.loan_amount,
                "interest_rate": loan.interest_rate,
                "monthly_installment": loan.monthly_installment,
                "repayments_left": repayments_left
            })

        return Response(loan_list, status=status.HTTP_200_OK)