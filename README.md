# Jupyter Quality Extension

This is an interactive quality assessment tool designed for Jupyter Notebook users developing Tier-1 research software. The extension integrates a set of quality metrics mapped to various software lifecycle stages, combining external tools and custom scripts.

## Features

- Evaluate the quality of code in Jupyter Notebooks
- Metrics tailored to different development stages (e.g., planning, development, testing, maintenance)
- Visual feedback and actionable results
- Integrated tools: Pylint, Radon, JSCPD, and self-written scripts

## Installation

### 1. Clone this repository

```
git clone https://github.com/yutong0310/jupyter-quality-extension.git
cd jupyter-quality-extension
```

### 2. (Optional) Set up a virtual environment

```
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies

```
pip install -r requirements.txt
```

## How to Use

1. Start Jupyter Notebook:

```
jupyter notebook
```

2. Open any notebook you want to analyze (or create a new one)

3. In a code cell, run:

```python
%run extension.py
```

4. A user interface will appear with:
   - Dropdown for lifecycle stage selection
   - Metric selection checkboxes
   - Input for target path or GitHub repository URL
   - Quality scan results displayed in notebook

## Project Structure

```
jupyter-quality-extension/
├── extension.py              # Main interface script
├── requirements.txt          # Required dependencies
├── README.md
├── tools/                    # Analysis modules
├── evaluation/               # Metric evaluation logic
├── lifecycle/                # Stage-metric mappings
├── ui/                       # UI components (if needed)
```

## Metric Overview

| Metric                   | Tool or Script     |
|--------------------------|--------------------|
| Code Smells              | Pylint             |
| Maintainability Index    | Radon              |
| Cyclomatic Complexity    | Radon              |
| Code Duplication         | JSCPD              |
| Comment Density          | Radon              |
| Software Size (LoC)      | Self-written       |
| Percentage of Assertions | Self-written       |
| Unit Tests               | Self-written       |

Additional metrics related to FAIRness, documentation, licensing, and openness are planned for integration.

## License

This project is licensed under the Apache License 2.0.  

## Maintainer

This project was developed by Yutong Li  
University of Amsterdam — Master Thesis 2025
