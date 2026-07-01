# Premier Savings Chama — Chama Ledger

A web-based savings and loan management system for a rotating savings group (chama). Built to digitize member savings tracking, 
loan management, interest distribution, and financial period management.

---

### Backend

```bash
# clone the repo
git clone https://github.com/your-username/premier-savings-chama.git
cd premier-savings-chama/Backend

# install dependencies
pip install -r requirements.txt

# set environment variables
# create a .env file or set directly:
export DATABASE_URL="mysql+pymysql://root:password@localhost/premier_savings_chama"
export JWT_SECRET_KEY="your-secret-key"

# run the app
python main.py
```
### Frontend
Open `Frontend/index.html` with Live Server in VS Code.
The `config.js` file automatically detects the environment:
- Local: points to `http://127.0.0.1:5000`
- Production: points to the Render backend URL
- 
## Live Demo
- **Frontend:** https://premiersavingchama.netlify.app
- **Backend API:** https://premier-savings-chama.onrender.com

## Tech Stack

**Backend**
- Python 3.14
- Flask
- SQLAlchemy (ORM)
- Flask-JWT-Extended (authentication)
- Flask-CORS
- Gunicorn (production server)
- psycopg2 (PostgreSQL driver)

**Frontend**
- HTML, CSS, JavaScript (vanilla)
- Hosted on Netlify

**Database**
- PostgreSQL via Supabase

**Deployment**
- Backend: Render
- Frontend: Netlify
- Database: Supabase

---

## Features

### Members
- Admin can add members
- Members can sign up, sign in, reset password
- Role-based access — Admin and Member roles
- JWT authentication with 7-day token expiry

### Savings
- Members submit savings requests from their dashboard
- Admin approves savings — amount is then recorded
- Total savings tracked per member and across the chama

### Loans
- Members request loans from the loans page
- System checks loan viability against 75% of savings
- Loans above 75% of savings require a guarantor
- Guarantor receives a notification and must confirm before request goes to admin
- Admin verifies and approves loan — activates it in the system
- Due dates calculated automatically based on loan amount (every Ksh 20,000 = 1 month)
- Admin marks loans as paid by borrower or guarantor
- Paid loans are archived to loan history

### Interest
- Loan interest: 20% flat on principal, charged at due date
- If 10 days past due, guarantor is responsible
- Interest from repayments split 50/25/25:
  - 50% shared equally among all members (pro-rated by join date)
  - 25% shared equally among borrowers
  - 25% shared equally among guarantors
- Bank interest entered by admin, split equally among all members
- Pro-rated for members who joined mid-period

### Financial Periods
- Admin closes financial year from the admin page
- New period begins automatically on close date
- Interest distribution is calculated per open period
- First period starts from earliest member join date

### Admin Page
- View and approve pending loan requests
- View and approve pending savings requests
- Close financial year
- Mark loans as paid
- Add bank interest

---

## Project Structure

```
├── Backend/
│   ├── main.py              # Flask app entry point
│   ├── Config.py            # Database configuration
│   ├── requirements.txt     # Python dependencies
│   └── Admin/
│       ├── models.py        # SQLAlchemy models
│       ├── views.py         # Business logic functions
│       ├── routes.py        # Flask blueprint routes
│       └── auth.py          # Authentication functions
├── Frontend/
│   ├── config.js            # API base URL config
│   ├── members.css          # Main stylesheet
│   ├── Style.css            # Auth page stylesheet
│   ├── index.html           # Login/signup page
│   ├── Dashboard.html       # Main dashboard
│   ├── Members.html         # Members management
│   ├── loans.html           # Loans page
│   ├── interest.html        # Interest distribution
│   ├── admin.html           # Admin-only page
│   └── Fines.html           # Fines page (coming soon)
└── chama.sql                # Database schema
```

---

## Database Schema

| Table | Purpose |
|---|---|
| Members | Chama members with roles |
| Savings | Approved member savings |
| Savings_Requests | Pending savings awaiting admin approval |
| Loans | Active loans |
| Loan_Requests | Pending loan requests |
| Loan_History | Paid/archived loans |
| Loan_Repayments | Repayment records with interest |
| Guarantor_Confirmations | Guarantor responses to loan requests |
| Bank_Interests | Bank interest amounts entered by admin |
| Interest_Distribution | Per-member interest share records |
| Financial_Periods | Open and closed financial periods |

---

## Business Rules

- Minimum monthly savings: **Ksh 1,000**
- Late savings fine: **Ksh 300/month**
- Maximum loan without guarantor: **75% of total savings**
- Loan repayment periods: Ksh 20,000 per month (e.g. Ksh 40,000 = 2 months)
- Loan interest: **20% flat on principal**
- Guarantor steps in: **10 days after due date**
- Interest distribution: **50% everyone / 25% borrowers / 25% guarantors**
- Mid-year joiners get pro-rated interest share from their join date

---

## Local Setup

### Prerequisites
- Python 3.10+
- MySQL (for local development)
- Node.js (optional, for Live Server)

---
## Deployment

### Database (Supabase)
1. Create a project at supabase.com
2. Run `chama.sql` in the SQL Editor
3. Copy the **Transaction pooler** connection string (port 6543)

### Backend (Render)
1. Connect your GitHub repo
2. Set root directory to `Backend`
3. Build command: `pip install -r requirements.txt`
4. Start command: `gunicorn main:app`
5. Add environment variables:
   - `DATABASE_URL` — Supabase pooler connection string
   - `JWT_SECRET_KEY` — your secret key

### Frontend (Netlify)
1. Connect your GitHub repo
2. Set base directory to `Frontend`
3. Leave build command empty
4. Set publish directory to `Frontend`

## Authors
Wahu Muchemi
---

## License

This project is for academic and personal use.
