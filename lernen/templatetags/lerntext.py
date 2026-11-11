"""Kleiner, sicherer Markdown-Ersatz für Lektionen und Erklärungen."""

import re

from django import template
from django.utils.html import escape
from django.utils.safestring import mark_safe

register = template.Library()


def _inline(text: str) -> str:
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    return text


@register.filter
def lerntext(wert: str) -> str:
    teile, block = [], []
    zeilen = escape(wert or "").split("\n")
    i = 0
    while i < len(zeilen):
        z = zeilen[i]
        if z.strip().startswith("```"):
            code = []
            i += 1
            while i < len(zeilen) and not zeilen[i].strip().startswith("```"):
                code.append(zeilen[i])
                i += 1
            teile.append("<pre><code>" + "\n".join(code) + "</code></pre>")
        elif z.strip().startswith("- "):
            items = []
            while i < len(zeilen) and zeilen[i].strip().startswith("- "):
                items.append("<li>" + _inline(zeilen[i].strip()[2:]) + "</li>")
                i += 1
            teile.append("<ul>" + "".join(items) + "</ul>")
            continue
        elif z.strip().startswith("| "):
            rows = []
            while i < len(zeilen) and zeilen[i].strip().startswith("|"):
                zellen = [c.strip() for c in zeilen[i].strip().strip("|").split("|")]
                if not all(set(c) <= set("-: ") for c in zellen):
                    tag = "th" if not rows else "td"
                    rows.append("<tr>" + "".join(f"<{tag}>{_inline(c)}</{tag}>" for c in zellen) + "</tr>")
                i += 1
            teile.append('<div class="table-wrap"><table>' + "".join(rows) + "</table></div>")
            continue
        elif z.strip():
            absatz = [z]
            while i + 1 < len(zeilen) and zeilen[i + 1].strip() and not zeilen[i + 1].strip().startswith(("- ", "```", "| ")):
                i += 1
                absatz.append(zeilen[i])
            teile.append("<p>" + _inline("<br>".join(absatz)) + "</p>")
        i += 1
    return mark_safe("".join(teile))
