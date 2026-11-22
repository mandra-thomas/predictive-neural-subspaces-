all: slides.pdf slides_notes.pdf presentation_andra-thomas.pdf

slides.pdf: slides.tex FORCE
	latexmk -pdf slides.tex

slides_notes.pdf: slides_notes.tex slides.tex FORCE
	latexmk -pdf slides_notes.tex

# Submission copy (course naming rule presentation_lastname1_lastname2.pdf); identical to slides.pdf.
presentation_andra-thomas.pdf: slides.pdf
	cp slides.pdf presentation_andra-thomas.pdf

clean:
	latexmk -c slides.tex slides_notes.tex

FORCE:

.PHONY: all clean FORCE
