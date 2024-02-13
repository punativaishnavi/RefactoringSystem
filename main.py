# Main.py
from flask import Flask, render_template, request, jsonify
import re
from collections import defaultdict

app = Flask(__name__, template_folder='templates')


@app.route('/')
def home_page():
    return render_template('index.html')


@app.route('/refactoring')
def refactoring_page():
    return render_template('refactoring_options.html')


# Route to detect long method
@app.route('/detect_long_method', methods=['POST'])
def detect_long_method():
    file = request.files['codeFile']
    if file:
        content = file.read().decode('utf-8')
        long_methods = long_method(content)
        result = ""
        for function, lines in long_methods.items():
            if lines > 15:  # 15 is the threshold, so more than 15 is considered long.
                result += f"\nThe {function} function is a Long Function. It contains {lines} lines of code.\n"
        return result if result else "No Long Method Detected."
    return "No file uploaded."


@app.route('/detect_long_parameter', methods=['POST'])
def detect_long_parameter():
    file = request.files['codeFile']
    if file:
        content = file.read().decode('utf-8')
        long_methods = long_parameter(content)
        if long_methods:
            result = "The following methods have long parameter lists:\n"
            for method, param_count in long_methods:
                result += f"{method}: {param_count} parameters\n"
            return result
        else:
            return "No methods have long parameter lists."
    return "No file uploaded."


# Function to detect long method
def long_method(content):
    functions = {}
    lines = content.split('\n')
    current_function = None
    for line in lines:
        if line.strip() == '':  # Skip blank lines
            continue
        if current_function:
            if line.strip().startswith('}'):  # Function ends
                current_function = None
            else:
                functions[current_function] += 1
        elif any(line.strip().startswith(kw) for kw in
                 ['void', 'int', 'float', 'double', 'char', 'bool']):
            if '(' in line and ')' in line:
                function_name = line.split('(')[0].split()[-1]
                current_function = function_name
                functions[current_function] = 1
    return functions


# Function to detect long parameter
def long_parameter(content):
    pattern = r'(\w+\s+\w+)\s*\(([^)]*)\)'
    matches = re.findall(pattern, content)
    long_methods = []
    for match in matches:
        function_name, parameters = match
        param_count = len([param for param in parameters.split(',') if param])
        if param_count > 3:
            long_methods.append((function_name, param_count))
    return long_methods


# Work in Progress
def jaccard_similarity(set1, set2):
    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))
    return intersection / union if union else 0


def extract_functions_from_code(code_content):
    function_pattern = re.compile(r'\b\w+\s+(\w+)\s*\((.*?)\)\s*\{([\s\S]*?)\}', re.MULTILINE)
    return function_pattern.findall(code_content)


def normalize_code(code):
    # Normalize variable names and literals for better structural comparison
    code = re.sub(r'\b(int|float|double|char|void|bool)\b', 'type', code)  # Normalize types
    code = re.sub(r'\bfor\b', 'loop', code)  # Normalize loops
    code = re.sub(r'".*?"', '"literal"', code)  # Normalize string literals
    code = re.sub(r'\b\d+\b', 'number', code)  # Normalize numbers
    return code


def tokenize_function_code(function_code):
    function_code = normalize_code(function_code)  # Normalize the code before tokenizing
    return set(re.findall(r'\b\w+\b', function_code))


def duplicate_code(functions):
    duplicate_scores = defaultdict(list)
    for i, (func1_name, func1_params, func1_body) in enumerate(functions):
        tokens1 = tokenize_function_code(func1_name + ' ' + func1_params + ' ' + func1_body)
        for j, (func2_name, func2_params, func2_body) in enumerate(functions):
            if i != j:
                tokens2 = tokenize_function_code(func2_name + ' ' + func2_params + ' ' + func2_body)
                score = jaccard_similarity(tokens1, tokens2)
                if score >= 0.75:
                    rounded_score = round(score, 2)
                    duplicate_scores[f"{func1_name}({func1_params})"].append((f"{func2_name}({func2_params})", rounded_score))

    return duplicate_scores


@app.route('/detect_duplicate_code', methods=['POST'])
def detect_duplicate_code():
    file = request.files.get('codeFile')
    if file:
        content = file.read().decode('utf-8')
        functions = extract_functions_from_code(content)
        duplicate_scores = duplicate_code(functions)
        if duplicate_scores:
            results = {func: duplicates for func, duplicates in duplicate_scores.items()}
            return jsonify(results)
        return jsonify({"message": "No duplicate code detected."})
    return jsonify({"error": "No file uploaded."})


if __name__ == "__main__":
    app.run(debug=True)
