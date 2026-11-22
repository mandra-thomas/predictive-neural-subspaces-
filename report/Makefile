# Build the report. `make` builds main.pdf with latexmk; `make figs` refreshes figure copies from ../figures
# (that directory is gitignored, so the copies in report/figures/ are what the committed build uses).
FIGSRC := ../figures
FIGS := fig1_geometry_d5.pdf fig2_content_d5.pdf fig3_estimator_d5.pdf figS1_nesting_d5.pdf \
        fig4_slowmode_controls.pdf fig5_slowmode_examples.pdf

.PHONY: all figs clean distclean
all: main.pdf

main.pdf: main.tex references.bib neurips_2026.sty $(wildcard figures/*.pdf)
	latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex

figs:
	@mkdir -p figures
	@for f in $(FIGS); do [ -f $(FIGSRC)/$$f ] && cp $(FIGSRC)/$$f figures/ || echo "missing $$f"; done
	@[ -f $(FIGSRC)/residual/fig1_geometry_d5.pdf ] && cp $(FIGSRC)/residual/fig1_geometry_d5.pdf figures/fig1_geometry_d5_residual.pdf || true
	@[ -f $(FIGSRC)/residual/fig2_content_d5.pdf ] && cp $(FIGSRC)/residual/fig2_content_d5.pdf figures/fig2_content_d5_residual.pdf || true

clean:
	latexmk -c main.tex

distclean:
	latexmk -C main.tex
