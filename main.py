# Main.py
from flask import Flask, render_template, request
import re

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
        for function, lines in long_methods:
            if lines > 15:
                result += f"\nThe {function} function is a Long Function. It contains {lines} lines of code.\n"
        return result
    return "No file uploaded."


# Route to detect long parameter
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
    code_lines = content.split('\n')
    braces = 0
    functions = []
    current_function = None
    current_function_lines = 0

    for line in code_lines:
        line = line.strip()
        if not line:
            continue
        for char in line:
            if char == '{':
                braces += 1
            elif char == '}':
                braces -= 1
        if (line.startswith('int') or line.startswith('void') or line.startswith('bool') or line.startswith(
                'char') or line.startswith('wchar_t') or line.startswith('double') or line.startswith(
            'float')) and (line.endswith(')') or line.endswith('{')):
            if current_function is not None:
                functions.append((current_function, current_function_lines))
            current_function = line.split()[1].split('(')[0]
            current_function_lines = 1
        elif current_function is not None:
            current_function_lines += 1

    if current_function is not None:
        functions.append((current_function, current_function_lines))

    if braces == 0:
        return functions


# Function to detect long parameter
def long_parameter(content):
    method_params = re.findall(r'\b\w+\b', content)
    long_methods = []
    method_name = None
    params = []
    for param in method_params:
        if param.endswith('('):
            if method_name and len(params) > 3:
                long_methods.append((method_name, params))
            method_name = param[:-1]
            params = []
        elif param.endswith(')'):
            params.append(param[:-1])
        elif param.endswith(','):
            params.append(param[:-1])
    if method_name and len(params) > 3:
        long_methods.append((method_name, params))
    return long_methods


def jaccard_similarity(method1, method2):
    method1 = set(method1)
    method2 = set(method2)
    intersection = len(method1.intersection(method2))
    union = len(method1.union(method2))
    result = intersection / union
    return result


def extract_method_content(content, method_name):
    pattern = fr'{method_name}\s*\([^)]*\)\s*\{{[\s\S]*?}}'
    match = re.search(pattern, content)
    if match:
        return match.group()
    return None


# Function to detect duplicate code
def detect_duplicate_code(content, method_names):
    duplicate_methods = []

    # Iterate through method names
    for i in range(len(method_names)):
        func1 = method_names[i]
        method_content1 = extract_method_content(content, func1)
        if method_content1:
            for j in range(i + 1, len(method_names)):
                func2 = method_names[j]
                method_content2 = extract_method_content(content, func2)
                if method_content2:
                    jaccard_index = jaccard_similarity(method_content1, method_content2)
                    if jaccard_index > 0.75:
                        duplicate_methods.append((func1, func2, jaccard_index))

    return duplicate_methods


# Route to detect duplicate code
@app.route('/detect_duplicate_code', methods=['POST'])
def detect_duplicate_code_route():
    file = request.files['codeFile']
    if file:
        content = file.read().decode('utf-8')
        # Fetch method names from the content
        method_names = re.findall(r'\b\w+\b\s+\b\w+\b\([^)]*\)\s*{', content)
        # Detect duplicate methods
        duplicate_methods = detect_duplicate_code(content, method_names)
        # If duplicate methods found, return the result
        if duplicate_methods:
            result = "Duplicated Code Detected:\n"
            for func1, func2, jaccard_index in duplicate_methods:
                result += f"{func1} and {func2} are duplicated. Jaccard Similarity: {jaccard_index}\n"
            return result
        else:
            return "No duplicated code detected."

    return "No file uploaded."


if __name__ == "__main__":
    app.run(debug=True)
