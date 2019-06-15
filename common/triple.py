
class Triple:

   __subject = ''
   __predicate = ''
   __object = ''

   def __init__(self, s, p, o):
       self.__subject = s
       self.__predicate = p
       self.__object = o

   def __format_name(self, name):
       return name.replace(' ', '_').replace('\'', '')

   def get_turtle(self):
       prefixes = {'http://www.w3.org/1999/02/22-rdf-syntax-ns#': 'rdf', 'http://www.w3.org/2000/01/rdf-schema#': 'rdfs', 'http://local/local.owl#': 'local'}
       classes = {}
       properties = {}

       s = 'local:{}'.format(self.__format_name(self.__subject))
       s_class = '{}\ta\trdfs:Class'.format(s)
       s_label = 'rdfs:label\t"{}"'.format(self.__subject)
       classes.update({s: '{}\t;\n\t{}\t.'.format(s_class, s_label)})

       o = 'local:{}'.format(self.__format_name(self.__object))
       o_class = '{}\ta\trdfs:Class'.format(o)
       o_label = 'rdfs:label\t"{}"'.format(self.__object)
       classes.update({o: '{}\t;\n\t{}\t.'.format(o_class, o_label)})

       p = 'local:{}'.format(self.__format_name(self.__predicate))
       p_class = '{}\ta\trdf:Property'.format(p)
       p_domain = 'rdfs:domain\t{}'.format(s)
       p_range = 'rdfs:range\t{}'.format(o)
       p_label = 'rdfs:label\t"{}"'.format(self.__predicate)
       properties.update({p: '{}\t;\n\t{}\t;\n\t{}\t;\n\t{}\t.'.format(p_class, p_domain, p_range, p_label)})

       relation = '{}\t{}\t{}\t.'.format(s, p, o)

       return prefixes, classes, properties, relation
