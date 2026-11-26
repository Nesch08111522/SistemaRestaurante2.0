from types import SimpleNamespace

from app.services import traceability_scheduler as scheduler


def test_worker_starts_only_once_for_each_process(monkeypatch):
    monkeypatch.setenv('ANCHOR_MODE', 'onchain')
    monkeypatch.delenv('ANCHOR_AUTO_ENABLED', raising=False)
    monkeypatch.setattr(scheduler, '_threads', {})
    started = []
    class Thread:
        def __init__(self, **kwargs): self.kwargs = kwargs
        def start(self): started.append(self)
        def is_alive(self): return True
    monkeypatch.setattr(scheduler.threading, 'Thread', Thread)
    app = SimpleNamespace(testing=False)
    assert scheduler.ensure_started(app) is True
    assert scheduler.ensure_started(app) is False
    assert len(started) == 1


def test_worker_disabled_during_tests_or_without_onchain(monkeypatch):
    monkeypatch.setenv('ANCHOR_MODE', 'onchain')
    assert scheduler.ensure_started(SimpleNamespace(testing=True)) is False
    monkeypatch.setenv('ANCHOR_MODE', 'off')
    assert scheduler.ensure_started(SimpleNamespace(testing=False)) is False
