from types import SimpleNamespace

from llm.utils import translation


def test_detect_language_spanish():
    result = translation.detect_language(
        "Hola, ¿cómo estás?",
        allow=translation.SUPPORTED_LANGUAGES.keys(),
    )
    assert result == "es"


def test_detect_language_fallback_on_empty():
    assert translation.detect_language("", allow=translation.SUPPORTED_LANGUAGES.keys()) == "en"


def test_translate_text_returns_original_when_languages_match(monkeypatch):
    call_flag = {"called": False}

    def fail_if_called():
        call_flag["called"] = True
        raise AssertionError("OpenAI should not be invoked when no translation is needed.")

    monkeypatch.setattr(translation, "get_openai_client", fail_if_called)
    assert translation.translate_text("Hello", "en", source_language="en") == "Hello"
    assert call_flag["called"] is False


def test_translate_text_uses_openai_client(monkeypatch):
    captured = {}

    def fake_create(**kwargs):
        captured.update(kwargs)
        return SimpleNamespace(
            choices=[
                SimpleNamespace(
                    message=SimpleNamespace(content="Hola"),
                )
            ]
        )

    fake_client = SimpleNamespace(
        settings=SimpleNamespace(openai_model="gpt-test"),
        client=SimpleNamespace(
            chat=SimpleNamespace(
                completions=SimpleNamespace(create=fake_create)
            )
        ),
    )

    monkeypatch.setattr(translation, "get_openai_client", lambda: fake_client)
    result = translation.translate_text("Hello", "es", source_language="en")

    assert result == "Hola"
    assert captured["messages"][0]["content"].startswith("You are a translation engine")
    assert captured["messages"][1]["content"].startswith("Source language: English")
