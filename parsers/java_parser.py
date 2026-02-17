

from tree_sitter import Parser, Language
import tree_sitter_java
from engine.parser_manager import ParserManager
JAVA_LANGUAGE = Language(tree_sitter_java.language())
parser = Parser(JAVA_LANGUAGE)


def parse(file_path: str):
    """
    Parse a Java source file and return Tree-sitter tree.
    """
    with open(file_path, "rb") as f:
        source = f.read()

    tree = parser.parse(source)
    return tree


# Register parser
ParserManager.register("java", parse)
