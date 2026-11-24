def main():
    """Prueba rápida del módulo IA en modo mock."""
    from app import create_app
    app = create_app()
    
    with app.app_context():
        from app.ai.client import is_mock, is_configured
        print("Mock mode:", is_mock(), "| API configurada:", is_configured())
    
        # Recomendación
        from app.ai.recommender import recommend
        r = recommend(
            id_usuario_actor=1,
            restricciones=["sin gluten"],
            preferencias=["mariscos"],
            catalogo=[{"id": 1, "tipo": "plato", "nombre": "Ceviche", "restaurante": "Big Ben", "precio": 35.0}],
            contexto="algo fresco",
        )
        print("Recomendación:", r)
    
        # Auditoría
        from app.ai.copilot import audit_menu
        a = audit_menu(
            id_usuario_actor=1,
            platos=[{"nombre": "Lomo saltado", "precio": 35, "descripcion": "Rico"}],
        )
        print("Auditoría:", a)


if __name__ == "__main__":
    main()
