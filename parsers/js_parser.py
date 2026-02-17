

from tree_sitter import Parser, Language
import tree_sitter_javascript
from engine.parser_manager import ParserManager

JS_LANGUAGE = Language(tree_sitter_javascript.language())
parser = Parser(JS_LANGUAGE)


def parse(file_path: str):
    """
    Parse a JavaScript source file and return Tree-sitter tree.
    """
    with open(file_path, "rb") as f:
        source = f.read()

    tree = parser.parse(source)
    return tree



ParserManager.register("javascript", parse)
