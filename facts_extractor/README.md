# Facts Extractor

Facts identification and extraction, in form of subject, predicate, and object triples.

- Primary facts (related to main verb of sentences), through Open Information Extraction
  systems, or through Semantic Role Labeling.
- Secondary facts (related to noun phrases), through dependency parsing.

## Running:

```bash
$ python3 extractor.py text_preprocessed.txt -p senna -s
```
(syntax: python3 extractor.py -h)
