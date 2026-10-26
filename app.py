
from flask import Flask, request, render_template_string, send_file, redirect, url_for, session
from minio import Minio
from datetime import datetime
from io import BytesIO
from markupsafe import escape
import os

app = Flask(__name__)

FLASK_SECRET_KEY = os.environ.get("FLASK_SECRET_KEY")
LOGIN_USERNAME = os.environ.get("LOGIN_USERNAME")
LOGIN_PASSWORD = os.environ.get("LOGIN_PASSWORD")

if not FLASK_SECRET_KEY or not LOGIN_USERNAME or not LOGIN_PASSWORD:
    raise RuntimeError("Set FLASK_SECRET_KEY, LOGIN_USERNAME, and LOGIN_PASSWORD.")

app.secret_key = FLASK_SECRET_KEY
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "cloud-minio:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "")

client = Minio(
    MINIO_ENDPOINT,
    access_key=MINIO_ACCESS_KEY,
    secret_key=MINIO_SECRET_KEY,
    secure=False
)
BUCKET = "student-files"

PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>CloudVault | File Storage</title>
<style>
*{box-sizing:border-box}
body{margin:0;background:#f3f6fc;color:#17233d;font-family:Arial,sans-serif}
header{background:linear-gradient(120deg,#155eef,#3978f6);color:white;padding:22px 6%;display:flex;justify-content:space-between;align-items:center}
.brand{font-size:25px;font-weight:700;letter-spacing:.2px}
.account{font-size:14px;background:#ffffff22;padding:10px 14px;border-radius:10px}
main{max-width:1100px;margin:32px auto;padding:0 22px}
.hero{background:linear-gradient(120deg,#e5efff,#fff);border:1px solid #d8e5ff;border-radius:18px;padding:30px;margin-bottom:24px}
.eyebrow{color:#2163db;font-size:12px;font-weight:bold;text-transform:uppercase;letter-spacing:1.5px}
h1{font-size:30px;margin:12px 0}
.hero p{color:#53627b;line-height:1.6;margin-bottom:0}
.stats{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin:22px 0}
.stat,.panel{background:white;border:1px solid #e2e9f4;border-radius:15px;padding:22px;box-shadow:0 5px 18px #18345b08}
.stat small{color:#68768d}
.stat strong{display:block;font-size:26px;margin-top:10px}
.panel{margin-bottom:22px}
h2{font-size:19px;margin:0 0 8px}
.sub{color:#68768d;font-size:14px;margin:0 0 20px}
input[type=file]{width:100%;padding:14px;border:1px dashed #b9c9e4;border-radius:10px;background:#f9fbff;margin-bottom:14px}
button,.download{background:#2163e8;color:white;border:0;border-radius:9px;padding:12px 18px;font-weight:bold;cursor:pointer;text-decoration:none;display:inline-block}
button:hover,.download:hover{background:#174dbb}
.notice{padding:13px 16px;border-radius:10px;background:#e5f8ed;color:#146c3a;margin-bottom:20px}
.tablewrap{overflow-x:auto}
table{width:100%;border-collapse:collapse;text-align:left}
th{background:#f5f8fd;color:#63718a;font-size:12px;text-transform:uppercase;letter-spacing:.5px}
th,td{padding:15px 12px;border-bottom:1px solid #edf1f7}
td{font-size:14px}
.filename{font-weight:bold;overflow-wrap:anywhere}
.empty{text-align:center;padding:32px;color:#68768d}
footer{text-align:center;color:#7b879b;font-size:13px;padding:25px}
@media(max-width:650px){header{padding:18px 5%}.brand{font-size:20px}main{margin:20px auto;padding:0 14px}.stats{grid-template-columns:1fr}h1{font-size:25px}.hero{padding:22px}.panel{padding:16px}}
</style>
</head>
<body>

<header>
  <div class="brand">☁ CloudVault</div>
  <div class="account">
    <span>● You're securely logged in</span>
    <form action="/logout" method="POST" style="display:inline;margin-left:12px">
      <button type="submit" style="padding:8px 14px;margin:0">Logout</button>
    </form>
  </div>
</header>

<main>
  <section class="hero">
    <div class="eyebrow">Secure Cloud File Storage</div>
    <h1>Your files. One secure space.</h1>
    <p>Upload, store and download your files through a Docker-powered web application with MinIO object storage and restricted application permissions.</p>
  </section>

  {% if message %}
  <div class="notice">{{ message }}</div>
  {% endif %}

  <section class="stats">
    <div class="stat"><small>Storage service</small><strong>● Online</strong></div>
    <div class="stat"><small>Files stored</small><strong>{{ count }}</strong></div>
    <div class="stat"><small>Upload limit</small><strong>16 MB</strong></div>
  </section>

  <section class="panel">
    <h2>↑ &nbsp; Upload a file</h2>
    <p class="sub">Choose a file from your device to store it in your cloud bucket.</p>
    <form action="/upload" method="POST" enctype="multipart/form-data">
      <input type="file" name="file" required>
      <button type="submit">↑ &nbsp; Upload file</button>
    </form>
  </section>

  <section class="panel">
    <h2>▤ &nbsp; Your stored files</h2>
    <p class="sub">Files saved in the MinIO <b>student-files</b> bucket.</p>
    {% if files %}
    <div class="tablewrap">
    <table>
      <thead><tr><th>File name</th><th>Size</th><th>Action</th></tr></thead>
      <tbody>
      {% for file in files %}
      <tr>
        <td class="filename">▧ &nbsp; {{ file.name }}</td>
        <td>{{ file.size }}</td>
        
<td>
  <a class="download"
     href="{{ url_for('download', filename=file.name) }}">↓ Download</a>

  <form action="{{ url_for('delete_file', filename=file.name) }}"
        method="POST"
        style="display:inline"
        onsubmit="return confirm('Are you sure you want to delete this file? This cannot be undone.');">
    <button type="submit"
            style="width:auto;margin:6px 0 0 6px;padding:12px 18px;background:#dc3545;">
      Delete
    </button>
  </form>
</td>

      </tr>
      {% endfor %}
      </tbody>
    </table>
    </div>
    {% else %}
    <div class="empty">No files yet. Upload your first file above.</div>
    {% endif %}
  </section>
</main>

<footer>CloudVault · Secure Cloud File Storage · Powered by Flask, MinIO & Docker</footer>

</body>
</html>
"""

def format_size(size):
    if size < 1024:
        return f"{size} B"
    if size < 1024 * 1024:
        return f"{size / 1024:.1f} KB"
    return f"{size / (1024 * 1024):.1f} MB"


import hmac
from flask import session

@app.route("/login", methods=["GET", "POST"])

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")

        if (
            hmac.compare_digest(username, LOGIN_USERNAME)
            and hmac.compare_digest(password, LOGIN_PASSWORD)
        ):
            session["logged_in"] = True
            return redirect(url_for("home"))

        return render_template_string(LOGIN_PAGE, error="Invalid username or password."), 401

    return render_template_string(LOGIN_PAGE, error="")


LOGIN_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>CloudVault | Login</title>
<style>
* { box-sizing: border-box; }
body {
    margin: 0;
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 22px;
    font-family: Arial, sans-serif;
    background: linear-gradient(135deg, #1049bd, #3978f6, #8bb8ff);
    color: #17233d;
}
.login-card {
    width: 100%;
    max-width: 420px;
    padding: 38px;
    border-radius: 22px;
    background: white;
    box-shadow: 0 22px 60px #092b7040;
}
.brand {
    text-align: center;
    color: #2163e8;
    font-size: 30px;
    font-weight: bold;
    margin-bottom: 10px;
}
.subtitle {
    text-align: center;
    color: #68768d;
    font-size: 14px;
    line-height: 1.5;
    margin-bottom: 30px;
}
h1 {
    text-align: center;
    font-size: 24px;
    margin-bottom: 8px;
}
label {
    display: block;
    font-size: 13px;
    font-weight: bold;
    margin: 18px 0 8px;
}
input {
    width: 100%;
    padding: 14px;
    border: 1px solid #d5deed;
    border-radius: 10px;
    font-size: 15px;
    outline: none;
}
input:focus {
    border-color: #2163e8;
    box-shadow: 0 0 0 3px #2163e81c;
}
button {
    width: 100%;
    margin-top: 24px;
    padding: 14px;
    border: none;
    border-radius: 10px;
    background: #2163e8;
    color: white;
    font-size: 15px;
    font-weight: bold;
    cursor: pointer;
}
button:hover { background: #174dbb; }
.error {
    padding: 12px;
    background: #fff0f0;
    color: #b42318;
    border-radius: 8px;
    font-size: 13px;
}
.footer {
    margin-top: 24px;
    text-align: center;
    color: #8290a6;
    font-size: 12px;
}
</style>
</head>
<body>
<div class="login-card">
    <div class="brand">&#9729; CloudVault</div>
    <div class="subtitle">Your files. One secure space.<br>
    SECURE CLOUD FILE STORAGE</div>
    <h1>Welcome back</h1>
    <p class="subtitle">Sign in to access your cloud workspace.</p>

    {% if error %}
    <div class="error">{{ error }}</div>
    {% endif %}

    <form method="post">
        <label for="username">Username</label>
        
<input id="username" name="username"
       placeholder="Enter your username"
       autocomplete="off" required>


        <label for="password">Password</label>
        


<div style="position:relative;width:100%;">
  <input
    id="password"
    name="password"
    type="password"
    placeholder="Enter your password"
    autocomplete="off"
    required
    style="display:block;width:100%;box-sizing:border-box;padding:14px 50px 14px 14px;position:relative;z-index:5;pointer-events:auto;user-select:text;"
  >

  <button
    type="button"
    id="togglePassword"
    aria-label="Show password"
    onclick="togglePasswordVisibility()"
    style="position:absolute;right:8px;top:50%;transform:translateY(-50%);z-index:2;background:transparent;color:#64748b;border:none;padding:8px;cursor:pointer;margin:0;line-height:1;"
  >👁</button>
</div>




        <button type="submit">Sign in to CloudVault &rarr;</button>
    </form>

    <div class="footer">CloudVault &middot; Secure File Storage</div>
</div>


<script>
function togglePasswordVisibility() {
  const password = document.getElementById("password");
  const button = document.getElementById("togglePassword");

  if (password.type === "password") {
    password.type = "text";
    button.textContent = "⊘";
    button.setAttribute("aria-label", "Hide password");
  } else {
    password.type = "password";
    button.textContent = "👁";
    button.setAttribute("aria-label", "Show password");
  }
}
</script>

</body>
</html>
"""

@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.before_request
def require_login():
    if request.endpoint in ("login",):
        return None
    if not session.get("logged_in"):
        return redirect(url_for("login"))

@app.route("/")
def home():
    objects = list(client.list_objects(BUCKET))
    files = [
        {"name": obj.object_name, "size": format_size(obj.size or 0)}
        for obj in objects
    ]
    return render_template_string(
        PAGE, files=files, count=len(files), message=request.args.get("message", "")
    )

@app.route("/upload", methods=["POST"])
def upload():
    file = request.files.get("file")
    if not file or not file.filename:
        return redirect(url_for("home", message="Please select a file."))

    filename = os.path.basename(file.filename).replace("\\\\", "")
    if not filename or filename in (".", ".."):
        return redirect(url_for("home", message="Invalid file name."))

    data = file.read()
    client.put_object(
        BUCKET, filename, BytesIO(data), length=len(data),
        content_type=file.mimetype or "application/octet-stream"
    )
    return redirect(url_for("home", message="Upload successful! Your file is stored."))


@app.route("/download/<path:filename>")
def download(filename):
    filename = os.path.basename(filename)
    response = client.get_object(BUCKET, filename)

    try:
        data = response.read()

        import mimetypes
        content_type, _ = mimetypes.guess_type(filename)

        return send_file(
            BytesIO(data),
            mimetype=content_type or "application/octet-stream",
            download_name=filename,
            as_attachment=True
        )
    finally:
        response.close()
        response.release_conn()

@app.route("/delete/<path:filename>", methods=["POST"])
def delete_file(filename):
    if not session.get("logged_in"):
        return redirect(url_for("login"))

    filename = os.path.basename(filename)

    try:
        client.remove_object(BUCKET, filename)
        return redirect(url_for("home", message="File deleted successfully."))
    except Exception:
        app.logger.exception("CloudVault file deletion failed")
        return redirect(url_for("home", message="Could not delete the file. Check server logs."))



    	
@app.errorhandler(413)
def too_large(error):
    return "File too large. The maximum upload size is 16 MB.", 413

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
