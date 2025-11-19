from wikibee.formatting import convert_wikitext_headers, split_wikitext_sections


def test_split_wikitext_sections_basic():
    text = """Introduction text.
== Section 1 ==
Content 1.
== Section 2 ==
Content 2.
"""
    sections = split_wikitext_sections(text)
    assert len(sections) == 3
    assert sections[0] == ("Introduction", "Introduction text.")
    assert sections[1] == ("Section 1", "Content 1.")
    assert sections[2] == ("Section 2", "Content 2.")


def test_split_wikitext_sections_no_intro():
    text = """== Section 1 ==
Content 1.
"""
    sections = split_wikitext_sections(text)
    assert len(sections) == 1
    assert sections[0] == ("Section 1", "Content 1.")


def test_convert_wikitext_headers():
    text = """Intro.
== Section 1 ==
Text.
=== Subsection ===
More text.
== Section 2 ==
End.
"""
    converted = convert_wikitext_headers(text)
    expected = """Intro.
## Section 1
Text.
### Subsection
More text.
## Section 2
End.
"""
    assert converted == expected
