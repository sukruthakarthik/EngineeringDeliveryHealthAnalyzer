def classify_rag(score: int) -> str:
    """Return 'Red', 'Amber', or 'Green' for a 0–100 health score.

    >>> classify_rag(80)
    'Green'
    >>> classify_rag(60)
    'Amber'
    >>> classify_rag(30)
    'Red'
    """
    if score >= 75:
        return "Green"
    if score >= 50:
        return "Amber"
    return "Red"
