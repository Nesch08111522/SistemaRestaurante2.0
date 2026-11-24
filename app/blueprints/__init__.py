# app/blueprints/__init__.py
"""Registro centralizado de todos los blueprints."""


def register_blueprints(app):
    from app.blueprints.public import bp as public_bp
    app.register_blueprint(public_bp)

    from app.blueprints.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix="/auth")

    from app.blueprints.discovery import bp as discovery_bp
    app.register_blueprint(discovery_bp, url_prefix="/descubrir")

    from app.blueprints.business import bp as business_bp
    app.register_blueprint(business_bp, url_prefix="/negocio")

    from app.blueprints.owner import bp as owner_bp
    app.register_blueprint(owner_bp, url_prefix="/owner")

    from app.blueprints.admin import bp as admin_bp
    app.register_blueprint(admin_bp, url_prefix="/admin")

    from app.blueprints.salon import bp as salon_bp
    app.register_blueprint(salon_bp, url_prefix="/salon")

    from app.blueprints.kitchen import bp as kitchen_bp
    app.register_blueprint(kitchen_bp, url_prefix="/kitchen")

    from app.blueprints.market import bp as market_bp
    app.register_blueprint(market_bp, url_prefix="/mercado")

    from app.blueprints.loyalty import bp as loyalty_bp
    app.register_blueprint(loyalty_bp, url_prefix="/recompensas")

    from app.blueprints.pantry import bp as pantry_bp
    app.register_blueprint(pantry_bp, url_prefix="/mi-cocina")

    from app.blueprints.ar import bp as ar_bp
    app.register_blueprint(ar_bp, url_prefix="/ar")