"""API-response parsing, including the markdown-fenced case. No network calls."""

from jobtailor.models import Contact, JobPosting, Profile, TailoredResume
from jobtailor.tailor import client as tailor_client


def test_strip_plain_json():
    raw = '{"summary": "s", "bullets": []}'
    data = tailor_client._strip_code_fences(raw)
    result = TailoredResume.model_validate_json(data)
    assert result.summary == "s"


def test_strip_fenced_json():
    # The model sometimes wraps JSON in a ```json ... ``` fence; strip it.
    raw = '```json\n{"summary": "hi", "bullets": []}\n```'
    data = tailor_client._strip_code_fences(raw)
    result = TailoredResume.model_validate_json(data)
    assert result.summary == "hi"


def test_tailor_parses_mocked_api(monkeypatch):
    """`client.tailor` parses a mocked API response without touching the network."""
    fake_json = (
        '{"summary": "Tailored.", '
        '"bullets": [{"accomplishment_id": "a1", "text": "Did a thing."}]}'
    )

    # Minimal fakes that mimic the shapes client.tailor reaches into.
    class _Block:
        type = "text"
        text = fake_json

    class _Response:
        content = [_Block()]

    class _Messages:
        def create(self, **kwargs):
            return _Response()

    class _FakeClient:
        messages = _Messages()

    # Patch the Anthropic constructor so no real client (and no network) is made,
    # and stub the API-key check so the test needs no real key.
    monkeypatch.setattr(tailor_client.anthropic, "Anthropic", lambda **kw: _FakeClient())
    monkeypatch.setattr(tailor_client.config, "anthropic_api_key", lambda: "test-key")

    profile = Profile(contact=Contact(name="Ada", email="ada@example.com"))
    job = JobPosting(source="inline", description="Backend role")

    result, prompt, _raw = tailor_client.tailor(profile, job)

    assert isinstance(result, TailoredResume)
    assert result.bullets[0].accomplishment_id == "a1"
    assert "Backend role" in prompt  # the job description made it into the prompt
