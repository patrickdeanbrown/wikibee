"""Tests for TTS text normalization functionality."""

import pytest
from wiki_extractor.tts_normalizer import TTSNormalizer, normalize_for_tts


class TestRomanNumeralsInNames:
    """Test normalization of Roman numerals in royal/historical names."""

    def test_royal_names(self):
        """Test royal names with Roman numerals."""
        normalizer = TTSNormalizer()

        test_cases = [
            ("Richard III was king", "Richard the third was king"),
            ("Louis XVI ruled France", "Louis the sixteenth ruled France"),
            (
                "Napoleon III established the empire",
                "Napoleon the third established the empire"
            ),
            ("Edward IV was a Yorkist king", "Edward the fourth was a Yorkist king"),
            (
                "Constantine I legalized Christianity",
                "Constantine the first legalized Christianity"
            ),
        ]

        for input_text, expected in test_cases:
            result = normalizer._normalize_royal_names(input_text)
            assert result == expected, (
                f"Input: {input_text}, Expected: {expected}, Got: {result}"
            )

    def test_war_names_unchanged(self):
        """Test that war names are not affected by royal name patterns."""
        normalizer = TTSNormalizer()

        # These should NOT be changed by royal name normalization
        test_cases = [
            "World War II was devastating",
            "Section III discusses methods",
            "Chapter V explains concepts",
        ]

        for text in test_cases:
            result = normalizer._normalize_royal_names(text)
            assert result == text, f"Text should be unchanged: {text}"

    def test_invalid_roman_numerals(self):
        """Test handling of invalid Roman numeral patterns."""
        normalizer = TTSNormalizer()

        # These should remain unchanged
        test_cases = [
            "Richard XIIII was not a real king",  # Invalid Roman numeral
            "Louis VVIII ruled",  # Invalid pattern
            "Napoleon IIII established",  # Invalid pattern
        ]

        for text in test_cases:
            result = normalizer._normalize_royal_names(text)
            assert result == text, f"Invalid Roman numerals should be unchanged: {text}"


class TestCenturyOrdinals:
    """Test normalization of ordinal numbers (19th, 3rd, etc.)."""

    def test_century_ordinals(self):
        """Test conversion of ordinal numbers to words."""
        normalizer = TTSNormalizer()

        test_cases = [
            ("19th century", "nineteenth century"),
            ("3rd Battalion", "third Battalion"),
            ("2nd World War", "second World War"),
            ("21st century technology", "twenty-first century technology"),
            ("1st place winner", "first place winner"),
            ("42nd parallel", "forty-second parallel"),
        ]

        for input_text, expected in test_cases:
            result = normalizer._normalize_century_ordinals(input_text)
            assert result == expected, (
                f"Input: {input_text}, Expected: {expected}, Got: {result}"
            )

    def test_mixed_ordinals(self):
        """Test text with multiple ordinal numbers."""
        normalizer = TTSNormalizer()

        input_text = (
            "The 19th century saw the 2nd Industrial Revolution in the 1st half"
        )
        expected = (
            "The nineteenth century saw the second Industrial Revolution "
            "in the first half"
        )
        result = normalizer._normalize_century_ordinals(input_text)
        assert result == expected

    def test_ordinals_in_context(self):
        """Test ordinals that should remain unchanged in certain contexts."""
        normalizer = TTSNormalizer()

        # These are edge cases - they should still be converted
        # Note: num2words uses "and" in some numbers
        test_cases = [
            ("Route 101st Street", "Route one hundred and first Street"),
            ("The 5th of November", "The fifth of November"),
        ]

        for input_text, expected in test_cases:
            result = normalizer._normalize_century_ordinals(input_text)
            assert result == expected


class TestLatinAbbreviations:
    """Test normalization of Latin abbreviations."""

    def test_common_abbreviations(self):
        """Test common Latin abbreviations."""
        normalizer = TTSNormalizer()

        test_cases = [
            (
                "This includes, e.g., algorithms",
                "This includes, for example algorithms"
            ),
            (
                "Machine learning, i.e., automated pattern recognition",
                "Machine learning, that is automated pattern recognition"
            ),
            (
                "Various methods: classification, regression, etc.",
                "Various methods: classification, regression, et cetera",
            ),
            (
                "The algorithm was developed c. 1943 by Turing",
                "The algorithm was developed circa 1943 by Turing",
            ),
        ]

        for input_text, expected in test_cases:
            result = normalizer._normalize_latin_abbreviations(input_text)
            assert result == expected, (
                f"Input: {input_text}, Expected: {expected}, Got: {result}"
            )

    def test_case_insensitive_abbreviations(self):
        """Test that abbreviations work regardless of case."""
        normalizer = TTSNormalizer()

        test_cases = [
            ("This includes E.G. algorithms", "This includes for example algorithms"),
            (
                "Machine learning I.E. pattern recognition",
                "Machine learning that is pattern recognition",
            ),
            ("Various methods ETC.", "Various methods et cetera"),
        ]

        for input_text, expected in test_cases:
            result = normalizer._normalize_latin_abbreviations(input_text)
            assert result == expected

    def test_circa_dates(self):
        """Test circa date patterns specifically."""
        normalizer = TTSNormalizer()

        test_cases = [
            ("Written c. 1943", "Written circa 1943"),
            ("Built c. 1850", "Built circa 1850"),
            ("Developed c.1960", "Developed circa 1960"),  # No space
        ]

        for input_text, expected in test_cases:
            result = normalizer._normalize_latin_abbreviations(input_text)
            assert result == expected


class TestDecades:
    """Test normalization of decade references."""

    def test_decade_conversion(self):
        """Test conversion of decades to spoken form."""
        normalizer = TTSNormalizer()

        test_cases = [
            (
                "The 1980s were transformative",
                "The nineteen eighties were transformative",
            ),
            ("Music from the 1960s", "Music from the nineteen sixties"),
            ("The 1950s saw rapid growth", "The nineteen fifties saw rapid growth"),
            ("Technology in the 2020s", "Technology in the twenty twenties"),
            ("The roaring 1920s", "The roaring nineteen twenties"),
            ("During the 1830s", "During the eighteen thirties"),
        ]

        for input_text, expected in test_cases:
            result = normalizer._normalize_decades(input_text)
            assert result == expected, (
                f"Input: {input_text}, Expected: {expected}, Got: {result}"
            )

    def test_hundreds_decades(self):
        """Test decades ending in 00s."""
        normalizer = TTSNormalizer()

        test_cases = [
            ("The 1800s were difficult", "The eighteen hundreds were difficult"),
            ("During the 1900s", "During the nineteen hundreds"),
            ("The 2000s brought change", "The two thousands brought change"),
        ]

        for input_text, expected in test_cases:
            result = normalizer._normalize_decades(input_text)
            assert result == expected

    def test_non_decade_years_unchanged(self):
        """Test that non-decade year references are unchanged."""
        normalizer = TTSNormalizer()

        test_cases = [
            "In 1984, Orwell's vision",  # Specific year, not decade
            "The year 2001 was significant",  # Specific year
        ]

        for text in test_cases:
            result = normalizer._normalize_decades(text)
            assert result == text


class TestWarNumbering:
    """Test normalization of war numbering."""

    def test_world_wars(self):
        """Test World War numbering conversion."""
        normalizer = TTSNormalizer()

        test_cases = [
            ("World War II was devastating", "World War Two was devastating"),
            ("World War I changed everything", "World War One changed everything"),
            ("After WWII ended", "After World War Two ended"),
            ("During WWI", "During World War One"),
        ]

        for input_text, expected in test_cases:
            result = normalizer._normalize_war_numbering(input_text)
            assert result == expected, (
                f"Input: {input_text}, Expected: {expected}, Got: {result}"
            )

    def test_mixed_war_references(self):
        """Test text with multiple war references."""
        normalizer = TTSNormalizer()

        input_text = (
            "World War I preceded World War II, and WWII was larger than WWI"
        )
        expected = (
            "World War One preceded World War Two, and World War Two was "
            "larger than World War One"
        )
        result = normalizer._normalize_war_numbering(input_text)
        assert result == expected


class TestFullNormalization:
    """Test complete normalization with all patterns."""

    def test_comprehensive_normalization(self):
        """Test text with multiple pattern types."""
        normalizer = TTSNormalizer()

        input_text = (
            "In the 19th century, Napoleon III ruled during the 1850s, "
            "e.g., after World War I but before World War II."
        )
        expected = (
            "In the nineteenth century, Napoleon the third ruled during the "
            "eighteen fifties, for example after World War One but before "
            "World War Two."
        )

        result = normalizer.normalize(input_text)
        assert result == expected

    def test_richard_iii_example(self):
        """Test the original problematic example."""
        input_text = (
            "Richard III (2 October 1452 – 22 August 1485) was King of "
            "England from the 3rd decade of the 15th century, i.e., during "
            "the 1480s."
        )
        expected = (
            "Richard the third (2 October 1452 – 22 August 1485) was King "
            "of England from the third decade of the fifteenth century, "
            "that is during the fourteen eighties."
        )

        result = normalize_for_tts(input_text)
        assert result == expected

    def test_phase_specific_normalization(self):
        """Test that phase-specific normalization works."""
        normalizer = TTSNormalizer()

        text = (
            "Richard III ruled in the 19th century during the 1980s, "
            "e.g., after World War II."
        )

        # Phase 1 only (should handle royal names, ordinals, abbreviations)
        phase1_result = normalizer.normalize(text, phase="phase1")
        expected_phase1 = (
            "Richard the third ruled in the nineteenth century during the "
            "1980s, for example after World War II."
        )
        assert phase1_result == expected_phase1

        # Phase 2 only (should handle decades, wars)
        phase2_result = normalizer.normalize(text, phase="phase2")
        expected_phase2 = (
            "Richard III ruled in the 19th century during the nineteen "
            "eighties, e.g., after World War Two."
        )
        assert phase2_result == expected_phase2

        # All phases
        full_result = normalizer.normalize(text, phase="all")
        expected_full = (
            "Richard the third ruled in the nineteenth century during the "
            "nineteen eighties, for example after World War Two."
        )
        assert full_result == expected_full


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_empty_text(self):
        """Test normalization of empty text."""
        assert normalize_for_tts("") == ""

    def test_no_matching_patterns(self):
        """Test text with no patterns to normalize."""
        text = "This is plain text with no special patterns."
        assert normalize_for_tts(text) == text

    def test_boundary_conditions(self):
        """Test pattern boundaries."""
        normalizer = TTSNormalizer()

        # Test that patterns only match at word boundaries
        test_cases = [
            "Richard33III",  # Should not match
            "19thabc",      # Should not match
            "ae.g.bc",      # Should not match as full word
        ]

        for text in test_cases:
            result = normalizer.normalize(text)
            assert result == text

    def test_malformed_patterns(self):
        """Test handling of malformed patterns."""
        normalizer = TTSNormalizer()

        # These should not crash and should remain unchanged
        test_cases = [
            "Richard XIIII",  # Invalid Roman numeral
            "The 0th century",  # Zero ordinal
            "c. abcd",  # Non-numeric after circa
        ]

        for text in test_cases:
            result = normalizer.normalize(text)
            # Should not crash and should handle gracefully
            assert isinstance(result, str)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

