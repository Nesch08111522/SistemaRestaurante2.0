"""Authenticated entry point; keep public login/register templates untouched."""
from flask import render_template
from app.core.auth_guard import login_required
from app.blueprints.workspace import navigation, workspace_errors
from . import bp


@bp.app_context_processor
def workspace_context():
    return {"workspace_navigation": navigation}


@bp.get('/inicio')
@workspace_errors
@login_required
def workspace_home():
    return render_template('workspace/home.html')
