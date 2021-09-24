class Statement:

    __contents = None

    __statement_id = None

    __subject = None
    __predicate = None
    __object = None

    def __init__(self, id, contents):
        self.__statement_id = id

        self.__contents = contents.lower().strip()

    def add_subject(self, s):
        self.__subject = s

    def add_predicate(self, p):
        self.__predicate = p

    def add_object(self, o):
        self.__object = o

    def to_string(self):
        return '{}\t"{}"'.format(self.__statement_id, self.__contents)

    def __format_name(self):
        return self.__statement_id

    def to_turtle(self):
        s = 'local:{}'.format(self.__format_name())
        s_statement = '{}\ta\trdf:Statement'.format(s)
        s_label = 'rdfs:label\t"{}"'.format(self.__contents)

        return {s: '{}\t;\n\t{}\t.'.format(s_statement, s_label)}
