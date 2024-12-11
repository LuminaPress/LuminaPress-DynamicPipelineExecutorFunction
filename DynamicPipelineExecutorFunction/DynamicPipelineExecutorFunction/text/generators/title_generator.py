import re
import unicodedata
from typing import List, Optional

social_medias = [
    "facebook",
    "instagram",
    "twitter",
    "tiktok",
    "linkedin",
    "snapchat",
    "pinterest",
    "reddit",
    "youtube",
    "whatsapp",
    "telegram",
    "tumblr",
    "wechat",
    "discord",
    "viber",
    "skype",
    "quora",
    "clubhouse",
    "flickr",
    "periscope",
    "line",
    "slack",
    "medium",
    "vero",
    "x",
    "myspace",
]


class TitleCondenser:
    def __init__(self, max_length: int = 80, style: str = "default"):
        """
        Initialize a universal title condenser.

        Args:
            max_length (int): Maximum length of the condensed title
            style (str): Condensing style ('default', 'punchy', 'professional')
        """
        self.max_length = max_length
        self.style = style.lower()

        # Predefined stop words and fillers to remove
        self.stop_words = {
            "default": {
                "the",
                "a",
                "an",
                "and",
                "or",
                "but",
                "in",
                "on",
                "at",
                "to",
                "for",
                "of",
                "with",
                "by",
            },
            "punchy": {
                "the",
                "a",
                "an",
                "and",
                "or",
                "but",
                "in",
                "on",
                "at",
                "to",
                "for",
                "of",
                "with",
                "by",
                "this",
                "that",
                "these",
                "those",
            },
            "professional": {
                "the",
                "a",
                "an",
                "and",
                "or",
                "but",
                "in",
                "on",
                "at",
                "to",
                "for",
                "of",
                "with",
                "by",
                "s",
                "r",
            },
        }

        # Domain-specific keyword boosters
        self.domain_keywords = {
            "news": [
                "breaking",
                "report",
                "analysis",
                "update",
                "reveals",
                "investigation",
            ],
        }

    def clean_text(self, text: str) -> str:
        """
        Clean and normalize input text.

        Args:
            text (str): Input text to clean

        Returns:
            str: Cleaned text
        """
        # Normalize unicode and remove special characters
        text = unicodedata.normalize("NFKD", text)

        # Remove URLs, platform tags, extra spaces
        text = re.sub(r"https?://\S+", "", text)
        text = re.sub(r"[\n\t\r]", " ", text)
        text = re.sub(r"[^\w\s\'-]", " ", text)
        text = re.sub(r"\s+", " ", text).strip()

        return text

    def condense_title(self, text: str, domain: Optional[str] = None) -> str:
        """
        Condense a long text into a catchy, concise title.

        Args:
            text (str): Input text to condense
            domain (str, optional): Specific domain for optimization

        Returns:
            str: Condensed, optimized title
        """
        # Clean the input text
        cleaned_text = self.clean_text(text)

        # Split into words
        words = cleaned_text.split()

        # Remove stop words
        stop_words = self.stop_words.get(self.style, self.stop_words["default"])
        meaningful_words = [word for word in words if word.lower() not in stop_words]

        # Domain-specific keyword boosting
        if domain:
            domain_boost_keywords = self.domain_keywords.get(domain, [])
            meaningful_words = sorted(
                meaningful_words,
                key=lambda word: 0 if word.lower() in domain_boost_keywords else 1,
            )

        # Limit to max length while preserving key information
        condensed_words = meaningful_words[:10]

        # Strategic capitalization
        capitalized_words = [
            (
                word.capitalize()
                if (index == 0 or word.lower() not in stop_words)
                else word.lower()
            )
            for index, word in enumerate(condensed_words)
        ]

        # Join and truncate if necessary
        condensed_title = " ".join(capitalized_words)

        # Final truncation
        if len(condensed_title) > self.max_length:
            condensed_title = condensed_title[: self.max_length - 3] + "..."

        return condensed_title


# Demonstration function
def demonstrate_condenser(
    texts: List[str],
    domain="news",
    style: str = "default",
    max_length: int = 80,
):
    """
    Demonstrate the title condenser across different inputs.

    Args:
        texts (List[str]): List of texts to condense
        domain (str, optional): Specific domain for optimization
        style (str): Condensing style
        max_length (int): Maximum title length
    """
    condenser = TitleCondenser(max_length=max_length, style=style)
    t = []
    for text in texts:
        condensed_title = condenser.condense_title(text, domain)
        t.append(condensed_title)
    for text in t:
        if "-" in text or any(
            [social_media.lower() in text.lower() for social_media in social_medias]
        ):
            continue
        return text
    return None


# news_examples = ag.get_titles()
# demonstrate_condenser(news_examples, , )
