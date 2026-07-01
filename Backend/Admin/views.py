from flask import request
from Config import SessionLocal
from Admin.models import Guarantor_Confirmations, Loan_History, Loan_Requests, Members,Savings,Loans,Bank_Interests,Loan_Repayments,Interest_Distribution,Financial_Periods, Savings_Requests
from sqlalchemy import func
import math
from flask import request, jsonify
from dateutil.relativedelta import relativedelta
from datetime import date, datetime, timedelta
def view_members():
    print("Fetching all members")
    try:
        db = SessionLocal()
        members = db.query(Members).all()
        members_list = []

        for member in members:
            # sum all savings for this member
            total_savings = db.query(func.sum(Savings.amount))\
                .filter(Savings.memberId == member.memberId)\
                .scalar() or 0

            # sum all active loans for this member
            total_loans = db.query(func.sum(Loans.amount))\
                .filter(Loans.borrowerId == member.memberId)\
                .filter(Loans.status == 'active')\
                .scalar() or 0

            members_list.append({
                "first_name": member.firstName,
                "last_name": member.lastName,
                "email": member.email,
                "date_joined": member.date_joined,
                "total_savings": total_savings,
                "total_loans": total_loans
            })

        db.close()
        return members_list

    except Exception as e:
        print(f"Error fetching members: {e}")
        return []
    
def max_loan_no_guarantor(memberId):
    try:
        db = SessionLocal()

        total_savings = db.query(func.sum(Savings.amount))\
            .filter(Savings.memberId == memberId)\
            .scalar() or 0

        db.close()

        max_loan = total_savings * 0.75
        return {
            "total_savings": total_savings,
            "max_loan_without_guarantor": max_loan
        }

    except Exception as e:
        print(f"Error calculating max loan: {e}")
        return {}


def view_all_savings():
    print("Fetching all savings")
    try:
        db = SessionLocal()

        members = db.query(Members).all()
        savings_list = []

        current_month = datetime.now().month
        current_year = datetime.now().year

        for member in members:
            # total savings all time
            total_savings = db.query(func.sum(Savings.amount))\
                .filter(Savings.memberId == member.memberId)\
                .scalar() or 0

            # check if they saved this month
            saved_this_month = db.query(Savings)\
                .filter(Savings.memberId == member.memberId)\
                .filter(func.month(Savings.date_saved) == current_month)\
                .filter(func.year(Savings.date_saved) == current_year)\
                .first()

            savings_list.append({
                "first_name": member.firstName,
                "last_name": member.lastName,
                "total_savings": total_savings,
                "paid_this_month": True if saved_this_month else False
            })

        db.close()
        return savings_list

    except Exception as e:
        print(f"Error fetching savings: {e}")
        return []
def loan_viability(memberId, requested_amount):
    print(f"Calculating loan viability for member {memberId}")
    try:
        db = SessionLocal()

        member = db.query(Members).filter(Members.memberId == memberId).first()
        if not member:
            return {"error": "Member not found"}

        total_savings = db.query(func.sum(Savings.amount))\
            .filter(Savings.memberId == memberId)\
            .scalar() or 0

        total_active_loans = db.query(func.sum(Loans.amount))\
            .filter(Loans.borrowerId == memberId)\
            .filter(Loans.status == 'active')\
            .scalar() or 0

        max_without_guarantor = total_savings * 0.75
        remaining_viability = max_without_guarantor - total_active_loans

        # needs guarantor if requested amount exceeds remaining borrowing power
        needs_guarantor = requested_amount > remaining_viability

        potential_guarantors = db.query(Members)\
            .filter(Members.memberId != memberId)\
            .filter(
                  db.query(func.sum(Savings.amount))\
                       .filter(Savings.memberId == Members.memberId)\
                       .scalar_subquery() * 0.75 > remaining_viability
    )\
            .all()

        guarantors_list = [
            {
                "memberId": g.memberId,
                "first_name": g.firstName,
                "last_name": g.lastName
            }
            for g in potential_guarantors
        ]

        db.close()

        return {
            "member": f"{member.firstName} {member.lastName}",
            "total_savings": total_savings,
            "total_active_loans": total_active_loans,
            "max_loan_without_guarantor": max_without_guarantor,
            "remaining_borrowing_power": remaining_viability,
            "requested_amount": requested_amount,
            "needs_guarantor": needs_guarantor,
            # only return guarantors list if they actually need one
            "suggested_guarantors": guarantors_list if needs_guarantor else []
        }

    except Exception as e:
        print(f"Error calculating viability: {e}")
        return {}
def calculate_due_date(amount, date_borrowed):
    # every 20k = 1 month, minimum 1 month
    months = math.ceil(amount / 20000)
    due_date = date_borrowed + relativedelta(months=months)
    return due_date    

def create_loan(borrowerId, guarantorId, amount):
    try:
        db = SessionLocal()
        from datetime import date

        date_borrowed = date.today()
        due_date = calculate_due_date(amount, date_borrowed)

        new_loan = Loans(
            borrowerId=borrowerId,
            guarantorId=guarantorId,
            amount=amount,
            date_borrowed=date_borrowed,
            due_date=due_date,
            status='active',
            amount_paid=0,
            guarantor_paid=False
        )

        db.add(new_loan)
        db.commit()
        db.close()

        return {
            "message": "Loan created successfully",
            "amount": amount,
            "date_borrowed": date_borrowed,
            "due_date": due_date
        }

    except Exception as e:
        print(f"Error creating loan: {e}")
        return {}
from datetime import date

def view_all_borrowers():
    print("Fetching all borrowers")
    try:
        db = SessionLocal()
        loans = db.query(Loans).all()
        borrowers_list = []
        total_loans = 0

        for loan in loans:
            member = db.query(Members).filter(Members.memberId == loan.borrowerId).first()
            
            amount = float(loan.amount)
            today = date.today()
            due_date = loan.due_date
            is_past_due = today > due_date
            interest = amount * 0.20 if is_past_due else 0

            borrowers_list.append({
                "loanId": loan.loanId,
                "borrower": f"{member.firstName} {member.lastName}",
                "amount_borrowed": amount,
                "date_borrowed": loan.date_borrowed,
                "due_date": loan.due_date,
                "amount_paid": float(loan.amount_paid),
                "interest": interest,
                "is_past_due": is_past_due,
                "status": loan.status,
                "guarantor_paid": loan.guarantor_paid,
                "guarantorId": loan.guarantorId
            })
            total_loans += amount

        db.close()
        return {
            "total_loans": total_loans,
            "total_borrowers": len(borrowers_list),
            "loans": borrowers_list
        }

    except Exception as e:
        print(f"Error fetching borrowers: {e}")
        return []
def view_guarantor_details(guarantorId):
    print(f"Fetching guarantor details for member {guarantorId}")
    try:
        db = SessionLocal()

        # check the guarantor exists
        guarantor = db.query(Members).filter(Members.memberId == guarantorId).first()
        if not guarantor:
            return {"error": "Guarantor not found"}

        # get all loans where this member is the guarantor
        guaranteed_loans = db.query(Loans)\
            .filter(Loans.guarantorId == guarantorId)\
            .all()

        if not guaranteed_loans:
            return {
                "guarantor": f"{guarantor.firstName} {guarantor.lastName}",
                "message": "This member has not guaranteed any loans"
            }

        loans_list = []

        for loan in guaranteed_loans:
            # get the borrower details
            borrower = db.query(Members).filter(Members.memberId == loan.borrowerId).first()

            # default date is due_date + 10 days (as per chama rules)
            from datetime import timedelta
            default_date = loan.due_date + timedelta(days=10)

            loans_list.append({
                "loanId": loan.loanId,
                "borrower": f"{borrower.firstName} {borrower.lastName}",
                "amount_guaranteed": loan.amount,
                "date_borrowed": loan.date_borrowed,
                "due_date": loan.due_date,
                "default_date": default_date,  # guarantor must pay by this date
                "status": loan.status,
                "guarantor_paid": loan.guarantor_paid
            })

        db.close()

        return {
            "guarantor": f"{guarantor.firstName} {guarantor.lastName}",
            "total_guaranteed": len(loans_list),
            "loans": loans_list
        }

    except Exception as e:
        print(f"Error fetching guarantor details: {e}")
        return {}


def add_member():
    print("Adding a new member")
    try:
        db = SessionLocal()
        data = request.get_json()

        # check if member already exists
        existing = db.query(Members).filter(Members.email == data['email']).first()
        if existing:
            return jsonify({"error": "Member already exists"}), 409

        new_member = Members(
            firstName=data['firstName'],
            lastName=data['lastName'],
            email=data['email'],
            phone=data['phone'],
            roles=data['roles'],
            date_joined=data['date_joined']
        )

        db.add(new_member)
        db.commit()
        db.refresh(new_member) 
        db.close()

        return jsonify({
            "message": "Member created successfully",
            "memberId": new_member.memberId
        }), 201

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500
def view_borrowed_interests():
    print("Fetching all borrowed interests")
    try:
        db = SessionLocal()
        repayments = db.query(Loan_Repayments).all()
        repayments_list = []
        total_borrowed_interest = 0

        for repayment in repayments:
            
            if repayment.loanId:
                loan = db.query(Loans).filter(Loans.loanId == repayment.loanId).first()
                guarantor_paid = loan.guarantor_paid
                borrowerId = loan.borrowerId
                guarantorId = loan.guarantorId
                amount = loan.amount
            else:
                
                loan_history = db.query(Loan_History)\
                    .filter(Loan_History.paid_date == repayment.date_paid)\
                    .filter(Loan_History.amount == repayment.amount_paid)\
                    .first()
                if not loan_history:
                    continue
                guarantor_paid = loan_history.guarantor_paid
                borrowerId = loan_history.borrowerId
                guarantorId = loan_history.guarantorId
                amount = loan_history.amount

            borrower = db.query(Members).filter(Members.memberId == borrowerId).first()

            if guarantor_paid and guarantorId:
                guarantor = db.query(Members).filter(Members.memberId == guarantorId).first()
                paid_by = f"{guarantor.firstName} {guarantor.lastName} (Guarantor)"
            else:
                paid_by = f"{borrower.firstName} {borrower.lastName} (Borrower)"

            repayments_list.append({
                "borrower": f"{borrower.firstName} {borrower.lastName}",
                "amount_borrowed": amount,
                "interest_paid": float(repayment.interest_paid),
                "amount_paid": float(repayment.amount_paid),
                "date_paid": repayment.date_paid,
                "paid_by": paid_by,
                "guarantor_paid": guarantor_paid
            })

            total_borrowed_interest += float(repayment.interest_paid)

        db.close()
        return {
            'total_borrowed_interest': total_borrowed_interest,
            'repayment_details': repayments_list
        }

    except Exception as e:
        print(f"Error fetching borrowed interests: {e}")
        return []
def calculate_current_interest(loanId):
    print(f"Calculating interest for loan {loanId}")
    try:
        db = SessionLocal()

        loan = db.query(Loans).filter(Loans.loanId == loanId).first()
        if not loan:
            return {"error": "Loan not found"}

        today = date.today()
        due_date = loan.due_date
        guarantor_due_date = due_date + timedelta(days=10)

        amount = float(loan.amount)

        # get total already repaid
        total_repaid = float(db.query(func.sum(Loan_Repayments.amount_paid))\
            .filter(Loan_Repayments.loanId == loanId)\
            .scalar() or 0)

        remaining_principal = amount - total_repaid

        interest = amount * 0.20
        total_owed = remaining_principal + interest

        # not yet due
        if today < due_date:
            days_to_due = (due_date - today).days
            return {
                "loanId": loanId,
                "amount_borrowed": amount,
                "total_repaid": total_repaid,
                "remaining_principal": remaining_principal,
                "due_date": due_date,
                "days_to_due": days_to_due,
                "interest_owed": 0,
                "total_owed": remaining_principal,
                "guarantor_due_date": guarantor_due_date,
                "guarantor_must_pay": False,
                "message": f"Loan not yet due. {days_to_due} days remaining"
            }

        # past due, guarantor not yet on hook
        if due_date <= today < guarantor_due_date:
            days_past_due = (today - due_date).days
            return {
                "loanId": loanId,
                "amount_borrowed": amount,
                "total_repaid": total_repaid,
                "remaining_principal": remaining_principal,
                "due_date": due_date,
                "days_past_due": days_past_due,
                "interest_owed": interest,
                "total_owed": total_owed,
                "guarantor_due_date": guarantor_due_date,
                "guarantor_must_pay": False,
                "message": f"Loan is {days_past_due} days overdue. Borrower should pay {total_owed}"
            }

        # 10+ days past due — guarantor on hook
        if today >= guarantor_due_date:
            days_past_due = (today - due_date).days
            guarantor = db.query(Members).filter(Members.memberId == loan.guarantorId).first() if loan.guarantorId else None
            return {
                "loanId": loanId,
                "amount_borrowed": amount,
                "total_repaid": total_repaid,
                "remaining_principal": remaining_principal,
                "due_date": due_date,
                "days_past_due": days_past_due,
                "interest_owed": interest,
                "total_owed": total_owed,
                "guarantor_due_date": guarantor_due_date,
                "guarantor_must_pay": True,
                "guarantor": f"{guarantor.firstName} {guarantor.lastName}" if guarantor else "No guarantor",
                "message": f"Loan is {days_past_due} days overdue. {'Guarantor ' + guarantor.firstName + ' must pay ' + str(total_owed) if guarantor else 'No guarantor assigned'}"
            }

        db.close()

    except Exception as e:
        print(f"Error calculating interest: {e}")
        return {}
def calculate_interest_distribution():
    print("Calculating interest distribution")
    try:
        db = SessionLocal()

        current_period = db.query(Financial_Periods)\
            .filter(Financial_Periods.status == 'open')\
            .first()

        if not current_period:
            return {"error": "No open period found"}

        period_start = current_period.period_start
        period_end = date.today()

        print(f"period_start: {period_start}, period_end: {period_end}")

        if period_start == period_end:
            return {
                "period_start": period_start,
                "period_end": period_end,
                "loan_interest_amount": 0,
                "bank_interest_amount": 0,
                "pools": {
                    "everyone_pool": 0,
                    "borrowers_pool": 0,
                    "guarantors_pool": 0
                },
                "distribution": []
            }
        loan_interest_amount = float(db.query(func.sum(Loan_Repayments.interest_paid))\
            .filter(Loan_Repayments.date_paid >= period_start)\
            .filter(Loan_Repayments.date_paid <= period_end)\
            .scalar() or 0)

        bank_interest_amount = float(db.query(func.sum(Bank_Interests.amount))\
            .filter(Bank_Interests.date >= period_start)\
            .filter(Bank_Interests.date <= period_end)\
            .scalar() or 0)

        all_members = db.query(Members).all()
        if not all_members:
            return {"error": "No members found"}

        total_period_days = (period_end - period_start).days

        def get_active_days(member):
            join_date = member.date_joined
            if join_date <= period_start:
                return total_period_days
            elif period_start < join_date <= period_end:
                return (period_end - join_date).days
            else:
                return 0

        total_weighted_days = sum(get_active_days(m) for m in all_members)

        if total_weighted_days == 0:
            return {"error": "No weighted days calculated"}

        borrowers = db.query(Members)\
            .join(Loan_History, Loan_History.borrowerId == Members.memberId)\
            .filter(Loan_History.paid_date >= period_start)\
            .filter(Loan_History.paid_date <= period_end)\
            .distinct().all()

        guarantors = db.query(Members)\
            .join(Loan_History, Loan_History.guarantorId == Members.memberId)\
            .filter(Loan_History.paid_date >= period_start)\
            .filter(Loan_History.paid_date <= period_end)\
            .distinct().all()

        everyone_pool   = loan_interest_amount * 0.50
        borrowers_pool  = loan_interest_amount * 0.25
        guarantors_pool = loan_interest_amount * 0.25

        borrower_share  = borrowers_pool  / len(borrowers)  if borrowers  else 0
        guarantor_share = guarantors_pool / len(guarantors) if guarantors else 0

        distribution = []
        

        for member in all_members:
            active_days = get_active_days(member)
            if active_days == 0:
                continue

            is_borrower  = member in borrowers
            is_guarantor = member in guarantors

            pro_rated_everyone_share = (active_days / total_weighted_days) * everyone_pool
            pro_rated_bank_share     = (active_days / total_weighted_days) * bank_interest_amount

            loan_interest_share  = pro_rated_everyone_share
            loan_interest_share += borrower_share  if is_borrower  else 0
            loan_interest_share += guarantor_share if is_guarantor else 0

            total_share = loan_interest_share + pro_rated_bank_share

            distribution.append({
                "memberId": member.memberId,
                "member": f"{member.firstName} {member.lastName}",
                "active_days": active_days,
                "is_borrower": is_borrower,
                "is_guarantor": is_guarantor,
                "everyone_pool_share": round(pro_rated_everyone_share, 2),
                "borrower_share": round(borrower_share, 2) if is_borrower else 0,
                "guarantor_share": round(guarantor_share, 2) if is_guarantor else 0,
                "loan_interest_share": round(loan_interest_share, 2),
                "bank_interest_share": round(pro_rated_bank_share, 2),
                "total_share": round(total_share, 2)
            })

        db.close()

        return {
            "period_start": period_start,
            "period_end": period_end,
            "loan_interest_amount": loan_interest_amount,
            "bank_interest_amount": bank_interest_amount,
            "pools": {
                "everyone_pool": everyone_pool,
                "borrowers_pool": borrowers_pool,
                "guarantors_pool": guarantors_pool
            },
            "distribution": distribution
        }

    except Exception as e:
        print(f"Error calculating interest: {e}")
        return {}
def save_interest_distribution():
    try:
        data = calculate_interest_distribution()

        if "error" in data or "message" in data:
            return data

        db = SessionLocal()

        for entry in data['distribution']:
            record = Interest_Distribution(
                memberId=entry['memberId'],
                share_amount=entry['total_share'],
                source='loanInterest',
                dateDistributed=date.today()
            )
            db.add(record)

        db.commit()
        db.close()

        return {"message": "Distribution saved successfully", "distribution": data['distribution']}

    except Exception as e:
        print(f"Error saving distribution: {e}")
        return {}
    
def flag_guarantor_loans():
    print("Flagging loans past due + 10 days")
    try:
        db = SessionLocal()

        today = date.today()

        
        flagged_loans = db.query(Loans)\
            .filter(Loans.status == 'active')\
            .filter(Loans.guarantor_paid == False)\
            .filter(Loans.guarantorId != None)\
            .all()

        if not flagged_loans:
            return {"message": "No loans flagged for guarantor action"}

        flagged_list = []

        for loan in flagged_loans:
            guarantor_due_date = loan.due_date + timedelta(days=10)

            if today >= guarantor_due_date:
                borrower = db.query(Members).filter(Members.memberId == loan.borrowerId).first()
                guarantor = db.query(Members).filter(Members.memberId == loan.guarantorId).first()

                days_overdue = (today - guarantor_due_date).days
                interest = loan.amount * 0.20
                total_owed = (loan.amount - loan.amount_paid) + interest

                flagged_list.append({
                    "loanId": loan.loanId,
                    "borrower": f"{borrower.firstName} {borrower.lastName}",
                    "guarantor": f"{guarantor.firstName} {guarantor.lastName}",
                    "guarantorId": loan.guarantorId,
                    "amount_borrowed": loan.amount,
                    "amount_paid": loan.amount_paid,
                    "interest": interest,
                    "total_owed": total_owed,
                    "due_date": loan.due_date,
                    "guarantor_due_date": guarantor_due_date,
                    "days_overdue": days_overdue,
                    "warning": f"ACTION REQUIRED: {guarantor.firstName} {guarantor.lastName} must pay {total_owed} for {borrower.firstName} {borrower.lastName}'s loan"
                })

        db.close()

        return {
            "total_flagged": len(flagged_list),
            "flagged_loans": flagged_list
        }

    except Exception as e:
        print(f"Error flagging loans: {e}")
        return {}
def total_savings():
    print("Fetching all savings")
    try:
        db = SessionLocal()

        members = db.query(Members).all()
        savings_list = []

        current_month = datetime.now().month
        current_year = datetime.now().year
        grand_total = 0 

        for member in members:
            total_savings = db.query(func.sum(Savings.amount))\
                .filter(Savings.memberId == member.memberId)\
                .scalar() or 0

            saved_this_month = db.query(Savings)\
                .filter(Savings.memberId == member.memberId)\
                .filter(func.extract('month', Savings.date_saved) == current_month)\
                .filter(func.extract('year', Savings.date_saved) == current_year)\
                .first()            

            savings_list.append({
                "first_name": member.firstName,
                "last_name": member.lastName,
                "total_savings": total_savings,
                "paid_this_month": True if saved_this_month else False
            })

            grand_total += total_savings  # add each member's savings to total

        db.close()

        # now return both the list and the summary
        return {
            "total_savings": grand_total,
            "total_members": len(members),
            "members": savings_list
        }

    except Exception as e:
        print(f"Error fetching savings: {e}")
        return {}
    
def bank_interests():
    try:
        db = SessionLocal()

        total_interest = db.query(func.sum(Bank_Interests.amount))\
            .scalar() or 0
        total_members=db.query(Members).count()
        each_members_amount= total_interest/total_members

        db.close()

        return {
            "total_members":total_members,
            "total_interest": total_interest,
            "each_members_amount":each_members_amount
        }

    except Exception as e:
        print(f"Error fetching bank interests: {e}")
        return {}
    

def get_current_period():
    try:
        db = SessionLocal()
        current = db.query(Financial_Periods)\
            .filter(Financial_Periods.status == 'open')\
            .first()
        db.close()

        if not current:
            return {"error": "No open period found"}

        return {
            "periodId": current.periodId,
            "period_start": current.period_start
        }

    except Exception as e:
        print(f"Error fetching current period: {e}")
        return {}


def close_financial_year(admin_id):
    try:
        db = SessionLocal()

        # reuse get_current_period instead of duplicating the query
        current_period_data = get_current_period()
        if "error" in current_period_data:
            return current_period_data

        current_period = db.query(Financial_Periods)\
            .filter(Financial_Periods.periodId == current_period_data['periodId'])\
            .first()

        today = date.today()

        current_period.period_end = today
        current_period.status = 'closed'
        current_period.closed_by = admin_id

        new_period = Financial_Periods(
            period_start=today,
            period_end=None,
            status='open'
        )

        db.add(new_period)
        db.commit()
        db.close()

        return {
            "message": "Financial year closed successfully",
            "closed_period": {
                "period_start": current_period.period_start,
                "period_end": today
            },
            "new_period_start": today
        }

    except Exception as e:
        print(f"Error closing financial year: {e}")
        return {}
    
def request_loan():
    try:
        db = SessionLocal()
        data = request.get_json()

        memberId = data['memberId']
        amount = float(data['amount'])
        guarantorId = data.get('guarantorId', None)

        total_savings = float(db.query(func.sum(Savings.amount))\
            .filter(Savings.memberId == memberId)\
            .scalar() or 0)

        total_active_loans = float(db.query(func.sum(Loans.amount))\
            .filter(Loans.borrowerId == memberId)\
            .filter(Loans.status == 'active')\
            .scalar() or 0)

        max_without_guarantor = total_savings * 0.75
        remaining_viability = max_without_guarantor - total_active_loans
        needs_guarantor = amount > remaining_viability

        if needs_guarantor and not guarantorId:
            return jsonify({"error": "This loan requires a guarantor"}), 400

        status = 'pending_guarantor' if needs_guarantor else 'pending_admin'

        new_request = Loan_Requests(
            memberId=memberId,
            guarantorId=guarantorId,
            amount=amount,
            date_requested=date.today(),
            status=status
        )

        db.add(new_request)
        db.commit()

        # get the id before closing session
        request_id = new_request.requestId

        if needs_guarantor:
            confirmation = Guarantor_Confirmations(
                requestId=request_id,
                guarantorId=guarantorId,
                status='pending'
            )
            db.add(confirmation)
            db.commit()

        db.close()

        return jsonify({
            "message": "Loan request submitted successfully",
            "requestId": request_id,
            "status": status,
            "needs_guarantor": needs_guarantor
        }), 201

    except Exception as e:
        print(f"Error requesting loan: {e}")
        return jsonify({"error": str(e)}), 500

def guarantor_confirm(requestId, guarantorId, decision):
    try:
        db = SessionLocal()

        # find the confirmation record
        confirmation = db.query(Guarantor_Confirmations)\
            .filter(Guarantor_Confirmations.requestId == requestId)\
            .filter(Guarantor_Confirmations.guarantorId == guarantorId)\
            .first()

        if not confirmation:
            return jsonify({"error": "Confirmation record not found"}), 404

        if decision == 'confirmed':
            confirmation.status = 'confirmed'
            confirmation.responded_at = date.today()

            # move loan request to pending_admin
            loan_request = db.query(Loan_Requests)\
                .filter(Loan_Requests.requestId == requestId).first()
            loan_request.status = 'pending_admin'

        elif decision == 'declined':
            confirmation.status = 'declined'
            confirmation.responded_at = date.today()

            # cancel the loan request
            loan_request = db.query(Loan_Requests)\
                .filter(Loan_Requests.requestId == requestId).first()
            loan_request.status = 'rejected'

        db.commit()
        db.close()

        return jsonify({
            "message": f"Loan request {decision} by guarantor",
            "requestId": requestId
        }), 200

    except Exception as e:
        print(f"Error confirming loan: {e}")
        return jsonify({"error": str(e)}), 500


def admin_verify_loan(requestId, adminId):
    try:
        db = SessionLocal()

        loan_request = db.query(Loan_Requests)\
            .filter(Loan_Requests.requestId == requestId)\
            .filter(Loan_Requests.status == 'pending_admin')\
            .first()

        if not loan_request:
            return jsonify({"error": "Loan request not found or not ready for approval"}), 404

        # calculate due date
        due_date = calculate_due_date(loan_request.amount, date.today())

        # save to Loans table
        new_loan = Loans(
            borrowerId=loan_request.memberId,
            guarantorId=loan_request.guarantorId,
            amount=loan_request.amount,
            date_borrowed=date.today(),
            due_date=due_date,
            status='active',
            amount_paid=0,
            guarantor_paid=False
        )

        db.add(new_loan)

        # update request status
        loan_request.status = 'approved'
        loan_request.reviewed_by = adminId
        loan_request.reviewed_at = date.today()

        db.commit()
        db.close()

        return jsonify({
            "message": "Loan approved and activated",
            "due_date": due_date
        }), 200

    except Exception as e:
        print(f"Error verifying loan: {e}")
        return jsonify({"error": str(e)}), 500


def get_pending_requests():
    try:
        db = SessionLocal()

        # for admin — all pending_admin requests
        pending = db.query(Loan_Requests)\
            .filter(Loan_Requests.status == 'pending_admin')\
            .all()

        pending_list = []
        for req in pending:
            member = db.query(Members).filter(Members.memberId == req.memberId).first()
            guarantor = db.query(Members).filter(Members.memberId == req.guarantorId).first() if req.guarantorId else None

            pending_list.append({
                "requestId": req.requestId,
                "member": f"{member.firstName} {member.lastName}",
                "amount": req.amount,
                "date_requested": req.date_requested,
                "guarantor": f"{guarantor.firstName} {guarantor.lastName}" if guarantor else "None",
                "status": req.status
            })

        db.close()
        return jsonify(pending_list), 200

    except Exception as e:
        print(f"Error fetching pending requests: {e}")
        return jsonify({"error": str(e)}), 500


def get_guarantor_notifications(guarantorId):
    try:
        db = SessionLocal()

        pending = db.query(Guarantor_Confirmations)\
            .filter(Guarantor_Confirmations.guarantorId == guarantorId)\
            .filter(Guarantor_Confirmations.status == 'pending')\
            .all()

        notifications = []
        for confirmation in pending:
            loan_request = db.query(Loan_Requests)\
                .filter(Loan_Requests.requestId == confirmation.requestId).first()
            borrower = db.query(Members)\
                .filter(Members.memberId == loan_request.memberId).first()

            notifications.append({
                "confirmationId": confirmation.confirmationId,
                "requestId": confirmation.requestId,
                "borrower": f"{borrower.firstName} {borrower.lastName}",
                "amount": loan_request.amount,
                "date_requested": loan_request.date_requested
            })

        db.close()
        return jsonify(notifications), 200

    except Exception as e:
        print(f"Error fetching notifications: {e}")
        return jsonify({"error": str(e)}), 500  

def request_saving():
    try:
        db = SessionLocal()
        data = request.get_json()

        new_request = Savings_Requests(
            memberId=data['memberId'],
            amount=data['amount'],
            date_requested=date.today(),
            status='pending'
        )

        db.add(new_request)
        db.commit()
        db.close()

        return jsonify({
            "message": "Savings request submitted successfully",
            "amount": data['amount']
        }), 201

    except Exception as e:
        print(f"Error submitting savings request: {e}")
        return jsonify({"error": str(e)}), 500


def approve_saving(requestId, adminId):
    try:
        db = SessionLocal()

        saving_request = db.query(Savings_Requests)\
            .filter(Savings_Requests.requestId == requestId)\
            .filter(Savings_Requests.status == 'pending')\
            .first()

        if not saving_request:
            return jsonify({"error": "Savings request not found"}), 404

        # add to savings table
        new_saving = Savings(
            memberId=saving_request.memberId,
            amount=saving_request.amount,
            date_saved=date.today()
        )

        db.add(new_saving)

        # update request status
        saving_request.status = 'approved'
        saving_request.approved_by = adminId
        saving_request.approved_at = date.today()

        db.commit()
        db.close()

        return jsonify({"message": "Savings approved and recorded"}), 200

    except Exception as e:
        print(f"Error approving saving: {e}")
        return jsonify({"error": str(e)}), 500


def get_pending_savings():
    try:
        db = SessionLocal()

        pending = db.query(Savings_Requests)\
            .filter(Savings_Requests.status == 'pending')\
            .all()

        pending_list = []
        for req in pending:
            member = db.query(Members)\
                .filter(Members.memberId == req.memberId).first()

            pending_list.append({
                "requestId": req.requestId,
                "member": f"{member.firstName} {member.lastName}",
                "amount": req.amount,
                "date_requested": req.date_requested,
                "status": req.status
            })

        db.close()
        return jsonify(pending_list), 200

    except Exception as e:
        print(f"Error fetching pending savings: {e}")
        return jsonify({"error": str(e)}), 500
def mark_paid_by_borrower(loanId):
    try:
        db = SessionLocal()

        loan = db.query(Loans).filter(Loans.loanId == loanId).first()
        if not loan:
            return jsonify({"error": "Loan not found"}), 404
        if loan.status == 'paid':
            return jsonify({"error": "Loan already paid"}), 400

        amount = float(loan.amount)
        borrowerId = loan.borrowerId
        guarantorId = loan.guarantorId
        date_borrowed = loan.date_borrowed
        due_date = loan.due_date
        interest = amount * 0.20
        total_owed = amount + interest

        # record repayment
        repayment = Loan_Repayments(
            loanId=loanId,
            amount_paid=amount,
            interest_paid=interest,
            paid_by=borrowerId,
            date_paid=date.today()
        )
        db.add(repayment)


        history = Loan_History(
            loanId=loanId,
            borrowerId=borrowerId,
            guarantorId=guarantorId,
            amount=amount,
            date_borrowed=date_borrowed,
            due_date=due_date,
            paid_date=date.today(),
            guarantor_paid=False,
            interest_paid=interest
        )
        db.add(history)

        # delete from active loans
        db.delete(loan)
        db.commit()
        db.close()

        return jsonify({
            "message": "Loan marked as paid by borrower",
            "amount_paid": amount,
            "interest_paid": interest,
            "total_paid": total_owed
        }), 200

    except Exception as e:
        print(f"Error marking loan paid: {e}")
        return jsonify({"error": str(e)}), 500


def mark_paid_by_guarantor(loanId):
    try:
        db = SessionLocal()

        loan = db.query(Loans).filter(Loans.loanId == loanId).first()
        if not loan:
            return jsonify({"error": "Loan not found"}), 404
        if loan.status == 'paid':
            return jsonify({"error": "Loan already paid"}), 400

        amount = float(loan.amount)
        borrowerId = loan.borrowerId
        guarantorId = loan.guarantorId
        date_borrowed = loan.date_borrowed
        due_date = loan.due_date
        interest = amount * 0.20
        total_owed = amount + interest

        repayment = Loan_Repayments(
            loanId=loanId,
            amount_paid=amount,
            interest_paid=interest,
            paid_by=guarantorId,
            date_paid=date.today()
        )
        db.add(repayment)

        history = Loan_History(
            loanId=loanId,
            borrowerId=borrowerId,
            guarantorId=guarantorId,
            amount=amount,
            date_borrowed=date_borrowed,
            due_date=due_date,
            paid_date=date.today(),
            guarantor_paid=True,
            interest_paid=interest
        )
        db.add(history)

        db.delete(loan)
        db.commit()
        db.close()

        return jsonify({
            "message": "Loan marked as paid by guarantor",
            "amount_paid": amount,
            "interest_paid": interest,
            "total_paid": total_owed
        }), 200

    except Exception as e:
        print(f"Error marking loan paid by guarantor: {e}")
        return jsonify({"error": str(e)}), 500

def add_bank_interest():
    try:
        db = SessionLocal()
        data = request.get_json()

        amount = float(data['amount'])
        total_members = db.query(Members).count()

        new_interest = Bank_Interests(
            amount=amount,
            date=date.today()
        )

        db.add(new_interest)
        db.commit()
        db.close()

        return jsonify({
            "message": "Bank interest recorded",
            "amount": amount,
            "total_members": total_members,
            "each_member_gets": round(amount / total_members, 2)
        }), 201

    except Exception as e:
        print(f"Error adding bank interest: {e}")
        return jsonify({"error": str(e)}), 500    