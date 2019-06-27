
class Triple:

    __subject = None
    __predicate = None
    __object = None

    __sentence_number = -1

    __subject_links = []
    __predicate_link = None
    __object_links = []

    def __init__(self, sn, s, p, o, sl=[], pl=None, ol=[]):
        self.__sentence_number = sn

        self.__subject = s
        self.__predicate = p
        self.__object = o

        self.__subject_links = sl
        self.__predicate_link = pl
        self.__object_link = ol

    def to_string(self):
        return '{}\t"{}"\t"{}"\t"{}"'.format(self.__sentence_number, self.__subject, self.__predicate, self.__object)

    def __format_name(self, name):
        return name.replace(' ', '_').replace('\'', '')

    def to_turtle(self):
        prefixes = {'http://www.w3.org/1999/02/22-rdf-syntax-ns#': 'rdf', 'http://www.w3.org/2000/01/rdf-schema#': 'rdfs', 'http://local/local.owl#': 'local'}
        classes = {}
        properties = {}
        part_relations = set()

        s = 'local:{}'.format(self.__format_name(self.__subject))
        s_class = '{}\ta\trdfs:Class'.format(s)
        s_label = 'rdfs:label\t"{}"'.format(self.__subject)
        classes.update({s: '{}\t;\n\t{}\t.'.format(s_class, s_label)})

        part_relations.update(self.__get_parts(self.__subject_links, s))

        o = 'local:{}'.format(self.__format_name(self.__object))
        o_class = '{}\ta\trdfs:Class'.format(o)
        o_label = 'rdfs:label\t"{}"'.format(self.__object)
        classes.update({o: '{}\t;\n\t{}\t.'.format(o_class, o_label)})

        part_relations.update(self.__get_parts(self.__object_links, s))

        p = 'local:{}'.format(self.__format_name(self.__predicate))
        p_class = '{}\ta\trdf:Property'.format(p)
        p_domain = 'rdf:subject\t{}'.format(s)
        p_range = 'rdf:object\t{}'.format(o)
        p_label = 'rdfs:label\t"{}"'.format(self.__predicate)
        properties.update({p+p_range+p_label: '{}\t;\n\t{}\t;\n\t{}\t;\n\t{}\t.'.format(p_class, p_domain, p_range, p_label)})

        part_relations.update(self.__get_parts([self.__predicate_link], p))

        relation = '{}\t{}\t{}\t.'.format(s, p, o)

        return prefixes, classes, properties, part_relations, relation

    def __get_typeof(self, type, target):
        match_type = type[type.find('_') + 1: type.rfind('_')]
        if not match_type: # not found
            link = type
        else:
            link = type[:type.find(match_type)-1]
        matched = type[type.find('\"') + 1:-1]
        return match_type, link, matched

    def __get_parts(self, parts, full):
        if len(parts) == 0: return {}
        elif len(parts) == 1 and not parts[0].startswith('notfound:'):
            match_type, link, matched = self.__get_typeof(parts[0], full)
            return {'{}\trdf:type\t{}\t.'.format(full, link), '{}\trdfs:label\t"{}"\t.'.format(link, matched)}
        else:
            part_relations = set()
            for part in parts:
                if not part.startswith('notfound'):
                    match_type, link, matched = self.__get_typeof(part, full)
                    part_relations.add('{}\tlocal:partOf\t{}\t.'.format(link, full))
                    part_relations.add('{}\trdfs:label\t"{}"\t.'.format(link, matched))
                else: # notfound:
                    ent = 'local:{}'.format(part[part.find(':')+1:])
                    part_relations.add('{}\tlocal:partOf\t{}\t.'.format(ent, full))

            part_relations.add('local:partof\trdf:type\tnci:C43743\t.')
            part_relations.add('nci:C43743\trdfs:label\t"{}"\t.'.format('Part Of'))

            return part_relations

