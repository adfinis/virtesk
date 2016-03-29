all:
	bash -c 'for i in *.pdf; do convert -density 600 -alpha deactivate $$i $$(basename $$i .pdf).png & done; echo -n "Waiting for childs..."; wait; echo done.'
