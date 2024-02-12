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
        elif any(line.strip().startswith(kw) for kw in ['void', 'int', 'float', 'double', 'char', 'bool']):  # Simplified detection
            if '(' in line and ')' in line:  # Found a function start
                function_name = line.split('(')[0].split()[-1]
                current_function = function_name
                functions[current_function] = 1  # Start counting lines for this function
    return functions


# Function to detect long parameter
def long_parameter(content):
    # Regex pattern to match function definitions
    pattern = r'(\w+\s+\w+)\s*\(([^)]*)\)'
    matches = re.findall(pattern, content)
    long_methods = []

    for match in matches:
        # Extract the function name and parameters
        function_name, parameters = match
        # Split parameters on comma, filter out empty strings and count them
        param_count = len([param for param in parameters.split(',') if param])
        # Check if the parameter count exceeds the threshold
        if param_count > 3:
            long_methods.append((function_name, param_count))

    return long_methods


if __name__ == "__main__":
    app.run(debug=True)
