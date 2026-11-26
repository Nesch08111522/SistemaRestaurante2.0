import os

import pytest

from app.services import traceability


class Store:
    def __init__(self):
        self.rows = []
        self.marked = []

    def latest(self, **_kwargs):
        return self.rows[-1] if self.rows else None

    def enqueue(self, **kwargs):
        row = {"id_ancla": len(self.rows) + 1, **kwargs}
        self.rows.append(row)
        return row

    def pending(self, *, limit):
        return self.rows[:limit]

    def mark(self, id_ancla, **kwargs):
        self.marked.append((id_ancla, kwargs))


@pytest.fixture(autouse=True)
def trace_secret(monkeypatch):
    monkeypatch.setenv("TRACEABILITY_PSEUDONYM_SECRET", "x" * 32)


def review(**changes):
    item = {"id_resena": 3, "id_restaurante": 9, "id_usuario": 21,
            "calificacion": 5, "comentario": " Excelente  café ", "creado_en": "2026-01-01T00:00:00Z"}
    item.update(changes)
    return item


def test_review_hash_is_stable_without_raw_comment_or_user():
    assert traceability.review_hash(review()) == traceability.review_hash(review(comentario="excelente café"))
    assert len(traceability.review_hash(review())) == 64
    assert traceability.pseudonymize(21) != "21"


def test_enqueue_chains_an_amended_review():
    store = Store()
    first = traceability.enqueue_review(review(), store)
    second = traceability.enqueue_review(review(actualizado_en="2026-01-02T00:00:00Z"), store)
    assert first["hash_previo"] is None
    assert second["hash_previo"] == first["hash_canonico"]


def test_dry_run_never_submits_onchain():
    store = Store()
    traceability.enqueue_ai_decision({"id_decision": 8, "tipo": "recommend", "entidad": "menu",
                                      "id_usuario_actor": 21, "hash_entrada": "a" * 64,
                                      "estado": "ok", "creado_en": "2026-01-01"}, store)
    assert traceability.process_pending(store, mode="dry-run") == {"mode": "dry_run", "processed": 1}
    assert store.marked == [(1, {"estado": "simulado"})]
    with pytest.raises(ValueError, match="on-chain"):
        traceability.process_pending(store, mode="onchain")
