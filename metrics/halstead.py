"""
Halstead Complexity Metric (Tree-sitter based, token-level)

Implements full Halstead theory:

n1 = number of distinct operators
n2 = number of distinct operands
N1 = total operators
N2 = total operands

Vocabulary (n) = n1 + n2
Program Length (N) = N1 + N2
Volume (V) = N * log2(n)
Difficulty (D) = (n1 / 2) * (N2 / n2)
Effort (E) = V * D
Estimated Bugs (B) = V / 3000
"""

import math
from collections import Counter
from metrics.base_metric import BaseMetric
from engine.metric_manager import MetricManager

OPERATOR_TYPES = {
    "binary_expression", "unary_expression", "update_expression",
    "assignment_expression", "comparison_expression", "logical_expression",
    "if_statement", "for_statement", "while_statement", "do_statement",
    "switch_statement", "case", "return_statement", "throw_statement",
    "call_expression", "new_expression", "delete_expression",
    "+=", "-=", "*=", "/=", "%=", "&&", "||", "==", "!=", 
    "<=", ">=", "<", ">", "+", "-", "*", "/", "%", "=",
    "!", "&", "|", "^", "~", "++", "--", ".", "->", "::", 
    "?", ":", ";", ",", "(", ")", "[", "]", "{", "}"
}

# Operand node types
OPERAND_TYPES = {
    "identifier", "number_literal", "string_literal", "char_literal",
    "true", "false", "null", "nullptr", "this", "super",
    "decimal_integer_literal", "hex_integer_literal", "float_literal"
}

# Keywords that are operators
OPERATOR_KEYWORDS = {
    "if", "else", "for", "while", "do", "switch", "case", "default",
    "return", "break", "continue", "throw", "try", "catch", "finally",
    "new", "delete", "sizeof", "typeof", "instanceof"
}



class HalsteadMetric(BaseMetric):

    def analyze(self, tree, file_path: str, language: str) -> dict:
        if not tree or not tree.root_node:
            return self._empty_result()

        operators = Counter()
        operands = Counter()

        def is_operator(node):
            """Check if node is an operator."""
            node_type = node.type
            
            # Check node type
            if node_type in OPERATOR_TYPES:
                return True
            
            # Check if it's a keyword operator
            if len(node.children) == 0:
                text = node.text.decode('utf-8') if isinstance(node.text, bytes) else str(node.text)
                if text in OPERATOR_KEYWORDS:
                    return True
            
            return False

        def is_operand(node):
           
            return node.type in OPERAND_TYPES

        def traverse(node):
            """Traverse tree and collect operators/operands."""
            
            if len(node.children) == 0:
                text = node.text.decode('utf-8') if isinstance(node.text, bytes) else str(node.text)
                
                
                if not text.strip():
                    return
                
              
                if is_operand(node):
                    operands[text] += 1
                    return
                
              
                if is_operator(node):
                    operators[text] += 1
                    return
            
       
            else:
                if is_operator(node):
                    
                    operators[node.type] += 1
            
        
            for child in node.children:
                traverse(child)

        traverse(tree.root_node)

       

        n1 = len(operators)              # distinct operators
        n2 = len(operands)               # distinct operands
        N1 = sum(operators.values())     # total operators
        N2 = sum(operands.values())      # total operands

        vocabulary = n1 + n2
        program_length = N1 + N2

        
        if vocabulary == 0:
            return self._empty_result()

        volume = program_length * math.log2(vocabulary) if vocabulary > 0 else 0
        difficulty = (n1 / 2) * (N2 / n2) if n2 > 0 else 0
        effort = volume * difficulty
        estimated_bugs = volume / 3000 if volume > 0 else 0

        return {
            "halstead": {
                "n1_distinct_operators": n1,
                "n2_distinct_operands": n2,
                "N1_total_operators": N1,
                "N2_total_operands": N2,
                "vocabulary": vocabulary,
                "program_length": program_length,
                "volume": round(volume, 2),
                "difficulty": round(difficulty, 2),
                "effort": round(effort, 2),
                "estimated_bugs": round(estimated_bugs, 3)
            }
        }

    def _empty_result(self):
        """Return empty result when no data."""
        return {
            "halstead": {
                "n1_distinct_operators": 0,
                "n2_distinct_operands": 0,
                "N1_total_operators": 0,
                "N2_total_operands": 0,
                "vocabulary": 0,
                "program_length": 0,
                "volume": 0,
                "difficulty": 0,
                "effort": 0,
                "estimated_bugs": 0
            }
        }

MetricManager.register(HalsteadMetric())