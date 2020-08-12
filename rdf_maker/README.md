# RDF Maker

Combines the Facts Extractor and the Knowledge Base Linker outputs,
into a Turtle (Terse RDF Triple Language) file format.

- Triples file is required.
- Links file is optional. A non-ontology-linked KG is generated, in
  case such file is not provided.

-- usage: python3 maker.py -h

( ex: python3 maker.py -t text_triples.txt -l text_links.txt -v )