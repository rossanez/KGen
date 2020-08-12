# Facts Extractor

Facts identification and extraction, in form of subject, predicate, and object triples.

- Primary facts (related to main verb of sentences), through Open Information Extraction
  systems, or through Semantic Role Labeling.
- Secondary facts (related to noun phrases), through dependency parsing.

-- usage: python3 extractor.py -h

( ex: python3 extractor.py -f text.txt -p senna -s -v )