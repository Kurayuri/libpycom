import re


class SyntaxUtils:
    class Class:
        @staticmethod
        def getAttrs(_obj):
            return {key: getattr(_obj, key) for key in dir(_obj)
                    if not key.startswith('__') and not key.endswith('__')}

    class Dict:
        @staticmethod
        def getDottedKey(_dict, dotted_key):
            keys = dotted_key.split('.')
            value = _dict

            for key in keys:
                value = value[key]
            return value

    class Str:
        @staticmethod
        def formatFString(_str, _context):
            # Match {xxx.xxx}
            pattern = re.compile(r'\{([^\{\}]+)\}')

            def replace_match(match):
                dotted_key = match.group(1)
                return str(SyntaxUtils.Dict.getDottedKey(_context, dotted_key))

            return pattern.sub(replace_match, _str)
