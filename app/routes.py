from flask import Blueprint, render_template, request, redirect, url_for
from .logic import load_messages, save_message

main = Blueprint("main", __name__)

@main.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        name = request.form.get("name")
        content = request.form.get("content")
        if name and content:
            save_message(name, content)
            return redirect(url_for("main.index"))  # Prevent re-posting on refresh
    messages = load_messages()
    return render_template("index.html", messages=messages)
