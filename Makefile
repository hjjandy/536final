# basic tools
LATEX	= latex
BIBTEX	= bibtex
DVIPS	= dvips
PS2PDF	= ps2pdf

# build options 
OS	= $(shell echo -n $$OSTYPE)
ifeq ($(OS), cygwin)
# in windows '=' needs to be turned to '#'
PS2PDFOPT= -dCompatibilityLevel\#1.5 -dEmbedAllFonts\#true	\
	   -dPDFSETTINGS\#/prepress
else
PS2PDFOPT= -dCompatibilityLevel=1.5 -dEmbedAllFonts=true	\
	   -dPDFSETTINGS=/prepress
endif
DVIPSOPT =-Ppdf -tletter -D600 -G0

# sources
TEX_SRC	= *.tex
BIB_SRC	= *.bib
FIG_SRC = figs/*.eps

# default target
TARGET	= report

# phony targets
.PHONY: all clean

all: $(TARGET).pdf

$(TARGET).bbl: $(BIB_SRC)
	$(LATEX) $(TARGET)
	$(BIBTEX) $(TARGET)
	$(LATEX) $(TARGET)
	$(BIBTEX) $(TARGET)
	$(LATEX) $(TARGET)

$(TARGET).dvi: $(TEX_SRC) $(FIG_SRC) $(TARGET).bbl
	$(LATEX) $(TARGET)

$(TARGET).ps: $(TARGET).dvi
	$(DVIPS) $(DVIPSOPT) -o $@ $<

$(TARGET).pdf: $(TARGET).ps
	$(PS2PDF) $(PS2PDFOPT) $< $@

# clean
clean:
	rm -f *.aux *.bbl *.blg *.out *.log *.dvi *.ps $(TARGET).pdf
