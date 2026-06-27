from sqlalchemy import Column, ForeignKey, Integer, String, Enum, Date, DateTime, Numeric, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from Config import Base


class Members(Base):
    __tablename__ = 'Members'

    memberId = Column(Integer, primary_key=True, autoincrement=True)
    firstName = Column(String(20))
    lastName = Column(String(20))
    email = Column(String(255))
    phone = Column(String(55))
    roles = Column(Enum('Admin', 'Member',name='roles_enum'))
    date_joined = Column(Date)
    created_at = Column(DateTime, default=datetime.utcnow)
    password=Column(String(255))
    loans_taken = relationship('Loans', foreign_keys='Loans.borrowerId', back_populates='borrower')
    loans_guaranteed = relationship('Loans', foreign_keys='Loans.guarantorId', back_populates='guarantor')


class Savings(Base):
    __tablename__ = 'Savings'

    savingsId = Column(Integer, primary_key=True, autoincrement=True)
    memberId = Column(Integer, ForeignKey('Members.memberId'))
    amount = Column(Numeric(15, 2))
    date_saved = Column(Date)

    member = relationship('Members')


class Loans(Base):
    __tablename__ = 'Loans'

    loanId = Column(Integer, primary_key=True, autoincrement=True)
    borrowerId = Column(Integer, ForeignKey('Members.memberId'))
    guarantorId = Column(Integer, ForeignKey('Members.memberId'), nullable=True)
    amount = Column(Numeric(15, 2))
    date_borrowed = Column(Date)
    due_date = Column(Date)
    status = Column(Enum('active', 'paid', 'defaulted', name='loan_active_status'))
    amount_paid = Column(Numeric(15, 2))
    paid_date = Column(Date)
    guarantor_paid = Column(Boolean, default=False)

    borrower = relationship('Members', foreign_keys=[borrowerId], back_populates='loans_taken')
    guarantor = relationship('Members', foreign_keys=[guarantorId], back_populates='loans_guaranteed')


class Loan_Repayments(Base):
    __tablename__ = 'Loan_Repayments'

    repaymentId = Column(Integer, primary_key=True, autoincrement=True)
    loanId = Column(Integer, ForeignKey('Loans.loanId', ondelete='SET NULL'), nullable=True)
    amount_paid = Column(Numeric(15, 2))
    interest_paid = Column(Numeric(15, 2))
    paid_by = Column(Integer, ForeignKey('Members.memberId'))
    date_paid = Column(Date)

    loan = relationship('Loans')
    payer = relationship('Members')


class Bank_Interests(Base):
    __tablename__ = 'Bank_Interests'

    interestId = Column(Integer, primary_key=True, autoincrement=True)
    amount = Column(Numeric(15, 2))
    date = Column(Date)
    


class Interest_Distribution(Base):
    __tablename__ = 'Interest_Distribution'
    distributionId = Column(Integer, primary_key=True, autoincrement=True)
    interestId = Column(Integer, ForeignKey('Bank_Interests.interestId'))
    memberId = Column(Integer, ForeignKey('Members.memberId'))
    share_amount = Column(Numeric(15, 2))
    source = Column(Enum('loanInterest', 'bankInterest', name='interest_source'))
    dateDistributed = Column(Date)
    bank_interest = relationship('Bank_Interests')
    member = relationship('Members')

class Financial_Periods(Base):
    __tablename__ = 'Financial_Periods'

    periodId = Column(Integer, primary_key=True, autoincrement=True)
    period_start = Column(Date)
    period_end = Column(Date, nullable=True)
    closed_by = Column(Integer, ForeignKey('Members.memberId'), nullable=True)
    closed_at = Column(DateTime, default=datetime.utcnow)
    status = Column(Enum('open', 'closed', name='financial_status'), default='open')

    closed_by_member = relationship('Members')


class Loan_Requests(Base):
    __tablename__ = 'Loan_Requests'

    requestId = Column(Integer, primary_key=True, autoincrement=True)
    memberId = Column(Integer, ForeignKey('Members.memberId'))
    guarantorId = Column(Integer, ForeignKey('Members.memberId'), nullable=True)
    amount = Column(Numeric(15, 2))
    date_requested = Column(Date)
    status = Column(Enum('pending_guarantor', 'pending_admin', 'approved', 'rejected', name='loan_status'), default='pending_guarantor')
    reviewed_by = Column(Integer, ForeignKey('Members.memberId'), nullable=True)
    reviewed_at = Column(Date, nullable=True)

    member = relationship('Members', foreign_keys=[memberId])
    guarantor = relationship('Members', foreign_keys=[guarantorId])
    reviewer = relationship('Members', foreign_keys=[reviewed_by])


class Guarantor_Confirmations(Base):
    __tablename__ = 'Guarantor_Confirmations'

    confirmationId = Column(Integer, primary_key=True, autoincrement=True)
    requestId = Column(Integer, ForeignKey('Loan_Requests.requestId'))
    guarantorId = Column(Integer, ForeignKey('Members.memberId'))
    status = Column(Enum('pending', 'confirmed', 'declined', name='guarantor_status'), default='pending')
    responded_at = Column(Date, nullable=True)

    loan_request = relationship('Loan_Requests')
    guarantor = relationship('Members')

class Savings_Requests(Base):
    __tablename__ = 'Savings_Requests'

    requestId = Column(Integer, primary_key=True, autoincrement=True)
    memberId = Column(Integer, ForeignKey('Members.memberId'))
    amount = Column(Numeric(15, 2))
    date_requested = Column(Date)
    status = Column(Enum('pending', 'approved', 'rejected',name='savings_status'), default='pending')
    approved_by = Column(Integer, ForeignKey('Members.memberId'), nullable=True)
    approved_at = Column(Date, nullable=True)

    member = relationship('Members', foreign_keys=[memberId])
    approver = relationship('Members', foreign_keys=[approved_by])

class Loan_History(Base):
    __tablename__ = 'Loan_History'

    historyId = Column(Integer, primary_key=True, autoincrement=True)
    loanId = Column(Integer)
    borrowerId = Column(Integer, ForeignKey('Members.memberId'))
    guarantorId = Column(Integer, ForeignKey('Members.memberId'), nullable=True)
    amount = Column(Numeric(15, 2))
    date_borrowed = Column(Date)
    due_date = Column(Date)
    paid_date = Column(Date)
    guarantor_paid = Column(Boolean)
    interest_paid = Column(Numeric(15, 2))    
