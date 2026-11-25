"""Translate stored role names to the application's authorization vocabulary."""
ROLE_ALIASES = {
    "usuario": "diner", "user": "diner",
    "empresario": "business_owner", "owner": "business_owner",
}

def canonical_role(role):
    name = str(role or "guest").strip().lower()
    return ROLE_ALIASES.get(name, name)
