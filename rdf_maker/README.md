# RDF Maker

Combines the Facts Extractor and the Ontology Linker outputs,
into a Turtle (Terse RDF Triple Language) file format.

- Triples file is required.
- Links file is optional. A non-ontology-linked KG is generated, in
  case such file is not provided.

## Running:

```bash
$ python3 maker.py text_preprocessed_triples.txt -l text_preprocessed_links.txt
```
(syntax: python3 maker.py -h)
