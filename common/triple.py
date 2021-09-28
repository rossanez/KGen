class Triple:

    __subject = None
    __predicate = None
    __object = None

    __sentence_number = None

    __subject_links = []
    __predicate_link = None
    __object_links = []

    def __init__(self, sn, s, p, o, sl=[], pl=None, ol=[]):
        self.__sentence_number = sn

        if s.find(':') > 0:
            self.__subject = s.strip()
        else:
            self.__subject = s.lower().strip()
        self.__predicate = p.strip() # no lowering here. It will always be an URI.
        if o.find(':') > 0:
            self.__object = o.strip()
        else:
            self.__object = o.lower().strip()

        self.__subject_links = sl
        self.__predicate_link = pl
        self.__object_links = ol

    def to_tuple(self):
        return (self.__subject, self.__predicate, self.__object)

    def to_string(self):
        if self.__subject.find(':') > 0: #Subject is not a String, it is a resource/link
            s_subj = '{}'.format(self.__subject)
        else:
            s_subj = '"{}"'.format(self.__subject)
        if self.__predicate.find(':') > 0: #Predicate is not a String, it is a resource/link
            s_pred = '{}'.format(self.__predicate)
        else:
            s_pred = '"{}"'.format(self.__predicate)
        if self.__object.find(':') > 0: #Object is not a String, it is a resource/link
            s_obj = '{}'.format(self.__object)
        else:
            s_obj = '"{}"'.format(self.__object)

        return f'{self.__sentence_number}\t{s_subj}\t{s_pred}\t{s_obj}'

    def __format_name(self, name):
        nospacesname = '_'.join(name.split())
        return ''.join([c for c in nospacesname if c.isalnum() or c == '_'])


    def to_turtle(self):
        prefixes = {'http://www.w3.org/1999/02/22-rdf-syntax-ns#': 'rdf', 'http://www.w3.org/2000/01/rdf-schema#': 'rdfs', 'http://www.w3.org/2002/07/owl#': 'owl', 'http://local/local.owl#': 'local'}
        classes = {}
        properties = {}
        part_relations = set()

        if self.__subject.find(':') > 0:
            s = self.__subject # It is already a resource/link
        else:
            s = 'local:{}'.format(self.__format_name(self.__subject))
            s_class = '{}\ta\trdf:Class'.format(s)
            s_label = 'rdfs:label\t"{}"'.format(self.__subject)
            classes.update({s: '{}\t;\n\t{}\t.'.format(s_class, s_label)})

            if len(self.__subject_links) > 0:
                part_relations.update(self.__get_parts(self.__subject_links, s))

        if self.__object.find(':') > 0:
            o = self.__object # It is already a resource/link
        else:
            o = 'local:{}'.format(self.__format_name(self.__object))
            o_class = '{}\ta\trdf:Class'.format(o)
            o_label = 'rdfs:label\t"{}"'.format(self.__object)
            classes.update({o: '{}\t;\n\t{}\t.'.format(o_class, o_label)})

            if len(self.__object_links) > 0:
                part_relations.update(self.__get_parts(self.__object_links, o))

        if self.__predicate.find(':') > 0: #and not self.__predicate.startswith('local:'):
            p = self.__predicate # It is already a resource/link
        else:
            if self.__predicate.startswith('local:'):
                p = self.__predicate
            else:
                p = 'local:{}'.format(self.__format_name(self.__predicate))
            p_class = '{}\ta\trdf:Property'.format(p)
            #p_domain = 'rdf:subject\t{}'.format(s)
            #p_range = 'rdf:object\t{}'.format(o)
            p_label = 'rdfs:label\t"{}"'.format(self.__predicate)
            #properties.update({p+p_range+p_label: '{}\t;\n\t{}\t;\n\t{}\t;\n\t{}\t.'.format(p_class, p_domain, p_range, p_label)})
            properties.update({p: '{}\t;\n\t{}\t.'.format(p_class, p_label)})

            if len(self.__predicate_link) > 0:
                part_relations.update(self.__get_parts([self.__predicate_link], p))

        relation = '{}\t{}\t{}\t.'.format(s, p, o)

        return prefixes, classes, properties, part_relations, relation

    def __get_typeof(self, type, target):
        line = type.split('\t')
        num_links = len(line) // 3 # Result as integer

        matched_types = []
        links = []
        matches = []
        for i in range(num_links):
            match_type = line[0 + 3*i]
            link = line[1 + 3*i]
            matched = line[2 + 3*i]

            if match_type == 'sameas' or match_type == 'synonym':
                match_type = 'owl:sameAs'
            # in case match_type == 'no_match', it will be kept as is

            if link == 'not_found': # not_found
                link = type

            matched_types += [match_type]
            links += [link]
            matches += [matched]

        return matched_types, links, matches

    def __get_parts(self, parts, full):
        if len(parts) == 0: return {}
        elif len(parts) == 1:
            match_types, links, matches = self.__get_typeof(parts[0], full)
            parts = set()
            for i in range(len(links)):
                if match_types[i] == 'no_match':
                    continue

                parts.add('{}\t{}\t{}\t.'.format(full, match_types[i], links[i]))
                parts.add('{}\trdfs:label\t"{}"\t.'.format(links[i], matches[i]))
            return parts
        else:
            part_relations = set()
            for part in parts:
                match_types, links, matches = self.__get_typeof(part, full)
                for i in range(len(links)):
                    if match_types[i] == 'no_match':
                        part_relations.add('local:{}\trdfs:label\t"{}"\t.'.format(self.__format_name(matches[i]), matches[i]))
                        part_relations.add('local:{}\trdfs:member\t{}\t.'.format(self.__format_name(matches[i]), full))
                    else:
                        part_relations.add('{}\trdfs:label\t"{}"\t.'.format(links[i], matches[i]))
                        part_relations.add('{}\trdfs:member\t{}\t.'.format(links[i], full))

            return part_relations

