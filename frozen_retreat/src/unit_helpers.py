"""Unit and table helpers for the frozen retreat trade study."""

from __future__ import annotations


def km_s_to_m_s(v_km_s: float) -> float:
    """Convert km/s to m/s."""
    return v_km_s * 1000.0


def hours_to_seconds(hours: float) -> float:
    """Convert hours to seconds."""
    return hours * 3600.0


def days_to_seconds(days: float) -> float:
    """Convert days to seconds."""
    return days * 86400.0


def metric_tons_to_kg(m_t: float) -> float:
    """Convert metric tons to kilograms."""
    return m_t * 1000.0


def kg_to_metric_tons(m_kg: float) -> float:
    """Convert kilograms to metric tons."""
    return m_kg / 1000.0


def markdown_table(headers: list[str], rows: list[list[object]]) -> str:
    """Render a simple markdown table from headers and rows."""
    head = "| " + " | ".join(headers) + " |"
    sep = "| " + " | ".join(["---"] * len(headers)) + " |"
    body = ["| " + " | ".join(str(v) for v in row) + " |" for row in rows]
    return "\n".join([head, sep] + body)
