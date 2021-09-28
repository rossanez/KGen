class Statement:

    __contents = None

    __statement_id = None

    __subject = None
    __predicate = None
    __object = None
    __others = []

    def __init__(self, id, contents):
        self.__statement_id = id.lower().strip()
        self.__contents = contents.lower().strip()
        self.__subject = None
        self.__predicate = None
        self.__object = None
        self.__others = []

    def set_subject(self, s):
        self.__subject = s

    def has_subject(self):
        return not self.__subject == None

    def set_predicate(self, p):
        self.__predicate = p

    def set_negative_predicate(self):
        if not self.__predicate == None:
            self.__predicate = f'not {self.__predicate}'

    def set_object(self, o):
        self.__object = o

    def has_object(self):
        return not self.__object == None

    def add_object(self, o):
        self.__object = f'{self.__object} {o}'

    def add_other(self, p, o):
        self.__others.append((p,o))

    def to_string(self):
        ret = '{}\t"{}"'.format(self.__statement_id, self.__contents)
        if not self.__subject is None:
            ret += '\n{}\t"{}"\trdf:subject\t"{}"'.format(self.__statement_id, self.__contents, self.__subject)
        if not self.__predicate is None:
            ret += '\n{}\t"{}"\trdf:predicate\t"{}"'.format(self.__statement_id, self.__contents, self.__predicate)
        if not self.__object is None:
            ret += '\n{}\t"{}"\trdf:object\t"{}"'.format(self.__statement_id, self.__contents, self.__object)
        for other in self.__others:
            ret += '\n{}\t"{}"\t{}\t"{}"'.format(self.__statement_id, self.__contents, other[0], other[1])

        return ret

    def __format_name(self):
        return self.__statement_id

    def get_res_id(self):
        return f'local:{self.__format_name()}'

    def to_turtle(self):
        prefixes = {'http://www.w3.org/1999/02/22-rdf-syntax-ns#': 'rdf', 'http://www.w3.org/2000/01/rdf-schema#': 'rdfs', 'http://local/local.owl#': 'local'}

        s = self.get_res_id()
        s_statement = '{}\ta\trdf:Statement'.format(s)
        s_label = 'rdfs:label\t"{}"'.format(self.__contents)

        # subject/predicate/object/others will be processed as Triple objects
        return prefixes, {s: '{}\t;\n\t{}\t.'.format(s_statement, s_label)}
