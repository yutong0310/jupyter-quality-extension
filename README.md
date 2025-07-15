# Jupyter Quality Extension

An interactive, lifecycle-aware quality assessment tool for research software developed in Jupyter Notebooks.  
This tool is designed for research software and helps researchers evaluate notebook quality using relevant metrics based on the software's development stage.

## Features

- Assess the quality of Jupyter-based research software projects
- Metrics tailored to different lifecycle stages (e.g., Development, Maintenance)
- Interactive notebook-based interface with pass/fail icons and improvement suggestions
- Automatically converts `.ipynb` notebooks into `.py` scripts for metric compatibility
- Modular design for easy extension and maintenance

## Installation

This project was developed and tested with:
- Python 3.13.2  
- pip 25.0

### 1. Clone this repository

```
git clone https://github.com/yutong0310/jupyter-quality-extension.git
cd jupyter-quality-extension
```

### 2. Install dependencies

```
pip install -r requirements.txt
```
```
npm install -g jscpd
```
```
brew install gitleaks # (MacOS) or refer to the official instructions: https://github.com/gitleaks/gitleaks
```

## How to Use

1. Start Jupyter Notebook:

```
jupyter notebook
```

2. Open any notebook you want to analyze 

3. In a code cell, run:

```python
%run extension.py
```

4. A user interface will appear with:
   - Dropdown for lifecycle stage selection
   - Input for target path or GitHub repository URL
   - Quality scan results displayed in notebook

## Project Structure

```
jupyter-quality-extension/
├── extension.py              # Main interface script
├── requirements.txt          # Required dependencies
├── tools/                    # Individual tool integrations
├── evaluation/               # Metric evaluation logic
├── lifecycle/                # Stage-metric mappings
├── README.md
```

## Metric Overview

| Quality Dimension       | Metric                        | Tool or Script     | Stage        |
|-------------------------|-------------------------------|--------------------|--------------|
| Maintainability         | Code Smells                   | Pylint             | Development  |
| Maintainability         | Maintainability Index         | Radon              | Development  |
| Maintainability         | Cyclomatic Complexity         | Radon              | Development  |
| Maintainability         | Code Duplication              | JSCPD              | Development  |
| Maintainability         | Comment Density               | Radon              | Development  |
| Maintainability         | Software Size (LoC)           | Custom Script      | Development  |
| Security                | Security Vulnerabilities      | Bandit             | Maintenance  |
| Security                | Leaked Credentials            | Gitleaks           | Maintenance  |
| FAIRness                | License Presence              | howfairis          | Maintenance  |
| FAIRness                | Public Repository             | howfairis          | Maintenance  |
| FAIRness                | Rich Metadata                 | howfairis          | Maintenance  |
| FAIRness                | Documentation Quality         | howfairis          | Maintenance  |
| Functional Suitability  | Percentage of Assertions      | Custom Script      | Testing      |
| Sustainability          | Dependency Management         | Custom Script      | Development  |


## License

This project is licensed under the Apache License 2.0.  

## Maintainer

This project was developed by Yutong Li  
University of Amsterdam — Master Thesis 2025
