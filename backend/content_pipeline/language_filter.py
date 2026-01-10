"""
Language Detection and Filtering Module

This module provides functionality to:
1. Detect the language of tender text (English, Oromifa, Sidama, Amharic, etc.)
2. Filter out non-English/Oromifa tenders for later processing
3. Validate language detection accuracy
"""

import re
from typing import Dict, List, Tuple
import logging

logger = logging.getLogger(__name__)


class LanguageDetector:
    """Detect and filter tender languages"""

    def __init__(self):
        """Initialize language patterns"""

        # Oromifa language patterns (already supported)
        self.oromifa_patterns = [
            r'\b(?:Waajjirri|Mootummaa|Naannoo|Oromiyaa|Oromiyaatti|bu\'ura|Aangoo)\b',
            r'\bBaankiin\s+\w+\s+W\.A\b',
            r'\bMana\s+(?:Murtii|daldaalaa|jireenyaa)\b',
            r'\bKutaa\s+Magaalaa\b',
            r'\bguyyaa|guyyaan\b',
        ]

        # Sidama language patterns (not yet supported)
        self.sidama_patterns = [
            r'\b(?:Sidaamu|Dagoomi|Qoqqowi|Mootimma|Daaeelu|Woradi)\b',
            r'\b(?:egensiishshi|Bakkalcho|gaazeexira|barrinni|kayise|geeshsha|mitte|mittente|lootera|garafato|taje|ledo|amadiisiise|shiqisha|dandaannohu)\b',
            r'\bWomaashshunn\b',
        ]

        # Amharic language patterns (limited support)
        self.amharic_patterns = [
            r'[\u1200-\u137F]',  # Ethiopic script range
        ]

        # English indicators
        self.english_patterns = [
            r'\b(?:invites?|invite|announces?|announce|seeks?|seek|would\s+like|requests?|request|has\s+received|intends?|wants?)\b',
            r'\b(?:eligible|interested|qualified|bidders?|contractors?|suppliers?)\b',
            r'\b(?:procurement|tender|quotation|proposal|bid|contract)\b',
            r'\b(?:Ministry|University|Bank|Corporation|Commission|Authority|Agency|Bureau|Office|Department)\b',
        ]

    def detect_language(self, text: str) -> Tuple[str, float]:
        """
        Detect the primary language of tender text

        Args:
            text: Tender text to analyze

        Returns:
            Tuple of (language, confidence)
            - language: 'english', 'oromifa', 'sidama', 'amharic', 'mixed', 'unknown'
            - confidence: 0.0 to 1.0
        """
        if not text or len(text.strip()) < 10:
            return ('unknown', 0.0)

        text_lower = text.lower()

        # Count pattern matches for each language
        oromifa_count = sum(1 for pattern in self.oromifa_patterns if re.search(pattern, text, re.IGNORECASE))
        sidama_count = sum(1 for pattern in self.sidama_patterns if re.search(pattern, text, re.IGNORECASE))
        amharic_count = sum(1 for pattern in self.amharic_patterns if re.search(pattern, text))
        english_count = sum(1 for pattern in self.english_patterns if re.search(pattern, text, re.IGNORECASE))

        # Calculate total matches
        total_matches = oromifa_count + sidama_count + amharic_count + english_count

        if total_matches == 0:
            return ('unknown', 0.0)

        # Determine primary language
        scores = {
            'oromifa': oromifa_count,
            'sidama': sidama_count,
            'amharic': amharic_count,
            'english': english_count
        }

        # Sort by score
        sorted_langs = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        primary_lang, primary_score = sorted_langs[0]

        # Check for mixed language (multiple languages with significant presence)
        significant_threshold = 0.3 * total_matches
        significant_langs = [lang for lang, score in sorted_langs if score >= significant_threshold]

        if len(significant_langs) > 1:
            # Mixed language
            confidence = primary_score / total_matches
            return ('mixed', confidence)

        # Calculate confidence
        confidence = primary_score / total_matches

        return (primary_lang, confidence)

    def is_supported_language(self, text: str) -> Tuple[bool, str, float]:
        """
        Check if tender language is currently supported

        Args:
            text: Tender text to analyze

        Returns:
            Tuple of (is_supported, language, confidence)
        """
        language, confidence = self.detect_language(text)

        # Currently supported languages
        supported = ['english', 'mixed']  # Mixed usually means English + Oromifa

        # Oromifa is supported if confidence is reasonable
        if language == 'oromifa' and confidence >= 0.3:
            supported.append('oromifa')

        is_supported = language in supported

        return (is_supported, language, confidence)

    def filter_supported_tenders(self, tenders: List[Dict]) -> Tuple[List[Dict], List[Dict]]:
        """
        Filter tenders by supported languages

        Args:
            tenders: List of tender dictionaries

        Returns:
            Tuple of (supported_tenders, unsupported_tenders)
        """
        supported = []
        unsupported = []

        for tender in tenders:
            # Combine title and description for better detection
            text = f"{tender.get('Title', '')} {tender.get('Description', '')}"

            is_supported, language, confidence = self.is_supported_language(text)

            if is_supported:
                supported.append(tender)
                logger.debug(f"Tender {tender.get('Title', '')[:50]}... detected as {language} (confidence: {confidence:.2f})")
            else:
                unsupported.append({
                    **tender,
                    'detected_language': language,
                    'confidence': confidence
                })
                logger.info(f"Filtered out tender (language: {language}, confidence: {confidence:.2f}): {tender.get('Title', '')[:80]}")

        logger.info(f"Filtered tenders: {len(supported)} supported, {len(unsupported)} unsupported")

        return (supported, unsupported)


def filter_csv_by_language(csv_path: str, output_path: str = None) -> Dict:
    """
    Filter CSV file by supported languages

    Args:
        csv_path: Path to input CSV file
        output_path: Path to output CSV file (optional)

    Returns:
        Dictionary with filtering statistics
    """
    import pandas as pd

    # Load CSV
    df = pd.read_csv(csv_path)

    # Convert to list of dicts
    tenders = df.to_dict('records')

    # Filter
    detector = LanguageDetector()
    supported, unsupported = detector.filter_supported_tenders(tenders)

    # Create filtered dataframe
    if supported:
        df_supported = pd.DataFrame(supported)

        if output_path:
            df_supported.to_csv(output_path, index=False)
            logger.info(f"Saved {len(supported)} supported tenders to {output_path}")

    # Statistics
    stats = {
        'total_tenders': len(tenders),
        'supported_tenders': len(supported),
        'unsupported_tenders': len(unsupported),
        'unsupported_breakdown': {}
    }

    # Break down unsupported by language
    for tender in unsupported:
        lang = tender.get('detected_language', 'unknown')
        stats['unsupported_breakdown'][lang] = stats['unsupported_breakdown'].get(lang, 0) + 1

    return stats


if __name__ == '__main__':
    # Test the language detector
    import logging
    logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')

    test_texts = [
        "The Ministry of Water and Energy now invites sealed bids from eligible bidders",
        "Mootummaa Biyyoolessaa Naannoo Oromiyaatti Waajjirri invites eligible bidders",
        "Sidaamu Dagoomi Qoqqowi Mootimma Daaeelu Woradi Womaashshunn kuni egensiishshi Bakkalcho gaazeexira",
        "Baankiin Sinqee W.A bu'ura Aangoo Labsii 97/1990 Guyyaan adda",
    ]

    detector = LanguageDetector()

    print("="*80)
    print("LANGUAGE DETECTION TEST")
    print("="*80)

    for i, text in enumerate(test_texts, 1):
        language, confidence = detector.detect_language(text)
        is_supported, _, _ = detector.is_supported_language(text)

        print(f"\nTest {i}:")
        print(f"Text: {text[:80]}...")
        print(f"Detected: {language} (confidence: {confidence:.2f})")
        print(f"Supported: {'Yes' if is_supported else 'No'}")
