from flask import Blueprint, render_template, request
from .logic import calculate_square

main = Blueprint('main', __name__)

@main.route('/', methods=['GET', 'POST'])
def index():
    result = None
    if request.method == 'POST':
        try:
            number = float(request.form['number'])
            result = calculate_square(number)
        except ValueError:
            result = 'Invalid input'
    return render_template('index.html', result=result)
