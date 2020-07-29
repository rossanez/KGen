import itertools
import os
import re

from nltk import pos_tag, RegexpParser, tree, word_tokenize
from nltk.corpus import stopwords, verbnet, wordnet
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize, RegexpTokenizer
from nltk.tree import Tree

from .stanfordcorenlp.corenlpwrapper import CoreNLPWrapper

class NLPUtils:

    ENTITY_GRAMMAR = "ENTITY: {<R.*>*<HYPH>*<R.*>*<JJ.*>*<HYPH>*<JJ.*>*<HYPH>*<NN.*>*<HYPH>*<NN.*>+}"
    PUNCTUATION = ['.', ',', ':', ';']

    @staticmethod
    def adjust_tokens(contents, remove_punctuation=False):
        # This seems like a major overhead, maybe there is a better way...
        nlp = CoreNLPWrapper()
        annotated = nlp.annotate(contents,  properties={'annotators': 'tokenize, ssplit, pos'})

        resolved = ''
        for sentence in annotated['sentences']:
            for token in sentence['tokens']:
                if remove_punctuation and (token['pos'] in NLPUtils.PUNCTUATION or (token['index'] == 1 and token['pos'] == 'DT')):
                    continue

                if token['pos'] in NLPUtils.PUNCTUATION or token['pos'] == 'POS':
                    resolved = resolved.strip()

                resolved += token['word'] + ' '

            resolved = resolved.strip()
            resolved += '\n'

        return resolved.strip()

    @staticmethod
    def remove_stopwords(sentence):
        stop_words = set(stopwords.words('english'))
        word_tokens = word_tokenize(sentence)

        filtered_sentence = [w for w in word_tokens if not w.lower() in stop_words]

        return ' '.join(filtered_sentence)

    @staticmethod
    def is_stopword(word):
        stop_words = set(stopwords.words('english'))

        return word.lower() in stop_words

    @staticmethod
    def get_verbnet_args(verb, verbose=False):
        lemmatizer = WordNetLemmatizer()
        lemmatized_verb = lemmatizer.lemmatize(verb.lower(), 'v')

        classids = verbnet.classids(lemma=lemmatized_verb)
        if verbose:
            print('Class IDs for "{}": {}'.format(lemmatized_verb, classids))

        if len(classids) < 1:
            if verbose:
                print('No entry found on verbnet for "{}". Attempting WordNet synsets!'.format(lemmatized_verb))

            wn_synsets = wordnet.synsets(lemmatized_verb)
            for synset in wn_synsets:
                if len(synset.lemmas()) < 1:
                    continue

                candidate = str(synset.lemmas()[0].name())
                classids = verbnet.classids(lemma=candidate)
                if verbose:
                    print('Class IDs for "{}": {}'.format(candidate, classids))

                if len(classids) > 0:
                    break

            if len(classids) < 1:
                if verbose:
                    print('Unable to find entries on verbnet for neither of the synsets... Will go recursive now (which is not a good thing!)')

                for synset in wn_synsets:
                    if len(synset.lemmas()) < 1:
                        continue

                    candidate = str(synset.hypernyms()[0].lemmas()[0].name())
                    return NLPUtils.get_verbnet_args(candidate, verbose=verbose)

                if verbose:
                    print('Exhausted attempts... returning an empty list.')
                return []

        for id in classids:
            class_number = id[id.find('-')+1:]
            try:
                v = verbnet.vnclass(class_number)
                roles = [t.attrib['type'] for t in v.findall('THEMROLES/THEMROLE')]
                pass
            except ValueError:
                print('VN class number not found: {}'.format(class_number))

                # Will handle these both below
                v = [None]
                roles = []
                pass

            while len(roles) < 1 and len(v) > 0:
                fallback_class_number = class_number[:class_number.rfind('-')]
                if verbose:
                    print('No roles found for class {}, falling back to {}.'.format(class_number, fallback_class_number))
                class_number = fallback_class_number

                try:
                    v = verbnet.vnclass(class_number)
                    roles = [t.attrib['type'] for t in v.findall('THEMROLES/THEMROLE')]
                    pass
                except ValueError:
                    # Go on with the loop
                    v = [None]
                    roles = []
                    pass

            if len(roles) > 0:
                if verbose:
                    print('Roles found: {}'.format(roles))

                return roles

        return None

    @staticmethod
    def dependency_parse(contents, deps_key='basicDependencies', verbose=False):
        nlp = CoreNLPWrapper()
        annotated = nlp.annotate(contents, properties={'annotators': 'tokenize, ssplit, pos, lemma, ner, depparse'})

        dependencies = list()
        for sentence in annotated['sentences']:
            for dependency in sentence[deps_key]:
                dep_tuple = (dependency['governorGloss'], dependency['dep'], dependency['dependentGloss'])
                if verbose:
                    print('{} --{}--> {}'.format(dep_tuple[0], dep_tuple[1], dep_tuple[2]))

                dependencies.append(dep_tuple)

        return dependencies

    @staticmethod
    def extract_entities_and_relations(contents):
        print('Determining the noun-phrases (possible entities) and verbs (possible predicates). \n Please wait, as it may take a while ...')
        nlp = CoreNLPWrapper()
        annotated = nlp.annotate(contents, properties={'annotators': 'tokenize, ssplit, pos, lemma, ner, parse'})

        verb_set = set()
        entity_set = set()
        for sentence in annotated['sentences']:
            for token in sentence['tokens']:
                if token['pos'].startswith('VB'):
                    verb_set.add(token['word'])

            parsed_sentence = sentence['parse'].replace('\n', '')
            parse_tree = Tree.fromstring(parsed_sentence)
            for sub_tree in parse_tree.subtrees():
                if sub_tree.label() == 'NP':
                    np_entity = NLPUtils.adjust_tokens(' '.join(sub_tree.leaves()), remove_punctuation=True)
                    if np_entity: # not empty
                        if np_entity.endswith('.'):
                            np_entity = np_entity.replace('.', '') # needed due to a tokenizer bug
                        entity_set.add(np_entity)

        return entity_set, verb_set

    @staticmethod
    def extract_candidate_entities(contents):
        candidates = NLPUtils.__extract_entity_candidates_using_grammar(contents)
        #candidates = candidates.union(NLPUtils.__extract_entity_candidates_delimited_by_stopwords(contents))
        return candidates

    @staticmethod
    def __extract_entity_candidates_delimited_by_stopwords(contents):
        tokenizer = RegexpTokenizer(r'[\w\-\(\)]*')
        tokens = tokenizer.tokenize(contents)
        filtered_words = [a for a in [w if w not in stopwords.words('english') else ':delimiter:' for w in tokens] if a != '']
        matrix_of_tokens = [list(g) for k,g in itertools.groupby(filtered_words,lambda x: x == ':delimiter:') if not k]
        return {" ".join(row).lower() for row in matrix_of_tokens}

    @staticmethod
    def __extract_entity_candidates_using_grammar(contents):
        pos_tags = pos_tag(word_tokenize(contents))

        grammar_parser = RegexpParser(NLPUtils.ENTITY_GRAMMAR)

        candidates = set()
        pos_tags_with_grammar = grammar_parser.parse(pos_tags)
        for node in pos_tags_with_grammar:
            if isinstance(node, tree.Tree) and node.label() == 'ENTITY':
                candidate = ''
                for leaf in node.leaves():
                    #part = re.sub('[\=\,\…\’\'\+\-\–\“\”\"\/\‘\[\]\®\™\%]', ' ', leaf[0])
                    #part = re.sub('\.$|^\.', '', part)
                    #part = part.lower().strip()
                    candidate += ' ' + leaf[0]
                candidate = re.sub('\.+', '.', candidate)
                candidate = re.sub('\s+', ' ', candidate)
                candidates.add(candidate.strip())
        return candidates

