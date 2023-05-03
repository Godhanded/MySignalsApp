from flask import Blueprint, request, jsonify, session
from MySignalsApp.utils import (
    query_one_filtered,
    query_all_filtered,
    query_all,
    has_permission,
    is_active,
)
from MySignalsApp.models import User, Roles


registrar = Blueprint("registrar", __name__, url_prefix="/registrar")


@registrar.route("/provider/new", methods=["POST"])
def add_provider():
    registrar_id = has_permission(session, "Registrar")
    is_active(User, registrar_id)

    data = request.get_json()
    provider_email = data.get("provider_email")

    if not provider_email:
        return (
            jsonify(
                {"error": "Bad Request", "message": "Did you fill all fields properly?"}
            ),
            400,
        )

    try:
        user = query_one_filtered(User, email=provider_email)
        if not user:
            return (
                jsonify(
                    {
                        "error": "Resource not found",
                        "message": f"User with mail {provider_email} does not exist",
                    }
                ),
                404,
            )

        if user.id == registrar_id:
            return (
                jsonify(
                    {"error": "Forbidden", "message": "You can't change role of self"}
                ),
                403,
            )
        if Roles.PROVIDER == user.roles:
            return (
                jsonify(
                    {
                        "error": "Forbidden",
                        "message": f"The user with mail {provider_email} is already a provider",
                    }
                ),
                403,
            )

        user.roles = Roles.PROVIDER
        user.insert()
        return jsonify({"message": "success", "provider": provider_email})
    except Exception as e:
        return (
            jsonify(
                {
                    "error": "Internal server error",
                    "message": "It's not you it's us",
                }
            ),
            500,
        )


@registrar.route("/registrar/new", methods=["POST"])
def add_registrar():
    registrar_id = has_permission(session, "Registrar")
    is_active(User, registrar_id)

    data = request.get_json()
    registrar_email = data.get("registrar_email")

    if not registrar_email:
        return (
            jsonify(
                {"error": "Bad Request", "message": "Did you fill all fields properly?"}
            ),
            400,
        )

    try:
        user = query_one_filtered(User, email=registrar_email)
        if not user:
            return (
                jsonify(
                    {
                        "error": "Resource not found",
                        "message": f"User with mail {registrar_email} does not exist",
                    }
                ),
                404,
            )

        if user.id == registrar_id:
            return (
                jsonify(
                    {"error": "Forbidden", "message": "You can't change role of self"}
                ),
                403,
            )
        if Roles.REGISTRAR == user.roles:
            return (
                jsonify(
                    {
                        "error": "Forbidden",
                        "message": f"The user with mail {registrar_email} is already a registrar",
                    }
                ),
                403,
            )

        user.roles = Roles.REGISTRAR
        user.insert()
        return jsonify({"message": "success", "registrar": registrar_email})
    except Exception as e:
        return (
            jsonify(
                {
                    "error": "Internal server error",
                    "message": "It's not you it's us",
                }
            ),
            500,
        )


@registrar.route("/drop_role", methods=["POST"])
def drop_role():
    registrar_id = has_permission(session, "Registrar")
    is_active(User, registrar_id)

    data = request.get_json()
    user_email = data.get("user_email")

    if not user_email:
        return (
            jsonify(
                {"error": "Bad Request", "message": "Did you fill all fields properly?"}
            ),
            400,
        )

    try:
        user = query_one_filtered(User, email=user_email)
        if not user:
            return (
                jsonify(
                    {
                        "error": "Resource not found",
                        "message": f"User with mail {user_email} does not exist",
                    }
                ),
                404,
            )

        if user.id == registrar_id:
            return (
                jsonify(
                    {"error": "Forbidden", "message": "You can't change role of self"}
                ),
                403,
            )
        if Roles.USER == user.roles:
            return (
                jsonify(
                    {
                        "error": "Forbidden",
                        "message": f"The user with mail {user_email} is already a regular user",
                    }
                ),
                403,
            )

        user.roles = Roles.USER
        user.insert()
        return jsonify({"message": "success", "registrar": user_email})
    except Exception as e:
        return (
            jsonify(
                {
                    "error": "Internal server error",
                    "message": "It's not you it's us",
                }
            ),
            500,
        )


@registrar.route("/role/providers")
def get_providers():
    registrar_id = has_permission(session, "Registrar")
    is_active(User, registrar_id)

    try:
        providers = query_all_filtered(User, roles=Roles.PROVIDER)
        if not providers:
            return jsonify({"message": "success", "providers": [], "total": 0})

        provider_list = [provider.format() for provider in providers]
        return jsonify(
            {
                "message": "success",
                "providers": provider_list,
                "total": len(provider_list),
            }
        )

    except Exception as e:
        return (
            jsonify(
                {
                    "error": "Internal server error",
                    "message": "It's not you it's us",
                }
            ),
            500,
        )


@registrar.route("/role/registrars")
def get_registrars():
    registrar_id = has_permission(session, "Registrar")
    is_active(User, registrar_id)

    try:
        registrars = query_all_filtered(User, roles=Roles.REGISTRAR)
        if not registrars:
            return jsonify({"message": "success", "providers": [], "total": 0})

        registrar_list = [registrar.format() for registrar in registrars]
        return jsonify(
            {
                "message": "success",
                "providers": registrar_list,
                "total": len(registrar_list),
            }
        )

    except Exception as e:
        return (
            jsonify(
                {
                    "error": "Internal server error",
                    "message": "It's not you it's us",
                }
            ),
            500,
        )


@registrar.route("/role/users")
def get_users():
    registrar_id = has_permission(session, "Registrar")
    is_active(User, registrar_id)

    try:
        users = query_all_filtered(User, roles=Roles.USER)
        if not users:
            return jsonify({"message": "success", "providers": [], "total": 0})

        user_list = [user.format() for user in users]
        return jsonify(
            {
                "message": "success",
                "providers": user_list,
                "total": len(user_list),
            }
        )

    except Exception as e:
        return (
            jsonify(
                {
                    "error": "Internal server error",
                    "message": "It's not you it's us",
                }
            ),
            500,
        )


@registrar.route("/get/users")
def get_all_users():
    registrar_id = has_permission(session, "Registrar")
    is_active(User, registrar_id)

    try:
        users = query_all(User)
        if not users:
            return jsonify({"message": "success", "providers": [], "total": 0})

        user_list = [user.format() for user in users]
        return jsonify(
            {
                "message": "success",
                "providers": user_list,
                "total": len(user_list),
            }
        )

    except Exception as e:
        return (
            jsonify(
                {
                    "error": "Internal server error",
                    "message": "It's not you it's us",
                }
            ),
            500,
        )
