# app/blueprints/auth/__init__.py
"""Blueprint de autenticación."""
from __future__ import annotations

from flask import (
    Blueprint, flash, jsonify, redirect, render_template, request, session, url_for,
)

from app.core.security import (
    is_safe_redirect_url, normalize_text, session_identity,
)
from app.models.user import UserModel

bp = Blueprint("auth", __name__)


@bp.get("/login")
def login_form():
    if session.get("user_id"):
        return redirect(url_for("public.home"))
    return render_template(
        "auth/login.html",
        next=request.args.get("next", ""),
    )


@bp.post("/login")
def login_submit():
    username = (request.form.get("username") or "").strip()
    password = request.form.get("password") or ""
    next_url = request.form.get("next") or ""

    if not username or len(username) > 254 or not password:
        flash("Usuario y contraseña son obligatorios.", "error")
        return render_template(
            "auth/login.html", next=next_url, username=username
        ), 400

    user = UserModel.authenticate(username, password)
    if not user:
        flash("Usuario o contraseña incorrectos.", "error")
        return render_template(
            "auth/login.html", next=next_url, username=username
        ), 401

    session.clear()
    session["user_id"] = user["id"]
    session["user"] = session_identity(user)
    session["role"] = user["role"]
    session["username"] = user["username"]
    session.permanent = True
    nombre = (user.get("profile") or {}).get("name") or user["username"]
    flash(f"¡Bienvenido, {nombre}!", "success")

    destino = next_url if is_safe_redirect_url(next_url) else url_for("auth.workspace_home")
    return redirect(destino)


@bp.get("/register")
def register_form():
    if session.get("user_id"):
        return redirect(url_for("public.home"))
    return render_template("auth/register.html")


@bp.post("/register")
def register_submit():
    username = normalize_text(request.form.get("username"), max_length=120)
    password = request.form.get("password") or ""
    confirm = request.form.get("confirm") or ""
    email = normalize_text(request.form.get("email"), max_length=254)
    name = normalize_text(request.form.get("name"), max_length=180)

    if not username or not password or not email:
        flash("Usuario, contraseña y correo son obligatorios.", "error")
        return render_template(
            "auth/register.html", username=username, email=email, name=name
        ), 400
    if len(password) < 8:
        flash("La contraseña debe tener al menos 8 caracteres.", "error")
        return render_template(
            "auth/register.html", username=username, email=email, name=name
        ), 400
    if confirm and confirm != password:
        flash("Las contraseñas no coinciden.", "error")
        return render_template(
            "auth/register.html", username=username, email=email, name=name
        ), 400

    user = UserModel.register(
        username=username, password=password, email=email, name=name, role="user"
    )
    if not user:
        flash("El nombre de usuario ya existe.", "error")
        return render_template(
            "auth/register.html", username=username, email=email, name=name
        ), 409

    session.clear()
    session["user_id"] = user["id"]
    session["user"] = session_identity(user)
    session["role"] = user["role"]
    session["username"] = user["username"]
    session.permanent = True
    flash("¡Cuenta creada! Bienvenido a SmartResto.", "success")
    return redirect(url_for("public.home"))


# GET requests show a confirmation; only POST changes session state.
@bp.route("/logout", methods=["GET", "POST"])
def logout():
    if request.method == "GET":
        return render_template("workspace/logout.html")
    session.clear()
    flash("Sesión cerrada.", "info")
    return redirect(url_for("public.home"))


@bp.get("/recover")
def recover_form():
    return render_template("auth/login.html", recover=True, next="")


@bp.post("/recover")
def recover_submit():
    """Request a password-reset code without disclosing account existence."""
    from app.services.account_recovery import issue
    username = normalize_text(request.form.get("username"), max_length=254)
    channel = normalize_text(request.form.get("channel") or "email", max_length=10).lower()
    try:
        if username:
            issue(username, channel)
    except DomainError as exc:
        flash(exc.message, "error")
        return render_template("auth/login.html", recover=True, next=""), exc.status
    flash("Si la cuenta existe y tiene un correo válido, recibirás un código.", "info")
    return render_template("auth/login.html", recover=True, next=""), 200


@bp.post("/recover/complete")
def recover_complete():
    """Consume the code sent by ``recover_submit`` and rotate the password."""
    from app.services.account_recovery import complete
    from app.services.errors import DomainError

    username = normalize_text(request.form.get("username"), max_length=254)
    challenge = request.form.get("challenge") or ""
    code = request.form.get("code") or ""
    password = request.form.get("password") or ""
    confirmation = request.form.get("confirm") or ""
    if password != confirmation:
        flash("Las contraseñas no coinciden.", "error")
        return render_template("auth/login.html", recover=True, next=""), 400
    try:
        changed = complete(username, challenge, code, password)
    except DomainError as exc:
        flash(exc.message, "error")
        return render_template("auth/login.html", recover=True, next=""), exc.status
    if not changed:
        flash("El código no es válido, expiró o ya fue usado.", "error")
        return render_template("auth/login.html", recover=True, next=""), 400
    flash("Contraseña actualizada. Ya puedes iniciar sesión.", "success")
    return redirect(url_for("auth.login_form"))


@bp.get("/api/whoami")
def api_whoami():
    from app.core.security import fresh_session_user
    user = fresh_session_user()
    if not user:
        return jsonify({"authenticated": False}), 200
    profile = user.get("profile") or {}
    return jsonify({
        "authenticated": True,
        "user": {
            "id": user["id"],
            "username": user["username"],
            "role": user["role"],
            "name": profile.get("name"),
            "email": profile.get("email"),
        },
    }), 200

from . import workspace_routes  # noqa: E402,F401

from . import profile_routes  # noqa: E402,F401

from . import favorite_routes  # noqa: E402,F401

from . import notification_routes  # noqa: E402,F401

from . import personal_routes  # noqa: E402,F401
