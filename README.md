

 StaticLens

StaticLens is a multi-language static code analysis tool designed to evaluate code quality and structural complexity across software repositories. It analyzes source files using established software engineering metrics and presents results through an interactive web-based dashboard.



 Overview

StaticLens supports static analysis for:

* Python
* C++
* Java
* JavaScript

It parses source code using Tree-sitter and computes:

* Cyclomatic Complexity
* Halstead Metrics
* Object-Oriented Structural Metrics

The tool supports both individual file uploads and full GitHub repository analysis.

---

 Features

* Multi-language parsing powered by Tree-sitter
* Per-function cyclomatic complexity calculation
* Halstead metrics (volume, difficulty, effort, estimated defects)
* Object-oriented structural analysis:

  * Number of classes
  * Number of methods
  * Number of attributes
  * Inheritance relationships
* Repository-level analysis
* Risk classification based on metric thresholds
* Interactive Streamlit dashboard
* Downloadable JSON reports

---

 Architecture

StaticLens follows a modular architecture:

 Parser Layer

* Detects programming language
* Uses Tree-sitter for AST generation

 Metric Engine

* Central MetricManager executes registered metric modules

 Metrics Implemented

* Cyclomatic Complexity
* Halstead Metrics
* OOP Structural Metrics

 Frontend

* Built using Streamlit
* Dashboard visualization
* Export functionality

 Future Enhancements

* AI-assisted metric interpretation (Version 3)
* Control-flow graph based complexity refinement
* Expanded language support
* Enhanced visualization and trend analysis

