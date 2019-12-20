import os

from nltk.corpus import stopwords
from nltk.corpus import verbnet
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
from nltk.tree import Tree

from .stanfordcorenlp.corenlpwrapper import CoreNLPWrapper

class NLPUtils:

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

        classids = verbnet.classids(lemmatized_verb)
        if verbose:
            print('Class IDs for "{}": {}'.format(lemmatized_verb, classids))

        if len(classids) < 1:
            return None

        for id in classids:
            class_number = id[id.find('-')+1:]
            v = verbnet.vnclass(class_number)
            roles = [t.attrib['type'] for t in v.findall('THEMROLES/THEMROLE')]

            while len(roles) < 1 and len(v) > 0:
                fallback_class_number = class_number[:class_number.rfind('-')]
                if verbose:
                    print('No roles found for class {}, falling back to {}.'.format(class_number, fallback_class_number))
                class_number = fallback_class_number
                v = verbnet.vnclass(class_number)
                roles = [t.attrib['type'] for t in v.findall('THEMROLES/THEMROLE')]

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

