from tree_sitter import Language, Parser
import tree_sitter_cpp
from engine.parser_manager import ParserManager

CPP_LANGUAGE = Language(tree_sitter_cpp.language())

parser = Parser(CPP_LANGUAGE)


def parse(file_path: str):
    with open(file_path, "rb") as f:
        source_code = f.read()

    tree = parser.parse(source_code)
    return tree


ParserManager.register("cpp", parse)
