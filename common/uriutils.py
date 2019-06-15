class URIUtils:

    @staticmethod
    def get_key_for_prefix(prefix):
        return prefix[prefix.rfind('/') + 1:prefix.rfind('#')]

    @staticmethod
    def get_prefix_and_suffix(uri):
        sep_char = '/'
        if '#' in uri:
            sep_char = '#'

        prefix = URIUtils.get_prefix(uri, sep_char)
        suffix = URIUtils.get_suffix(uri, sep_char)

        return prefix, suffix

    @staticmethod
    def get_prefix(uri, sep_char):
        return uri[:uri.rfind(sep_char) + 1]

    @staticmethod
    def get_suffix(uri, sep_char):
        return uri[uri.rfind(sep_char) + 1:]
