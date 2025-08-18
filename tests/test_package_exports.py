from wiki_extractor import (
    sanitize_filename,
    make_tts_friendly,
    extract_wikipedia_text,
    normalize_for_tts,
    INFLECT_AVAILABLE,
    NetworkError,
    APIError,
    NotFoundError,
    DisambiguationError,
    write_text_file,
)


def test_package_exports_present():
    # Sanity check: ensure the public API names are importable from package root
    assert callable(sanitize_filename)
    assert callable(make_tts_friendly)
    assert callable(extract_wikipedia_text)
    assert callable(normalize_for_tts)
    assert isinstance(INFLECT_AVAILABLE, bool)
    # Exception types should be classes
    assert isinstance(NetworkError, type)
    assert isinstance(APIError, type)
    assert isinstance(NotFoundError, type)
    assert isinstance(DisambiguationError, type)
    assert callable(write_text_file)
