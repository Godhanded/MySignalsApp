from user.models import User
from flask import jsonify, request, Blueprint, session
from Sig.utils import query_one_filtered, get_reset_token, verify_reset_token
from sig import bcrypt


user = Blueprint("user", url_prefix="/users")


@user.route("/register", methods=["POST"])
def register_user():
    data = request.get_json()
    user_name = data.get("user_name")
    email = data.get("email")
    password = data.get("password")
    confirm_password = data.get("confirm_password")

    if not (data and user_name and email and password and confirm_password):
        return (
            jsonify({"error": "Bad Request", "message": "Did you provide all fields?"}),
            304,
        )

    if password != confirm_password:
        return (
            jsonify({"error": "Bad Request", "message": "Passwords do not match"}),
            304,
        )

    if query_one_filtered(User, user_name=user_name) or query_one_filtered(
        User, email=email
    ):
        return (
            jsonify(
                {"error": "Conflict", "message": "User_name or email already exists"}
            ),
            304,
        )

    user = User(
        user_name=user_name,
        email=email,
        password=bcrypt.generate_password_hash(password),
    )
    user.insert()
    return jsonify(
        {"message": "Success", "user_name": user.user_name, "email": user.email}, 200
    )

@user.route("/activate/<string:token>")
def activate_user(token):
    user = verify_reset_token(User, token)
    if user:
        user.is_active = True
        user.update()
        return jsonify(
            {
                "message": "Success",
                "user_name": user.user_name,
                "is_active": user.is_active,
            },
            200,
        )
    return jsonify(
        {
            "error": "Unauthorized",
            "message": "Token is not valid or has already been used",
        },
        404,
    )


@user.route("/login", methods=["POST"])
def login_user():
    data = request.get_json()
    user_name_or_mail = data.get("user_name_or_mail")
    password = data.get("password")

    if not (data and user_name_or_mail and password):
        return jsonify(
            {"error": "Bad Request", "message": "Did you provide all fields?"}, 304
        )

    user = query_one_filtered(User, user_name=user_name_or_mail)
    if not user or not bcrypt.check_password_hash(user.password, password):
        user = query_one_filtered(User, email=user_name_or_mail)
        if not user or not bcrypt.check_password_hash(user.password, password):
            return jsonify(
                {"error": "Unauthorized", "message": "Incorrect username or password"},
                401,
            )

        session["user"] = user.id
        return jsonify(
            {
                "message": "Success",
                "user_name": user.user_name,
                "is_active": user.is_active,
            },
            200,
        )
    session["user"] = user.id
    return jsonify(
        {
            "message": "Success",
            "user_name": user.user_name,
            "is_active": user.is_active,
        },
        200,
    )


@user.route("/reset_password",methods=["POST"])
def reset_request():
    data=request.get_json()
    email = data.get("email")
    user= query_one_filtered(User,email)
    if user:
        token=get_reset_token(user)
        # send_reset_password_email(user,token)
        return jsonify({
            "message": f"Reset password token sent to {email}"
        },200)


@user.route("/reset_password/<string:token>", methods=["POST"])
def reset_token(token):
    data=request.get_json()
    password=data.get("password")
    password_confirm=data.get("password_confirm")
    if not password or not password_confirm:
        return (
            jsonify({"error": "Bad Request", "message": "Did you provide all fields?"}),
            304,
        )

    if password != confirm_password:
        return (
            jsonify({"error": "Bad Request", "message": "Passwords do not match"}),
            304,
        )
    user = verify_reset_token(User, token)
    if user:
        user.password=bcrypt.generate_password_hash(password)
        user.update()
        session.pop("user", None)
        return jsonify({"message": "Password changed"},200)
    return jsonify({"error": "Invalid token"},400)
    



@user.route("/logout", methods=["GET"])
def logout_user():
    session.pop("user", None)
    return jsonify(
        {
            "message": "Success",
        },
        200,
    )
