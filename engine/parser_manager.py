
class ParserManager:
    registry = {}

    @classmethod
    def register(cls, language, parser):
        cls.registry[language] = parser

    @classmethod
    def get_parser(cls, language):
        return cls.registry.get(language)
