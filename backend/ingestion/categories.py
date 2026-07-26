"""Single source of truth for knowledge base categories.

Every article in data/raw/article_links.json must belong to exactly one of
these. Keeping the list here (instead of inline strings across the pipeline)
means a new category is added in one place and validated everywhere.
"""


CATEGORIES = [
    "Healthy Diet",
    "Nutrition",
    "Food & Nutrients",
    "Fitness & Exercise",
    "Mental Health",
    "Sleep Health",
    "Heart Health",
    "Common Diseases",
    "Common Symptoms",
    "Immunity & Prevention",
    "Hydration",
    "Weight Management",
    "Women's Health",
    "Men's Health",
    "Child Health",
    "Senior Health",
    "Digestive Health",
    "Lifestyle & Wellness",
]


CATEGORY_SET = set(CATEGORIES)


def is_valid(category):

    return category in CATEGORY_SET


def validate(category):

    if not is_valid(category):

        raise ValueError(
            f"Unknown category: {category!r}. "
            f"Allowed categories: {', '.join(CATEGORIES)}"
        )

    return category
