all:
	bash -c 'for i in *.pdf; do { convert -density 600 -alpha deactivate $$i $$(basename $$i .pdf).png; convert -resize 800x565 $$(basename $$i .pdf).png $$(basename $$i .pdf)-small.png; } & done; echo -n "Waiting for childs..."; wait; echo done.'
