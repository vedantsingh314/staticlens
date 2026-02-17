
from metrics.base_metric import BaseMetric
from engine.metric_manager import MetricManager


class OOPMetrics(BaseMetric):

    def analyze(self, tree, file_path: str, language: str) -> dict:
        if not tree or not tree.root_node:
            return self._empty_result()

        classes = []
        total_methods = 0
        total_attributes = 0
        num_inheritance = 0

        # Language-specific node type mappings
        CLASS_NODES = {
            "class_declaration",    # Java, JavaScript
            "class_definition",     # Python
            "class_specifier",      # C++
        }

        METHOD_NODES = {
            "method_declaration",      # Java
            "method_definition",       # JavaScript, Python
            "function_definition",     # C++, Python (inside class)
            "constructor_declaration", # Java
        }

        FIELD_NODES = {
            "field_declaration",    # Java, C++
        }

        INHERITANCE_NODES = {
            "base_class_clause",    # C++
            "superclass",           # Python
            "extends_clause",       # Java
            "class_heritage",       # JavaScript
        }

        def is_class(node):
            """Check if node is a class."""
            return node.type in CLASS_NODES

        def is_method(node):
            """Check if node is a method/constructor."""
            return node.type in METHOD_NODES

        def is_field(node):
            """Check if node is a field declaration (Java/C++)."""
            if node.type in FIELD_NODES:
                # Ensure it's not a method (has function declarator)
                for child in node.children:
                    if "function" in child.type or is_method(child):
                        return False
                return True
            return False

        def is_inheritance(node):
            """Check if node represents inheritance."""
            return node.type in INHERITANCE_NODES

        def count_python_attributes(class_node):
            """Count Python attributes (self.x = y in __init__)."""
            attributes = set()
            
            def find_init(node):
                """Find __init__ method."""
                if node.type == "function_definition":
                    for child in node.children:
                        if child.type == "identifier":
                            name = child.text.decode('utf-8') if isinstance(child.text, bytes) else str(child.text)
                            if name == "__init__":
                                return node
                for child in node.children:
                    result = find_init(child)
                    if result:
                        return result
                return None
            
            def find_self_assignments(node):
                """Find self.x = y assignments."""
                if node.type == "assignment":
                    # Check left side for self.something
                    left = node.child_by_field_name("left")
                    if left and left.type == "attribute":
                        obj = left.child_by_field_name("object")
                        attr = left.child_by_field_name("attribute")
                        if obj and attr:
                            obj_text = obj.text.decode('utf-8') if isinstance(obj.text, bytes) else str(obj.text)
                            attr_text = attr.text.decode('utf-8') if isinstance(attr.text, bytes) else str(attr.text)
                            if obj_text == "self":
                                attributes.add(attr_text)
                
                for child in node.children:
                    find_self_assignments(child)
            
            init_method = find_init(class_node)
            if init_method:
                find_self_assignments(init_method)
            
            return len(attributes)

        def count_js_attributes(class_node):
            """Count JavaScript attributes (this.x = y in constructor)."""
            attributes = set()
            
            def find_this_assignments(node):
                """Find this.x = y assignments."""
                # assignment_expression with member_expression on left
                if node.type == "assignment_expression":
                    for child in node.children:
                        if child.type == "member_expression":
                            # Check if it's this.something
                            obj = child.child_by_field_name("object")
                            prop = child.child_by_field_name("property")
                            if obj and prop:
                                obj_text = obj.text.decode('utf-8') if isinstance(obj.text, bytes) else str(obj.text)
                                prop_text = prop.text.decode('utf-8') if isinstance(prop.text, bytes) else str(prop.text)
                                if obj_text == "this":
                                    attributes.add(prop_text)
                
                for child in node.children:
                    find_this_assignments(child)
            
            find_this_assignments(class_node)
            return len(attributes)

        def count_in_class(class_node, lang):
            """Count methods and attributes in a class."""
            methods = 0
            attributes = 0
            visited = set()
            
            def traverse_class(node, depth=0):
                nonlocal methods, attributes
                
                if depth > 50 or id(node) in visited:
                    return
                visited.add(id(node))
                
                # Skip nested classes
                if node != class_node and is_class(node):
                    return
                
                # Count methods
                if is_method(node):
                    methods += 1
                    return  # Don't descend into method body
                
                # Count field declarations (Java/C++)
                if is_field(node):
                    attributes += 1
                    return
                
                # Recurse to children
                for child in node.children:
                    traverse_class(child, depth + 1)
            
            # Traverse class body
            traverse_class(class_node)
            
            # Language-specific attribute counting
            if lang == "python":
                python_attrs = count_python_attributes(class_node)
                attributes += python_attrs
            elif lang == "javascript":
                js_attrs = count_js_attributes(class_node)
                attributes += js_attrs
            
            return methods, attributes

        def traverse(node, depth=0):
            """Find all classes in the tree."""
            nonlocal total_methods, total_attributes, num_inheritance

            if depth > 100:
                return

            # Found a class
            if is_class(node):
                # Check for inheritance
                has_inheritance = False
                for child in node.children:
                    if is_inheritance(child):
                        has_inheritance = True
                        break
                
                if has_inheritance:
                    num_inheritance += 1
                
                # Count methods and attributes
                methods, attributes = count_in_class(node, language)
                
                classes.append({
                    'methods': methods,
                    'attributes': attributes
                })
                total_methods += methods
                total_attributes += attributes
                
                return  # Don't descend (avoid nested classes)

            # Continue traversing
            for child in node.children:
                traverse(child, depth + 1)

        # Start analysis
        traverse(tree.root_node)

        # Calculate metrics
        num_classes = len(classes)
        
        avg_methods_per_class = (
            total_methods / num_classes if num_classes > 0 else 0
        )

        avg_attributes_per_class = (
            total_attributes / num_classes if num_classes > 0 else 0
        )

        method_attribute_ratio = (
            total_methods / total_attributes if total_attributes > 0 else 0
        )

        return {
            "oop_metrics": {
                "number_of_classes": num_classes,
                "number_of_methods": total_methods,
                "number_of_attributes": total_attributes,
                "inheritance_relationships": num_inheritance,
                "avg_methods_per_class": round(avg_methods_per_class, 2),
                "avg_attributes_per_class": round(avg_attributes_per_class, 2),
                "method_to_attribute_ratio": round(method_attribute_ratio, 2),
            }
        }

    def _empty_result(self):
        return {
            "oop_metrics": {
                "number_of_classes": 0,
                "number_of_methods": 0,
                "number_of_attributes": 0,
                "inheritance_relationships": 0,
                "avg_methods_per_class": 0,
                "avg_attributes_per_class": 0,
                "method_to_attribute_ratio": 0,
            }
        }


MetricManager.register(OOPMetrics())