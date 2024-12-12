import re
import unicodedata
from typing import List, Optional
from collections import Counter


class UniversalTitleExtractor:
    def __init__(self, domain: Optional[str] = None):
        """
        Initialize a universal title extractor with optional domain-specific optimization.

        Args:
            domain (str, optional): Specific domain for more targeted extraction
                                    (e.g., 'news', 'tech', 'sports', 'entertainment')
        """
        self.domain_strategies = {
            "news": {
                "key_words": ["breaking", "report", "analysis", "update"],
                "priority_sources": ["reuters", "ap", "associated press", "bloomberg"],
            },
            "tech": {
                "key_words": ["innovation", "breakthrough", "technology", "startup"],
                "priority_sources": ["techcrunch", "wired", "verge", "mit"],
            },
            "sports": {
                "key_words": ["championship", "victory", "tournament", "match"],
                "priority_sources": ["espn", "sports illustrated", "bleacher report"],
            },
            "entertainment": {
                "key_words": ["exclusive", "interview", "premiere", "trailer"],
                "priority_sources": [
                    "variety",
                    "hollywood reporter",
                    "entertainment weekly",
                ],
            },
        }

        self.domain = domain.lower() if domain else None

    def clean_text(self, text: str) -> str:
        """
        Comprehensively clean input text.

        Args:
            text (str): Input text to clean

        Returns:
            str: Cleaned text
        """
        # Remove URLs, extra whitespaces, platform tags
        text = re.sub(r"https?://\S+", "", text)
        text = re.sub(r"[\n\t\r]", " ", text)
        text = re.sub(r"[^\w\s\'-]", " ", text)
        text = re.sub(r"\s+", " ", text).strip()

        return text

    def score_title(self, text: str, candidates: List[str]) -> int:
        """
        Score a title based on multiple factors.

        Args:
            text (str): Title to score
            candidates (List[str]): All candidate titles

        Returns:
            int: Calculated score
        """
        text = text.lower()
        score = 0

        # Length preference (prefer titles between 10-120 characters)
        if 10 <= len(text) <= 120:
            score += 20

        # Domain-specific boosting
        if self.domain and self.domain in self.domain_strategies:
            domain_strategy = self.domain_strategies[self.domain]
            score += sum(word in text for word in domain_strategy["key_words"]) * 10
            score += (
                sum(
                    source in text
                    for source in domain_strategy.get("priority_sources", [])
                )
                * 15
            )

        # Uniqueness boost
        word_freq = Counter(text.split())
        unique_words = len([word for word, count in word_freq.items() if count == 1])
        score += unique_words * 5

        # Prefer more informative titles
        informative_words = [
            "how",
            "why",
            "what",
            "when",
            "where",
            "new",
            "first",
            "major",
            "big",
            "important",
            "key",
            "reveals",
        ]
        score += sum(word in text for word in informative_words) * 8

        # Penalize overly generic or noisy titles
        generic_words = [
            "news",
            "update",
            "post",
            "article",
            "says",
            "report",
            "x",
            "reddit",
            "linkedin",
            "twitter",
        ]
        score -= sum(word in text for word in generic_words) * 5

        return score

    def extract_title(self, candidates: List[str]) -> str:
        """
        Extract the most representative title from a list of candidates.

        Args:
            candidates (List[str]): List of potential titles

        Returns:
            str: The most representative, cleaned title
        """
        # Clean candidates
        cleaned_candidates = [
            self.clean_text(candidate)
            for candidate in candidates
            if len(self.clean_text(candidate)) > 5
        ]

        # Remove exact duplicates
        cleaned_candidates = list(dict.fromkeys(cleaned_candidates))

        if not cleaned_candidates:
            return "No Valid Title Found"

        # Select best title
        best_title = max(
            cleaned_candidates, key=lambda x: self.score_title(x, cleaned_candidates)
        )

        # Strategic capitalization
        words = best_title.split()
        important_words = {
            "a",
            "an",
            "the",
            "and",
            "but",
            "or",
            "for",
            "nor",
            "on",
            "at",
            "to",
            "from",
            "by",
            "with",
            "of",
            "in",
        }

        capitalized_words = [
            (
                word.capitalize()
                if (index == 0 or word.lower() not in important_words)
                else word.lower()
            )
            for index, word in enumerate(words)
        ]

        return " ".join(capitalized_words)


# Demonstration function
def demonstrate_extractor(candidates: List[str], domain: Optional[str] = None):
    """
    Demonstrate the universal title extractor.

    Args:
        candidates (List[str]): List of candidate titles
        domain (str, optional): Specific domain for extraction
    """
    extractor = UniversalTitleExtractor(domain)
    best_title = extractor.extract_title(candidates)

    print(f"{'='*50}")
    print(f"Domain: {domain or 'Generic'}")
    print(f"{'='*50}")
    print("Candidates:")
    for candidate in candidates:
        print(f"- {candidate}")
    print("\nExtracted Title:", best_title)
    print("\n")


# Example usage across different domains
news_examples = [
    'Ars Technica on X: "Latest James Webb data hints at new physics in Universe’s expansion https://t.co/fsfhbQ8l0k" / X',
    "Latest James Webb data hints at new physics in Universe’s expansion | These latest findings further support the Hubble Space Telescope's prior expansion rate measurements. : r/space",
    "Latest James Webb data hints at new physics in Universe’s expansion - 'Ars Technica' News Summary (United States) | BEAMSTART",
    "Ground News - New Telescope Data Deepens Mystery of Universe's Expansion",
    "\n\tWebb telescope confirms the universe is expanding at an unexpected rate - The Hindu\n",
    'Ars Technica: "Latest James Webb data hints a…" - Mastodon',
    "Bredec GmbH on LinkedIn: Latest James Webb data hints at new physics in Universe’s expansion",
    "Webb telescope's largest study of universe expansion confirms challenge to cosmic theory | Hub",
    "Space Telescope Data Reignites Debate Over How Fast Our Universe Is Expanding - Slashdot",
    "Latest James Webb data hints at new physics in Universe’s expansion : news",
]

# Demonstrate across different domains
demonstrate_extractor(news_examples, "news")

# Generic demonstration
generic_examples = [
    'Ars Technica on X: "Latest James Webb data hints at new physics in Universe’s expansion https://t.co/fsfhbQ8l0k" / X',
    "Latest James Webb data hints at new physics in Universe’s expansion | These latest findings further support the Hubble Space Telescope's prior expansion rate measurements. : r/space",
    "Latest James Webb data hints at new physics in Universe’s expansion - 'Ars Technica' News Summary (United States) | BEAMSTART",
    "Ground News - New Telescope Data Deepens Mystery of Universe's Expansion",
    "\n\tWebb telescope confirms the universe is expanding at an unexpected rate - The Hindu\n",
    'Ars Technica: "Latest James Webb data hints a…" - Mastodon',
    "Bredec GmbH on LinkedIn: Latest James Webb data hints at new physics in Universe’s expansion",
    "Webb telescope's largest study of universe expansion confirms challenge to cosmic theory | Hub",
    "Space Telescope Data Reignites Debate Over How Fast Our Universe Is Expanding - Slashdot",
    "Latest James Webb data hints at new physics in Universe’s expansion : news",
]
demonstrate_extractor(generic_examples)
