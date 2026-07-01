from Admin.models import Members
from Config import SessionLocal
from flask import request, jsonify
from flask_jwt_extended import create_access_token
import hashlib


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def SignUp():
    print("Trying to sign member up")
    try:
        db = SessionLocal()
        data = request.get_json()

        existing = db.query(Members).filter((Members.email == data['email']) | (Members.phone == data['phone'])).first()
        if existing:
            return jsonify({"error": "Member already exists"}), 409

        new_member = Members(
            firstName=data['firstName'],
            lastName=data['lastName'],
            email=data['email'],
            phone=data['phone'],
            roles=data['roles'],
            date_joined=data['date_joined'],
            password=hash_password(data['password'])
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


def SignIn():
    print("Trying to log member in")
    try:
        db = SessionLocal()
        data = request.get_json()

        user = db.query(Members).filter(Members.email == data['email']).first()

        if not user:
            return jsonify({"error": "Member does not exist"}), 404

        # check password against stored hash
        if user.password != hash_password(data['password']):
            return jsonify({"error": "Incorrect email or password"}), 401
        # create token with user info inside
        token = create_access_token(identity=str(user.memberId))
        db.close()
        return jsonify({
            "message": "Logged in successfully",
            "memberId": user.memberId,
            "token":token,
            "name": f"{user.firstName} {user.lastName}",
            "role": user.roles
        }), 200
    

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500
def ForgotPassword():
    print("Processing forgot password")
    try:
        db = SessionLocal()
        data = request.get_json()

        user = db.query(Members).filter(Members.email == data['email']).first()
        if not user:
            return jsonify({"error": "No member with that email"}), 404

        # generate reset token using email + secret
        reset_token = hashlib.sha256(f"{user.email}premier_chama_reset".encode()).hexdigest()

        db.close()

        # in production you would email this token
        # for now return it directly for testing
        return jsonify({
            "message": "Reset token generated",
            "reset_token": reset_token,
            "memberId": user.memberId
        }), 200

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500


def SetPassword():
    print("Setting new password")
    try:
        db = SessionLocal()
        data = request.get_json()

        # verify token matches
        expected_token = hashlib.sha256(f"{data['email']}premier_chama_reset".encode()).hexdigest()

        if data['reset_token'] != expected_token:
            return jsonify({"error": "Invalid or expired reset token"}), 401

        user = db.query(Members).filter(Members.email == data['email']).first()
        if not user:
            return jsonify({"error": "Member not found"}), 404

        user.password = hash_password(data['new_password'])
        db.commit()
        db.close()

        return jsonify({"message": "Password updated successfully"}), 200

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500
