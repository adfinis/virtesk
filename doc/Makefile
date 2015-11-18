MDFILES:=$(shell ls -1 *.md)
HTMLFILES=$(MDFILES:md=html)
all: $(HTMLFILES)
%.html: %.md
	pandoc -f markdown_github -o $@ $<

