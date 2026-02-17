"""
Formula: CC = 1 + number of decision points
"""

from metrics.base_metric import BaseMetric
from engine.metric_manager import MetricManager


class CyclomaticMetric(BaseMetric):
    def analyze(self, tree, file_path: str, language: str) -> dict:
        function_complexities = {}
        
        def count_decisions(node):
            """Count decision points in a node."""
            count = 0
            node_type = node.type.lower()
            
            # Count if, for, while, case, catch
            if any(x in node_type for x in ['if_statement', 'for_statement', 'while_statement', 
                                             'case', 'catch']):
                count += 1
            
            # Count && and ||
            if node.type in ['&&', '||']:
                count += 1
            
            # Recursively count in children
            for child in node.children:
                count += count_decisions(child)
            
            return count
        
        def find_functions(node):
            """Find all functions and calculate their CC."""
            # Check if this is a function
            if 'function' in node.type or 'method' in node.type:
                # Get function name
                name = f"line_{node.start_point[0] + 1}"
                for child in node.children:
                    if 'identifier' in child.type:
                        name = child.text.decode('utf-8')
                        break
                
                # Calculate CC = 1 + decisions
                cc = 1 + count_decisions(node)
                function_complexities[name] = cc
            
            # Check children
            for child in node.children:
                find_functions(child)
        
        # Start analysis
        if tree and tree.root_node:
            find_functions(tree.root_node)
        
        # Return results
        if not function_complexities:
            return {"cyclomatic_complexity": {"per_function": {}}}
        
        return {
            "cyclomatic_complexity": {
                "max": max(function_complexities.values()),
                "average": round(sum(function_complexities.values()) / len(function_complexities), 2)
            }
        }


MetricManager.register(CyclomaticMetric())