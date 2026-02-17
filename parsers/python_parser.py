from tree_sitter import Parser, Language
import tree_sitter_python
from engine.parser_manager import ParserManager

PY_LANGUAGE = Language(tree_sitter_python.language())
parser = Parser(PY_LANGUAGE)


def parse(file_path: str):
    with open(file_path, "rb") as f:
        source = f.read()

    tree = parser.parse(source)
    return tree


ParserManager.register("python", parse)
