from flask import Blueprint, request, jsonify, session
from MySignalsApp.schemas import ValidEmailSchema, PageQuerySchema
from MySignalsApp.models import User, Roles
from pydantic import ValidationError
from MySignalsApp.utils import (
    query_one_filtered,
    query_paginate_filtered,
    query_paginated,
    has_permission,
    is_active,
)
from MySignalsApp import db

registrar = Blueprint("registrar", __name__, url_prefix="/registrar")


@registrar.route("/provider/new", methods=["POST"])
def add_provider():
    registrar_id = has_permission(session, "Registrar")
    is_active(User, registrar_id)

    data = request.get_json()

    try:
        provider_email = ValidEmailSchema(**data)
        user = query_one_filtered(User, email=provider_email.email)
        if not user:
            return (
                jsonify(
                    {
                        "error": "Resource not found",
                        "message": f"User with mail {provider_email.email} does not exist",
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
                        "message": f"The user with mail {provider_email.email} is already a provider",
                    }
                ),
                403,
            )

        user.roles = Roles.PROVIDER
        user.insert()
        return jsonify({"message": "success", "provider": provider_email.email})
    except ValidationError as e:
        msg = ""
        for err in e.errors():
            msg += f"{str(err.get('loc')).strip('(),')}:{err.get('msg')}, "
        return (
            jsonify({"error": "Bad Request", "message": msg}),
            400,
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


@registrar.route("/registrar/new", methods=["POST"])
def add_registrar():
    registrar_id = has_permission(session, "Registrar")
    is_active(User, registrar_id)

    data = request.get_json()

    try:
        registrar_email = ValidEmailSchema(**data)
        user = query_one_filtered(User, email=registrar_email.email)
        if not user:
            return (
                jsonify(
                    {
                        "error": "Resource not found",
                        "message": f"User with mail {registrar_email.email} does not exist",
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
                        "message": f"The user with mail {registrar_email.email} is already a registrar",
                    }
                ),
                403,
            )

        user.roles = Roles.REGISTRAR
        user.insert()
        return jsonify({"message": "success", "registrar": registrar_email.email})
    except ValidationError as e:
        msg = ""
        for err in e.errors():
            msg += f"{str(err.get('loc')).strip('(),')}:{err.get('msg')}, "
        return (
            jsonify({"error": "Bad Request", "message": msg}),
            400,
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


@registrar.route("/drop_role", methods=["POST"])
def drop_role():
    registrar_id = has_permission(session, "Registrar")
    is_active(User, registrar_id)

    data = request.get_json()

    try:
        user_email = ValidEmailSchema(**data)
        user = query_one_filtered(User, email=user_email.email)
        if not user:
            return (
                jsonify(
                    {
                        "error": "Resource not found",
                        "message": f"User with mail {user_email.email} does not exist",
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
                        "message": f"The user with mail {user_email.email} is already a regular user",
                    }
                ),
                403,
            )

        user.roles = Roles.USER
        user.insert()
        return jsonify({"message": "success", "registrar": user_email.email})
    except ValidationError as e:
        msg = ""
        for err in e.errors():
            msg += f"{str(err.get('loc')).strip('(),')}:{err.get('msg')}, "
        return (
            jsonify({"error": "Bad Request", "message": msg}),
            400,
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


@registrar.route("/role/providers")
def get_providers():
    registrar_id = has_permission(session, "Registrar")
    is_active(User, registrar_id)
    try:
        page = PageQuerySchema(request.args.get("page", 1))
        providers = query_paginate_filtered(User, page.page, roles=Roles.PROVIDER)
        if not providers.items:
            return jsonify(
                {
                    "message": "success",
                    "providers": [],
                    "pages": providers.pages,
                    "total": providers.total if providers.total else 0,
                }
            )

        provider_list = [provider.format() for provider in providers]
        return jsonify(
            {
                "message": "success",
                "providers": provider_list,
                "pages": providers.pages,
                "total": providers.total if providers.total else 0,
            }
        )
    except ValidationError as e:
        msg = ""
        for err in e.errors():
            msg += f"{str(err.get('loc')).strip('(),')}:{err.get('msg')}, "
        return (
            jsonify({"error": "Bad Request", "message": msg}),
            400,
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
        page = PageQuerySchema(request.args.get("page", 1))
        registrars = query_paginate_filtered(User, page.page, roles=Roles.REGISTRAR)
        if not registrars.items:
            return jsonify(
                {
                    "message": "success",
                    "registrars": [],
                    "pages": registrars.pages,
                    "total": registrars.total if registrars.total else 0,
                }
            )

        registrar_list = [registrar.format() for registrar in registrars]
        return jsonify(
            {
                "message": "success",
                "registrars": registrar_list,
                "pages": registrars.pages,
                "total": registrars.total if registrars.total else 0,
            }
        )
    except ValidationError as e:
        msg = ""
        for err in e.errors():
            msg += f"{str(err.get('loc')).strip('(),')}:{err.get('msg')}, "
        return (
            jsonify({"error": "Bad Request", "message": msg}),
            400,
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
        page = PageQuerySchema(request.args.get("page", 1))
        users = query_paginate_filtered(User, page.page, roles=Roles.USER)
        if not users.items:
            return jsonify(
                {
                    "message": "success",
                    "users": [],
                    "pages": users.pages,
                    "total": users.total if users.total else 0,
                }
            )

        user_list = [user.format() for user in users]
        return jsonify(
            {
                "message": "success",
                "users": user_list,
                "pages": users.pages,
                "total": users.total if users.total else 0,
            }
        )
    except ValidationError as e:
        msg = ""
        for err in e.errors():
            msg += f"{str(err.get('loc')).strip('(),')}:{err.get('msg')}, "
        return (
            jsonify({"error": "Bad Request", "message": msg}),
            400,
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
        page = PageQuerySchema(request.args.get("page", 1))
        users = query_paginated(User, page.page)
        if not users.items:
            return jsonify(
                {
                    "message": "success",
                    "users": [],
                    "pages": users.pages,
                    "total": users.total if users.total else 0,
                }
            )

        user_list = [user.format() for user in users]
        return jsonify(
            {
                "message": "success",
                "users": user_list,
                "pages": users.pages,
                "total": users.total if users.total else 0,
            }
        )
    except ValidationError as e:
        msg = ""
        for err in e.errors():
            msg += f"{str(err.get('loc')).strip('(),')}:{err.get('msg')}, "
        return (
            jsonify({"error": "Bad Request", "message": msg}),
            400,
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
