###function of this analyzer is 
# to detect the language 
# call the parsermanager for the respective language parser
# generate the tree for the parser
# call the metrics manager wiht input as tree
# tree=parse("dummy.py")
# cc=calculate_cyclomatic_complexity(tree)
# print(cc)
#source venv/bin/activate
import os
from engine.parser_manager import ParserManager
from engine.metric_manager import MetricManager
from core.file_scanner import FileScanner
from core.github_clone import GitHubCloner
import parsers.cpp_parser
import parsers.python_parser
import parsers.java_parser
import parsers.js_parser

import metrics.cyclomatic
import metrics.halstead
import metrics.oop_metrics

EXTENSION_MAP = {
    "py": "python",
    "cpp": "cpp",
    "c": "cpp",
    "cc": "cpp",
    "cxx": "cpp",
    "h": "cpp",
    "hpp": "cpp",
    "java": "java",
    "js": "javascript",
    "jsx": "javascript",
}


def detect_language(filepath: str):
    _, ext = os.path.splitext(filepath)
    ext = ext[1:].lower()
    return EXTENSION_MAP.get(ext)

def print_tree(node, indent=0):
    print("  " * indent + node.type)
    
    for child in node.children:
        print_tree(child, indent + 1)

def analyzer(file_path: str):
    lang = detect_language(file_path)

    if not lang:
        print("language no detected")
        return None  # unsupported file

    parser = ParserManager.get_parser(lang)

    if not parser:
        print("parser not registered")
        return None  # parser not registered

    try:
        tree = parser(file_path)
    except Exception as e:
        return {
            "file": file_path,
            "language": lang,
            "error": f"Parsing failed: {str(e)}"
        }
    # print(tree.root_node)
    try:
        results = MetricManager.run_all(tree, file_path, lang)
    except Exception as e:
        return {
            "file": file_path,
            "language": lang,
            "error": f"Metric calculation failed: {str(e)}"
        }

    return {
        "file": file_path,
        "language": lang,
        "metrics": results
    }




def analyze_files(files, progress_callback=None):
   
    results = []
    total = len(files)
    
    for i, (file_path, language) in enumerate(files, 1):
        if progress_callback:
            progress_callback(i, total, file_path)
        
        result = analyzer(file_path)
        if result:
            results.append(result)
    
    return results


def analyze_directory(root_path: str, progress_callback=None):
   
    scanner = FileScanner()
    files = scanner.scan_directory(root_path)

    if progress_callback:
        progress_callback(f"Scanned {len(files)} supported files")

    results = analyze_files(files)
    return {
        "root_path": root_path,
        "total_files_scanned": len(files),
        "total_files_analyzed": len(results),
        "results": results
    }


def analyze_github_repo(repo_url: str, progress_callback=None, cleanup=True):
    
    cloner = GitHubCloner()
    cloned_path = None

    try:
        cloned_path = cloner.clone_repo(repo_url, progress_callback=progress_callback)
        analysis_output = analyze_directory(cloned_path, progress_callback=progress_callback)
        analysis_output["repo_url"] = repo_url
        analysis_output["cloned_path"] = cloned_path
        return analysis_output
    finally:
        if cleanup:
            cloner.cleanup()


# from reports.json_report import generate_json_report
# from reports.html_report import generate_html_report
# result=analyzer(file_path)
# generate_json_report(results, "report.json")
# generate_html_report(results, "report.html")

            












# tree = parse("test.cpp")
# # print("start")
# # print(tree.root_node.type)
# # print("mid")
# # print(tree.root_node)
# def print_tree(node, prefix="", is_last=True):
#     connector = "└── " if is_last else "├── "
#     print(prefix + connector + node.type)

#     prefix += "    " if is_last else "│   "

#     child_count = len(node.children)

#     for i, child in enumerate(node.children):
#         is_child_last = i == child_count - 1
#         print_tree(child, prefix, is_child_last)


# print_tree(tree.root_node)
