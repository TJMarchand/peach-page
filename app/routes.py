from flask import Blueprint, render_template, request, redirect, session, url_for
from .logic import load_messages, save_message, delete_message, save_user, verify_user, load_users

main = Blueprint("main", __name__)

# Decorator connects index function to webpage with route "/". index is called whenever we are at "/" and request is "GET" or "POST".
@main.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        if "username" not in session:
            return redirect(url_for("main.login"))
        
        action = request.form.get("action")

        if action == "post":
            name = session["username"]
            content = request.form.get("content")
            save_message(name, content)
        
        elif action == "delete":
            message_id = int(request.form.get("message_id"))
            delete_message(message_id)

        return redirect(url_for("main.index"))  # Prevent re-posting on refresh
    
    # if it's anything else than "POST" (i.e. "GET").
    messages = load_messages()
    users = load_users()
    user = session.get("username")
    if user:
        admin = users[user]['admin']
    else:
        admin = None
    # Have to return to send things back to browser. It is what Flask sends to browser.
    return render_template("index.html", messages=messages, user=user, admin=admin)

@main.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if save_user(username, password):
            return redirect(url_for("main.login"))
        else:
            return render_template("register.html", user_exist=True, prev_username=username)
    # If request.method == "GET", we didn't return yet. So we want simply want to render the template.
    return render_template("register.html")

@main.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if verify_user(username, password):
            session["username"] = username
            return redirect(url_for("main.index"))
        else:
            return render_template("login.html", non_exist=True, prev_username=username)
        
    return render_template("login.html")

@main.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("main.index"))

@main.route("/userlist", methods=["GET"])
def userlist():
    users = load_users().keys()
    return render_template("userlist.html", users=users)


"""
main is an instance of the class Blueprint.
Inside this instance is stored essentially a list of routes (like "/") with corresponding method and function (like "GET" and index())

main.route is a method which takes as arguments a path ("/"), and a list (["GET", "POST"]). It returns a function.
This function is used as decorator function, as @main.route(...).

The decorator function is essentially equal to setting index=decorator(index).
In our case the decorator function essentially just stores the function passed to it in the list of the main instance.
It then simply returns the original function so that the original function is unaffected.
"""