from flask_jwt_extended import get_jwt_identity, jwt_required

from Admin.views import add_bank_interest, admin_verify_loan, approve_saving, calculate_interest_distribution, close_financial_year, get_current_period, get_guarantor_notifications, get_pending_requests, get_pending_savings, guarantor_confirm, mark_paid_by_borrower, mark_paid_by_guarantor, request_loan, request_saving, save_interest_distribution, view_members,max_loan_no_guarantor,view_all_savings,loan_viability,calculate_due_date,view_all_borrowers,view_borrowed_interests
from flask import Blueprint, jsonify, request 
from Admin.views import create_loan,view_guarantor_details,calculate_current_interest,add_member,flag_guarantor_loans,total_savings,bank_interests
from Admin.auth import SignUp,SignIn, ForgotPassword, SetPassword
Admin_bp=Blueprint('Chama',__name__)

@Admin_bp.route('/Members',methods=['GET'])
@jwt_required()
def get_all_members():
    current_user = get_jwt_identity() 
    print(f"Request from member ID: {current_user}")
    return view_members()

@Admin_bp.route('/max_loan_no_guarantor',methods=['GET'])
@jwt_required()
def get_maximum_loan():
    current_user = get_jwt_identity() 
    print(f"Request from member ID: {current_user}")
    return max_loan_no_guarantor()
@Admin_bp.route('/view_all_savings',methods=['GET'])
@jwt_required()
def get_all_savings():
    current_user = get_jwt_identity() 
    print(f"Request from member ID: {current_user}")
    return view_all_savings()

@Admin_bp.route('/calculate_due_date',methods=['POST'])
@jwt_required()
def get_the_due_date():
    current_user = get_jwt_identity() 
    print(f"Request from member ID: {current_user}")
    return calculate_due_date()
@Admin_bp.route('/create_loan',methods=['POST'])
@jwt_required()
def post_create_loan():
    current_user = get_jwt_identity() 
    print(f"Request from member ID: {current_user}")
    return create_loan()
@Admin_bp.route('/view_all_borrowers',methods=['GET'])
@jwt_required()
def view_borrowers():
    current_user = get_jwt_identity() 
    print(f"Request from member ID: {current_user}")
    return view_all_borrowers()
@Admin_bp.route('/view_guarantor_details',methods=['POST'])
@jwt_required()
def view_guarantor_detail():
    current_user = get_jwt_identity() 
    print(f"Request from member ID: {current_user}")
    return view_guarantor_details()
@Admin_bp.route('/calculate_current_interest',methods=['POST'])
@jwt_required()
def interest_from_loans():
    current_user = get_jwt_identity() 
    print(f"Request from member ID: {current_user}")
    return calculate_current_interest()


@Admin_bp.route('/flag_guarantor_loans',methods=['GET'])
@jwt_required()
def guarantor_pays():
    current_user = get_jwt_identity() 
    print(f"Request from member ID: {current_user}")
    return flag_guarantor_loans()
@Admin_bp.route('/Total_savings',methods=['GET'])
@jwt_required()
def get_total_savings():
    current_user = get_jwt_identity() 
    print(f"Request from member ID: {current_user}")
    return total_savings()

@Admin_bp.route('/view_borrowed_interests',methods=['GET'])
@jwt_required()
def get_view_borrowed_interests():
    current_user = get_jwt_identity() 
    print(f"Request from member ID: {current_user}")
    return view_borrowed_interests()
@Admin_bp.route('/bank_interests',methods=['GET'])
@jwt_required()
def get_bank_interests():
    current_user = get_jwt_identity() 
    print(f"Request from member ID: {current_user}")
    return bank_interests()
@Admin_bp.route('/add_member',methods=['POST'])
@jwt_required()
def post_add_members():
    current_user = get_jwt_identity() 
    print(f"Request from member ID: {current_user}")
    return add_member()
# just view — safe to call anytime
@Admin_bp.route('/distribute_interest', methods=['GET'])
@jwt_required()
def interest_distribution_route():
    current_user = get_jwt_identity() 
    print(f"Request from member ID: {current_user}")
    return (calculate_interest_distribution())

@Admin_bp.route('/distribute_interest/save', methods=['POST'])
@jwt_required()
def save_distribution_route():
    current_user = get_jwt_identity() 
    print(f"Request from member ID: {current_user}")
    return jsonify(save_interest_distribution())
@Admin_bp.route('/close_year', methods=['POST'])
@jwt_required()
def close_year_route():
    current_user = get_jwt_identity() 
    print(f"Request from member ID: {current_user}")
    data = request.get_json()
    return jsonify(close_financial_year(data['admin_id']))

@Admin_bp.route('/SignUp',methods=['POST'])
def signing_up():
    
    return SignUp()
@Admin_bp.route('/SignIn',methods=['POST'])
def signing_in():
    
    return SignIn()

@Admin_bp.route('/request_loan', methods=['POST'])
@jwt_required()
def post_request_loan():
    return request_loan()

@Admin_bp.route('/guarantor_confirm', methods=['POST'])
@jwt_required()
def post_guarantor_confirm():
    data = request.get_json()
    return guarantor_confirm(data['requestId'], data['guarantorId'], data['decision'])

@Admin_bp.route('/admin_verify_loan', methods=['POST'])
@jwt_required()
def post_admin_verify_loan():
    data = request.get_json()
    return admin_verify_loan(data['requestId'], data['adminId'])

@Admin_bp.route('/pending_requests', methods=['GET'])
@jwt_required()
def get_all_pending_requests():
    return get_pending_requests()

@Admin_bp.route('/guarantor_notifications/<int:guarantorId>', methods=['GET'])
@jwt_required()
def get_notifications(guarantorId):
    return get_guarantor_notifications(guarantorId)

@Admin_bp.route('/loan_viability', methods=['POST'])
@jwt_required()
def get_loan_viability():
    current_user = get_jwt_identity()
    print(f"Request from member ID: {current_user}")
    data = request.get_json()
    return jsonify(loan_viability(data['memberId'], data['requested_amount']))
@Admin_bp.route('/request_saving', methods=['POST'])
@jwt_required()
def post_request_saving():
    return request_saving()

@Admin_bp.route('/pending_savings', methods=['GET'])
@jwt_required()
def get_all_pending_savings():
    return get_pending_savings()

@Admin_bp.route('/approve_saving', methods=['POST'])
@jwt_required()
def post_approve_saving():
    data = request.get_json()
    return approve_saving(data['requestId'], data['adminId'])
@Admin_bp.route('/current_period', methods=['GET'])
@jwt_required()
def current_period_route():
    return jsonify(get_current_period())
@Admin_bp.route('/mark_paid_borrower', methods=['POST'])
@jwt_required()
def paid_by_borrower():
    data = request.get_json()
    return mark_paid_by_borrower(data['loanId'])

@Admin_bp.route('/mark_paid_guarantor', methods=['POST'])
@jwt_required()
def paid_by_guarantor():
    data = request.get_json()
    return mark_paid_by_guarantor(data['loanId'])
@Admin_bp.route('/add_bank_interest', methods=['POST'])
@jwt_required()
def post_bank_interest():
    current_user = get_jwt_identity()
    print(f"Request from member ID: {current_user}")
    return add_bank_interest()


@Admin_bp.route('/forgot_password', methods=['POST'])
def forgot_password_route():
    return ForgotPassword()

@Admin_bp.route('/set_password', methods=['POST'])
def set_password_route():
    return SetPassword()