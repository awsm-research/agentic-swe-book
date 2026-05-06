#!/usr/bin/env bash
# Build PDF from the generated LaTeX for arXiv submission.
# Requires: python3, pdflatex (TeX Live or MiKTeX)
#
# Usage:
#   ./build_pdf.sh          # full build (md → tex → pdf)
#   ./build_pdf.sh --tex    # LaTeX → PDF only (skip Python conversion step)

set -euo pipefail

ARXIV_DIR="arxiv"
TEX_FILE="main.tex"
LOG="build.log"

# ── Step 1: Convert markdown → LaTeX (unless --tex flag given) ──
if [[ "${1:-}" != "--tex" ]]; then
  echo "==> Converting markdown to LaTeX..."
  python3 md_to_latex.py
  echo ""
fi

# ── Step 2: Compile LaTeX → PDF ──
if ! command -v pdflatex &>/dev/null; then
  echo "ERROR: pdflatex not found."
  echo "Install TeX Live:  brew install --cask mactex   (macOS)"
  echo "                   sudo apt install texlive-full (Ubuntu/Debian)"
  exit 1
fi

echo "==> Compiling LaTeX (pass 1/3)..."
cd "$ARXIV_DIR"

# Run three times: ToC + cross-refs need multiple passes
for pass in 1 2 3; do
  echo "    pass $pass..."
  pdflatex -interaction=nonstopmode -halt-on-error "$TEX_FILE" >> "$LOG" 2>&1 || {
    echo "ERROR: pdflatex failed on pass $pass. Check $ARXIV_DIR/$LOG"
    exit 1
  }
done

cd ..

PDF_OUT="$ARXIV_DIR/main.pdf"
if [[ -f "$PDF_OUT" ]]; then
  SIZE=$(du -sh "$PDF_OUT" | cut -f1)
  PAGES=$(python3 -c "
import subprocess, sys
try:
    result = subprocess.run(['pdfinfo', '$PDF_OUT'], capture_output=True, text=True)
    for line in result.stdout.splitlines():
        if 'Pages:' in line:
            print(line.split()[-1])
            sys.exit(0)
except Exception:
    pass
print('unknown')
")
  echo ""
  echo "==> Done!"
  echo "    PDF:   $PDF_OUT"
  echo "    Size:  $SIZE"
  echo "    Pages: $PAGES"
  echo ""
  echo "==> arXiv submission files are in: $ARXIV_DIR/"
  echo "    Upload main.tex + images/ directory (zip them together)"
else
  echo "ERROR: PDF not produced. Check $ARXIV_DIR/$LOG"
  exit 1
fi
