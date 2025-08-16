from flask import Flask, render_template, request, redirect, url_for, session, send_file, flash
from werkzeug.utils import secure_filename
import os
import tempfile
from supabase import create_client, Client

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "supersecret")

# Config from environment variables
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
PASSWORD = os.environ.get("APP_PASSWORD", "Wahab@2024")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        password = request.form.get("password")
        if password == PASSWORD:
            session["logged_in"] = True
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid password", "danger")
    return render_template("login.html")

@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if not session.get("logged_in"):
        return redirect(url_for("login"))

    if request.method == "POST":
        if "file" not in request.files:
            flash("No file uploaded", "danger")
            return redirect(request.url)

        file = request.files["file"]
        if file.filename == "":
            flash("No file selected", "danger")
            return redirect(request.url)

        filename = secure_filename(file.filename)
        supabase.storage.from_("files").upload(filename, file)

        flash("File uploaded successfully", "success")
        return redirect(url_for("dashboard"))

    # List files
    files = supabase.storage.from_("files").list()
    return render_template("dashboard.html", files=files)

@app.route("/download/<filename>")
def download(filename):
    if not session.get("logged_in"):
        return redirect(url_for("login"))

    # Download file to temp dir
    res = supabase.storage.from_("files").download(filename)
    temp_path = os.path.join(tempfile.gettempdir(), filename)
    with open(temp_path, "wb") as f:
        f.write(res)

    return send_file(temp_path, as_attachment=True)

@app.route("/delete/<filename>")
def delete(filename):
    if not session.get("logged_in"):
        return redirect(url_for("login"))

    supabase.storage.from_("files").remove(filename)
    flash("File deleted successfully", "success")
    return redirect(url_for("dashboard"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
