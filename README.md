# KGen

Knowledge Graphs Generation from unstructured text

## Running instructions:

### 1. Start CoreNLP server:

```bash
$ python3 common/stanfordcorenlp/server.py
```
(syntax: python3 common/stanfordcorenlp/server.py -h)

### 2. With the server started, run the pipeline in another shell, e.g.:

```bash
$ python3 pipeline.py text.txt -p senna -s -k cso -ng
```
(syntax: python3 pipeline.py -h)

### Alternatively, each stage may be executed outside the pipeline, e.g.:

#### 2.1. Preprocessing:

```bash
$ cd preprocessor
$ python3 preprocessor.py text.txt
```
(syntax: python3 preprocessor.py -h)

#### 2.2. Facts extractor:

```bash
$ cd facts_extractor
$ python3 extractor.py text_preprocessed.txt -p senna -s
```
(syntax: python3 extractor.py -h)

#### 2.3. Ontology linker (Optional stage, used to obtain ontology links):

```bash
$ cd kb_linker
$ python3 linker.py text_preprocessed.txt -k cso
```
(syntax: python3 linker.py -h)

#### 2.4. RDF maker:

```bash
$ cd rdf_maker
$ python3 maker.py text_preprocessed_triples.txt -l text_preprocessed_links.txt
```
(syntax: python3 maker.py -h)

#### 2.5. PNG generator (Optional stage, used to obtain a PNG image representing the KG):

```bash
$ cd graph_generator
$ python3 generator.py text_preprocessed_kg.ttl
```
(syntax: python3 generator.py -h)

### 3. When done, stop the server

```bash
$python3 common/stanfordcorenlp/server.py -k
```
(or simply Ctrl+C in its shell)

## Citing KGen

* Rossanez, A.; Dos Reis, J. C.; Torres, R. S.; De Ribaupierre, H. [KGen: A Knowledge Graph Generator from Biomedical Scientific Literature.](http://dx.doi.org/10.1186/s12911-020-01341-5) BMC Medical Informatics and Decision Making, v. 20, p. 314, 2020.

* Rossanez, A.; Dos Reis, J. C. [Generating Knowledge Graphs from Scientific Literature of Degenerative Diseases.](http://ceur-ws.org/Vol-2427/SEPDA_2019_paper_8.pdf) In Proceedings of the 4th International Workshop on Semantics-Powered Data Mining and Analytics (SEPDA 2019), co-located with the 18th International Semantic Web Conference (ISWC 2019). Aachen: CEUR Workshop Proceedings, 2019. v. 2427. p. 12-23.
