# ---------------------------------------------------------------------------
#  paper/Makefile — build every manuscript in this directory.
#
#  Invoked from the repo root as `make papers` (or `make paper-L3`); works
#  standalone too:
#
#      make -C paper              # every PDF
#      make -C paper L3-lambda-bounds.pdf
#      make -C paper verify       # the numeric verifiers
#      make -C paper clean        # PDFs and LaTeX droppings
#
#  Manuscripts are the .tex files at the top of paper/.  Files under shared/
#  are \input by them and are never built on their own; adding one to shared/
#  therefore rebuilds everything, which is what we want for the disclosure
#  blocks — a change to those must not reach one paper and miss another.
# ---------------------------------------------------------------------------

LATEX    ?= pdflatex
BIBTEX   ?= bibtex
LATEXOPT := -interaction=nonstopmode -halt-on-error -file-line-error

SOURCES := $(wildcard *.tex)
PDFS    := $(SOURCES:.tex=.pdf)
SHARED  := $(wildcard shared/*.tex) shared/refs.bib

.PHONY: all verify clean list toolchain
.DEFAULT_GOAL := all

all: toolchain $(PDFS)

# Fail with an instruction rather than with pdflatex's "command not found".
# docs/engineering-standards.md: a missing dependency is a question for the
# operator, never a silently degraded build.
toolchain:
	@command -v $(LATEX) >/dev/null 2>&1 || { \
	  echo "paper/Makefile: '$(LATEX)' not found."; \
	  echo "  macOS (MacPorts):  sudo port install texlive-latex texlive-latex-recommended"; \
	  echo "  macOS (MacTeX):    https://tug.org/mactex/"; \
	  echo "  Debian/Ubuntu:     sudo apt install texlive-latex-recommended texlive-latex-extra"; \
	  exit 1; }
	@command -v $(BIBTEX) >/dev/null 2>&1 || { \
	  echo "paper/Makefile: '$(BIBTEX)' not found (needed by the L papers)."; exit 1; }

# Three passes with a conditional bibtex between the first and second.  The
# bibtex run is conditional on the .aux actually naming a bibliography, because
# polyplets-report.tex and technical-report.tex still carry inline
# thebibliography environments and bibtex would exit 1 on them.
#
# Pass 3 is not superstition: pass 2 is where \cite keys and the \label targets
# inside the bibliography first resolve, and pass 3 is what settles page
# references to them.  A paper that still asks for a rerun after three passes
# says so on stderr rather than being left quietly stale.
%.pdf: %.tex $(SHARED)
	@echo "  LATEX   $<"
	@$(LATEX) $(LATEXOPT) $* >/dev/null || { $(LATEX) $(LATEXOPT) $*; exit 1; }
	@if grep -q '^\\bibdata' $*.aux 2>/dev/null; then \
	   echo "  BIBTEX  $*"; $(BIBTEX) $* >/dev/null || { $(BIBTEX) $*; exit 1; }; \
	   $(LATEX) $(LATEXOPT) $* >/dev/null; \
	 fi
	@$(LATEX) $(LATEXOPT) $* >/dev/null
	@grep -q 'Rerun to get' $*.log && echo "  WARNING $*: still asks for a rerun after 3 passes" >&2 || true
	@echo "  OK      $@"

# The numeric verifiers.  Each parses one manuscript and checks its printed
# numbers against banked results; each is red-first (it fails on a manuscript
# whose tables have drifted).  Run from the repo root, which is what they
# expect.
verify:
	@cd .. && python3 paper/verify_technical_report.py
	@cd .. && python3 paper/verify_l_papers.py
	@echo "paper/Makefile: verify_claims.py (polyplets-report.tex) needs build/g2;"
	@echo "  run it explicitly:  make build/g2 && python3 paper/verify_claims.py"

list:
	@echo "manuscripts:"
	@for f in $(SOURCES); do echo "  $$f"; done
	@echo "shared:"
	@for f in $(SHARED); do echo "  $$f"; done

clean:
	rm -f $(PDFS) *.aux *.log *.out *.bbl *.blg *.toc *.synctex.gz
