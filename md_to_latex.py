#!/usr/bin/env python3
"""
Convert mdBook markdown source to a single LaTeX file suitable for arXiv submission.
Usage: python md_to_latex.py
Output: arxiv/main.tex + arxiv/images/
"""

import re
import shutil
from pathlib import Path

SRC = Path("src")
OUT = Path("arxiv")
OUT.mkdir(exist_ok=True)

# Book metadata
TITLE = "AI-Native Software Engineering"
AUTHOR = "Kla Tantithamthavorn"
INSTITUTION = "Monash University"
EMAIL = ""
YEAR = "2026"

# Ordered list of files to include (from SUMMARY.md, excluding Monash-specific pages)
CHAPTERS = [
    ("preface", "Preface", None),
    ("about", "About the Author", None),
    # Part I
    ("chapter_1", "Software Engineering Fundamentals", "Part I: Software Engineering Fundamentals"),
    ("chapter_2", "Requirements Engineering", None),
    ("chapter_3", "Software Design, Architecture, and Patterns", None),
    ("chapter_4", "Software Quality \\& Testing", None),
    ("chapter_5", "Automated Code Review, Code Quality, and CI/CD", None),
    # Part II
    ("chapter_6", "Agentic Software Engineering: A New Paradigm", "Part II: Agentic Software Engineering"),
    ("chapter_7", "Configuring the Agent's World --- Context, Skills, and Tools", None),
    ("chapter_8", "Security of AI-Generated Code", None),
    ("chapter_9", "Security Concerns of Agentic AI Coding Tools", None),
    # Part III
    ("chapter_10", "Software Maintenance and Technical Debts", "Part III: Shipping Your Software Responsibly \\& Ethically"),
    ("chapter_11", "Software Versioning, Packaging, and Deployment", None),
    ("chapter_12", "Licenses, Ethics, and Responsible AI", None),
    # Tutorials
    ("tutorial_1", "Setting Up Python and GitLab", "Tutorials"),
    ("tutorial_2", "Eliciting Requirements from AI As Your Client", None),
    ("tutorial_3", "Designing a Learning Management System", None),
    ("tutorial_4", "Unit Testing 101", None),
    ("tutorial_5", "Code Quality and CI/CD", None),
    ("tutorial_6", "The AI-Assisted SDLC: From Spec to Code", None),
    ("tutorial_7", "The AI-Assisted SDLC: From Code to Well-Tested App", None),
    ("tutorial_8", "SAST, AI, and Human on Vulnerability Detection", None),
    ("tutorial_9", "Security Review in CI/CD Pipeline", None),
    ("tutorial_10", "Pay Down Debt on a Real Hotspot", None),
    ("tutorial_11", "Containerise and Ship a Three-Tier Application", None),
    ("tutorial_12", "Licences, Privacy, and Responsible AI in Practice", None),
]


BOX_DRAWING_MAP = {
    # Tree / directory chars → ASCII equivalents
    "└": "\\", "├": "|", "─": "-", "│": "|",
    "┌": "/", "┐": "\\", "┘": "/", "┤": "|",
    "┬": "+", "┴": "+", "┼": "+",
    # Other common non-ASCII in code blocks
    "→": "->", "←": "<-", "⇒": "=>", "⇐": "<=",
    "≤": "<=", "≥": ">=", "≠": "!=", "…": "...",
    "​": "",  # zero-width space
}


def sanitize_code_line(line: str) -> str:
    """Replace non-ASCII characters in code blocks with ASCII equivalents."""
    for char, replacement in BOX_DRAWING_MAP.items():
        line = line.replace(char, replacement)
    # Replace any remaining non-ASCII with '?'
    return line.encode("ascii", errors="replace").decode("ascii")


def escape_latex(text: str) -> str:
    """Escape special LaTeX characters, skipping already-escaped ones."""
    replacements = [
        ("\\", "\\textbackslash{}"),  # must be first
        ("&", "\\&"),
        ("%", "\\%"),
        ("$", "\\$"),
        ("#", "\\#"),
        ("_", "\\_"),
        ("{", "\\{"),
        ("}", "\\}"),
        ("~", "\\textasciitilde{}"),
        ("^", "\\textasciicircum{}"),
    ]
    for old, new in replacements:
        text = text.replace(old, new)
    return text


UNICODE_MAP = {
    # Math / comparison
    "≤": "$\\leq$", "≥": "$\\geq$", "≠": "$\\neq$", "≈": "$\\approx$",
    "→": "$\\rightarrow$", "←": "$\\leftarrow$", "↔": "$\\leftrightarrow$",
    "⇒": "$\\Rightarrow$", "⇐": "$\\Leftarrow$", "⇔": "$\\Leftrightarrow$",
    "∞": "$\\infty$", "∑": "$\\sum$", "∏": "$\\prod$", "∫": "$\\int$",
    "∈": "$\\in$", "∉": "$\\notin$", "⊂": "$\\subset$", "⊆": "$\\subseteq$",
    "∪": "$\\cup$", "∩": "$\\cap$", "∀": "$\\forall$", "∃": "$\\exists$",
    "±": "$\\pm$", "×": "$\\times$", "÷": "$\\div$", "·": "$\\cdot$",
    "√": "$\\sqrt{}$", "∝": "$\\propto$",
    # Quotes & dashes
    "‘": "`", "’": "'", "“": "``", "”": "''",
    "–": "--", "—": "---",
    # Symbols
    "©": "\\copyright{}", "®": "\\textregistered{}", "™": "\\texttrademark{}",
    "°": "$^\\circ$", "…": "\\ldots{}", "•": "\\textbullet{}",
    "α": "$\\alpha$", "β": "$\\beta$", "γ": "$\\gamma$", "δ": "$\\delta$",
    "ε": "$\\epsilon$", "λ": "$\\lambda$", "μ": "$\\mu$", "π": "$\\pi$",
    "σ": "$\\sigma$", "τ": "$\\tau$", "φ": "$\\phi$", "ω": "$\\omega$",
    "✓": "\\checkmark{}", "✗": "$\\times$",
    "​": "",  # zero-width space
}


def replace_unicode(text: str) -> str:
    for char, replacement in UNICODE_MAP.items():
        text = text.replace(char, replacement)
    return text


def md_inline_to_latex(text: str) -> str:
    """Convert inline markdown to LaTeX inline commands."""
    # Protect inline code first (extract, escape contents, restore)
    code_spans: list[str] = []
    def save_code(m: re.Match) -> str:
        inner = m.group(1).replace("&", "AMPERSAND_PLACEHOLDER").replace("%", "PERCENT_PLACEHOLDER")
        code_spans.append(inner)
        return f"CODESPAN_{len(code_spans)-1}_END"
    text = re.sub(r"`([^`]+)`", save_code, text)

    # Replace unicode characters before LaTeX escaping
    text = replace_unicode(text)

    # Escape LaTeX special characters in plain text
    text = text.replace("\\", "\\textbackslash{}")
    text = text.replace("&", "\\&")
    text = text.replace("%", "\\%")
    text = text.replace("$", "\\$")
    text = text.replace("#", "\\#")
    text = text.replace("~", "\\textasciitilde{}")
    text = text.replace("^", "\\textasciicircum{}")
    # Note: _ and { } handled carefully below to not break \commands

    # Bold (must come before italic)
    text = re.sub(r"\*\*(.+?)\*\*", r"\\textbf{\1}", text)
    text = re.sub(r"__(.+?)__", r"\\textbf{\1}", text)
    # Italic
    text = re.sub(r"\*(.+?)\*", r"\\textit{\1}", text)
    # Underscores: only treat as italic if surrounded by word chars
    text = re.sub(r"(?<!\w)_(.+?)_(?!\w)", r"\\textit{\1}", text)
    # Inline links — keep text, drop URL
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    # Bare URLs
    text = re.sub(r"https?://\S+", lambda m: "\\url{" + m.group(0).rstrip(".,);") + "}", text)

    # Escape remaining bare underscores (not part of \cmd{} or already escaped)
    # At this point italic/bold have been converted, so bare _ are literal underscores
    text = re.sub(r"(?<!\\)_", r"\\_", text)

    # Restore code spans as \texttt{}
    def restore_code(m: re.Match) -> str:
        idx = int(m.group(1))
        inner = code_spans[idx].replace("AMPERSAND_PLACEHOLDER", "\\&").replace("PERCENT_PLACEHOLDER", "\\%")
        inner = inner.replace("_", "\\_").replace("{", "\\{").replace("}", "\\}")
        return f"\\texttt{{{inner}}}"
    text = re.sub(r"CODESPAN_(\d+)_END", restore_code, text)

    return text


def md_to_latex_body(md_text: str, file_stem: str) -> str:
    """Convert a full markdown document body to LaTeX."""
    # Strip HTML comments (including mdBook {{#include}} directives and <!-- --> blocks)
    md_text = re.sub(r"<!--.*?-->", "", md_text, flags=re.DOTALL)
    # Strip mdBook preprocessor directives
    md_text = re.sub(r"\{\{#[^}]+\}\}", "", md_text)
    lines = md_text.splitlines()
    out = []
    in_code_block = False
    code_lang = ""
    in_table = False
    table_header_done = False
    in_quote = False
    quote_lines: list[str] = []
    list_stack: list[str] = []  # stack of 'ul' or 'ol'

    def flush_quote():
        nonlocal in_quote, quote_lines
        if in_quote and quote_lines:
            body = " ".join(q.lstrip("> ").strip() for q in quote_lines)
            out.append(f"\\begin{{quote}}\n\\textit{{{md_inline_to_latex(body)}}}\n\\end{{quote}}")
        in_quote = False
        quote_lines = []

    def close_lists():
        while list_stack:
            env = list_stack.pop()
            out.append(f"\\end{{{('itemize' if env == 'ul' else 'enumerate')}}}")

    i = 0
    while i < len(lines):
        line = lines[i]

        # ── Fenced code block ──
        if line.strip().startswith("```"):
            if in_code_block:
                out.append("\\end{lstlisting}")
                in_code_block = False
            else:
                flush_quote()
                close_lists()
                in_table = False
                code_lang = line.strip()[3:].strip().lower()
                # Only pass languages supported by the listings package
                LISTINGS_LANGS = {
                    "python", "bash", "sh", "shell", "c", "c++", "java", "javascript",
                    "sql", "html", "xml", "php", "ruby", "perl", "haskell", "r",
                    "matlab", "fortran", "ada", "lisp", "prolog", "pascal",
                }
                lang_norm = {"sh": "bash", "shell": "bash", "c++": "C++"}.get(code_lang, code_lang.capitalize())
                lang_opt = f"language={lang_norm}" if code_lang in LISTINGS_LANGS else ""
                out.append(f"\\begin{{lstlisting}}[{lang_opt}]" if lang_opt else "\\begin{lstlisting}")
                in_code_block = True
            i += 1
            continue

        if in_code_block:
            out.append(sanitize_code_line(line))
            i += 1
            continue

        # ── Blockquote ──
        if line.startswith(">"):
            in_quote = True
            quote_lines.append(line)
            i += 1
            continue
        else:
            flush_quote()

        # ── Horizontal rule ──
        if re.match(r"^---+\s*$", line) or re.match(r"^\*\*\*+\s*$", line):
            close_lists()
            # skip decorative rules; use \medskip instead
            out.append("\\medskip")
            i += 1
            continue

        # ── Headings ──
        heading_match = re.match(r"^(#{1,4})\s+(.+)", line)
        if heading_match:
            close_lists()
            in_table = False
            level = len(heading_match.group(1))
            title_text = md_inline_to_latex(heading_match.group(2).strip())
            # Strip leading chapter/tutorial number for sections (avoid duplication)
            mapping = {1: "chapter", 2: "section", 3: "subsection", 4: "subsubsection"}
            cmd = mapping.get(level, "subsubsection")
            out.append(f"\\{cmd}{{{title_text}}}")
            i += 1
            continue

        # ── Table ──
        if "|" in line and not in_code_block:
            # Detect separator row
            if re.match(r"^\s*\|?[\s|:-]+\|[\s|:-]*$", line):
                if not table_header_done:
                    table_header_done = True
                i += 1
                continue
            # Collect table rows
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if not in_table:
                col_spec = "l" * len(cells)
                out.append(f"\\begin{{tabular}}{{{col_spec}}}")
                out.append("\\hline")
                in_table = True
                table_header_done = False
            row = " & ".join(md_inline_to_latex(c) for c in cells) + " \\\\"
            out.append(row)
            # Peek: if next non-empty line is not a table row, close
            next_line = lines[i + 1].strip() if i + 1 < len(lines) else ""
            if "|" not in next_line:
                out.append("\\hline")
                out.append("\\end{tabular}")
                in_table = False
            i += 1
            continue
        else:
            if in_table:
                out.append("\\hline")
                out.append("\\end{tabular}")
                in_table = False

        # ── Unordered list ──
        ul_match = re.match(r"^(\s*)[-*+]\s+(.+)", line)
        if ul_match:
            indent = len(ul_match.group(1)) // 2
            content = md_inline_to_latex(ul_match.group(2))
            while len(list_stack) > indent + 1:
                env = list_stack.pop()
                out.append(f"\\end{{{('itemize' if env == 'ul' else 'enumerate')}}}")
            if len(list_stack) <= indent:
                list_stack.append("ul")
                out.append("\\begin{itemize}")
            out.append(f"  \\item {content}")
            i += 1
            continue

        # ── Ordered list ──
        ol_match = re.match(r"^(\s*)\d+\.\s+(.+)", line)
        if ol_match:
            indent = len(ol_match.group(1)) // 2
            content = md_inline_to_latex(ol_match.group(2))
            while len(list_stack) > indent + 1:
                env = list_stack.pop()
                out.append(f"\\end{{{('itemize' if env == 'ul' else 'enumerate')}}}")
            if len(list_stack) <= indent:
                list_stack.append("ol")
                out.append("\\begin{enumerate}")
            out.append(f"  \\item {content}")
            i += 1
            continue

        # ── Images ──
        img_match = re.match(r"!\[([^\]]*)\]\(([^)]+)\)", line.strip())
        if img_match:
            close_lists()
            alt = img_match.group(1)
            src = img_match.group(2)
            # Copy image to arxiv/images/
            src_path = SRC / src
            if src_path.exists():
                dest = OUT / "images" / src_path.name
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src_path, dest)
                img_ref = f"images/{src_path.name}"
            else:
                img_ref = src
            out.append(
                f"\\begin{{figure}}[h]\n"
                f"  \\centering\n"
                f"  \\includegraphics[width=0.85\\textwidth]{{{img_ref}}}\n"
                f"  \\caption{{{escape_latex(alt)}}}\n"
                f"\\end{{figure}}"
            )
            i += 1
            continue

        # ── Blank line ──
        if line.strip() == "":
            close_lists()
            out.append("")
            i += 1
            continue

        # ── Plain paragraph ──
        close_lists()
        out.append(md_inline_to_latex(line))
        i += 1

    flush_quote()
    close_lists()
    if in_table:
        out.append("\\hline\n\\end{tabular}")
    return "\n".join(out)


PREAMBLE = r"""\documentclass[11pt,a4paper]{book}

% Encoding & font
\usepackage[T1]{fontenc}
\usepackage[utf8]{inputenc}
\usepackage{lmodern}

% Page geometry
\usepackage[a4paper, margin=2.5cm]{geometry}

% Hyperlinks
\usepackage[colorlinks=true, linkcolor=blue, urlcolor=blue, citecolor=blue]{hyperref}
\usepackage{url}

% Code listings
\usepackage{listings}
\usepackage{xcolor}
\lstset{
  basicstyle=\ttfamily\small,
  breaklines=true,
  frame=single,
  backgroundcolor=\color{gray!10},
  keywordstyle=\color{blue}\bfseries,
  commentstyle=\color{green!50!black},
  stringstyle=\color{orange},
  numbers=left,
  numberstyle=\tiny\color{gray},
  numbersep=5pt,
  tabsize=2,
}

% Tables
\usepackage{booktabs}
\usepackage{longtable}
\usepackage{array}

% Graphics
\usepackage{graphicx}
\graphicspath{{images/}}

% Miscellaneous
\usepackage{parskip}
\usepackage{microtype}
\usepackage{amsmath}
\usepackage{amssymb}

% Part/chapter formatting
\usepackage{titlesec}
\titleformat{\chapter}[display]
  {\normalfont\huge\bfseries}{\chaptertitlename\ \thechapter}{20pt}{\Huge}

"""


def build_latex():
    parts_emitted: set[str] = set()
    body_parts: list[str] = []

    for file_stem, _title, part_label in CHAPTERS:
        md_path = SRC / f"{file_stem}.md"
        if not md_path.exists():
            print(f"  [skip] {md_path} not found")
            continue

        md_text = md_path.read_text(encoding="utf-8")

        # Emit \part{} if this chapter starts a new part
        if part_label and part_label not in parts_emitted:
            body_parts.append(f"\\part{{{escape_latex(part_label)}}}")
            parts_emitted.add(part_label)

        body_parts.append(f"% ── {file_stem} ──")
        body_parts.append(md_to_latex_body(md_text, file_stem))

    latex = (
        PREAMBLE
        + f"\\title{{{escape_latex(TITLE)}}}\n"
        + f"\\author{{{escape_latex(AUTHOR)} \\\\ {escape_latex(INSTITUTION)}}}\n"
        + f"\\date{{{YEAR}}}\n\n"
        + "\\begin{document}\n\n"
        + "\\frontmatter\n"
        + "\\maketitle\n"
        + "\\tableofcontents\n\n"
        + "\\mainmatter\n\n"
        + "\n\n".join(body_parts)
        + "\n\n\\end{document}\n"
    )

    out_file = OUT / "main.tex"
    out_file.write_text(latex, encoding="utf-8")
    print(f"Written: {out_file}  ({len(latex):,} chars)")

    # Copy images directory
    src_images = SRC / "images"
    if src_images.exists():
        dest_images = OUT / "images"
        if dest_images.exists():
            shutil.rmtree(dest_images)
        shutil.copytree(src_images, dest_images)
        print(f"Copied images → {dest_images}")


if __name__ == "__main__":
    build_latex()
