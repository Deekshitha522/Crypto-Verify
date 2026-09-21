import os
import sqlite3
import hashlib
import qrcode
import socket
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import landscape, A4
from reportlab.lib.colors import HexColor, Color
from reportlab.lib.utils import ImageReader
import qrcode
import os

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    send_from_directory
)

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

from reportlab.lib.colors import HexColor
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Image
)
from reportlab.lib.styles import getSampleStyleSheet


# ---------------------------------------
# Flask App
# ---------------------------------------

app = Flask(__name__)
app.secret_key = "cryptoverify_secret_key_2026"


# ---------------------------------------
# Get Local IP (for QR Code)
# ---------------------------------------

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"


# ---------------------------------------
# PDF Generator
# ---------------------------------------

def create_certificate_pdf(
    cid,
    name,
    usn,
    course,
    cgpa,
    date,
    hash_value,
    verify_url
):
    os.makedirs("generated", exist_ok=True)

    # Generate QR Code
    qr = qrcode.make(verify_url)
    qr_path = f"generated/{cid}_qr.png"
    qr.save(qr_path)

    pdf_path = f"generated/{cid}.pdf"

    width, height = landscape(A4)
    c = canvas.Canvas(pdf_path, pagesize=landscape(A4))

    # Theme Colors
    blue = HexColor("#123C8C")
    gold = HexColor("#D4AF37")
    light_gold = HexColor("#F7DC6F")

    # ======================================================
    # Background
    # ======================================================
    c.setFillColor(HexColor("#FCFCFC"))
    c.rect(0, 0, width, height, fill=1)

    # ======================================================
    # Decorative Double Border
    # ======================================================
    c.setStrokeColor(blue)
    c.setLineWidth(5)
    c.rect(18, 18, width - 36, height - 36)

    c.setLineWidth(1.5)
    c.rect(30, 30, width - 60, height - 60)

    # Corner Decorations
    corners = [
        (32, 32),
        (width - 32, 32),
        (32, height - 32),
        (width - 32, height - 32)
    ]

    for x, y in corners:
        c.circle(x, y, 14)
        c.circle(x, y, 9)
        c.line(x - 14, y, x + 14, y)
        c.line(x, y - 14, x, y + 14)

    # ======================================================
    # Watermark
    # ======================================================
    c.saveState()
    c.translate(width / 2, height / 2)
    c.rotate(25)

    c.setFillColor(Color(0.80, 0.84, 0.95, alpha=0.08))
    c.setFont("Helvetica-Bold", 78)
    c.drawCentredString(0, 0, "DIGITAL CERTIFICATE")

    c.restoreState()

    # ======================================================
    # Header
    # ======================================================
    c.setFillColor(blue)

    c.setFont("Times-Bold", 28)
    c.drawCentredString(width / 2, height - 55, "DIGITAL CERTIFICATE")

    c.setFont("Helvetica", 12)
    c.drawCentredString(width / 2, height - 82, "Secure Document Verification System")
    c.drawCentredString(width / 2, height - 100, "Powered by SHA-256 Hashing and RSA Digital Signatures")

    # Decorative Line
    c.setStrokeColor(gold)
    c.setLineWidth(1)
    c.line(180, height - 118, width - 180, height - 118)

    # ======================================================
    # Certificate Title
    # ======================================================
    c.setFillColor(blue)
    c.setFont("Times-Bold", 34)
    c.drawCentredString(width / 2, height - 165, "Certificate of Achievement")

    # ======================================================
    # Body
    # ======================================================
    c.setFont("Times-Italic", 18)
    c.drawCentredString(width / 2, height - 205, "This certificate is proudly presented to")

    c.setFont("Times-BoldItalic", 30)
    c.drawCentredString(width / 2, height - 242, name)

    c.setFont("Times-Italic", 16)
    c.drawCentredString(width / 2, height - 272, "for successfully completing the specified academic requirements.")

    c.setFont("Times-Bold", 20)
    c.drawCentredString(width / 2, height - 302, course)

    # ======================================================
    # Student Details
    # ======================================================
    start_y = height - 350

    c.setFillColor(blue)
    c.setFont("Helvetica-Bold", 13)

    labels = [
        ("USN", usn),
        ("CGPA", cgpa),
        ("Issue Date", date)
    ]

    y = start_y

    for label, value in labels:
        c.drawString(235, y, label)
        c.drawString(315, y, ":")

        c.setFont("Helvetica", 13)
        c.drawString(330, y, str(value))

        c.setFont("Helvetica-Bold", 13)
        y -= 28

    # ======================================================
    # Gold Official Seal
    # ======================================================
    seal_x = width / 2
    seal_y = 90

    c.setFillColor(gold)
    c.circle(seal_x, seal_y, 42, fill=1)

    c.setFillColor(light_gold)
    c.circle(seal_x, seal_y, 30, fill=1)

    c.setFillColor(HexColor("#7A5C00"))

    c.setFont("Helvetica-Bold", 12)
    c.drawCentredString(seal_x, seal_y + 5, "CERTIFIED")

    c.setFont("Helvetica", 8)
    c.drawCentredString(seal_x, seal_y - 10, "OFFICIAL SEAL")

    # Ribbon
    c.setFillColor(gold)
    c.wedge(seal_x - 18, seal_y - 50, seal_x, seal_y - 15, 220, 320, fill=1)
    c.wedge(seal_x, seal_y - 50, seal_x + 18, seal_y - 15, 220, 320, fill=1)

    # ======================================================
    # Signature Section
    # ======================================================
    c.setStrokeColor(blue)
    c.line(width - 260, 82, width - 135, 82)

    c.setFillColor(blue)

    c.setFont("Times-Italic", 18)
    c.drawString(width - 245, 95, "Authorized Signatory")

    c.setFont("Helvetica", 11)
    c.drawString(width - 220, 62, "Digital Issuing Authority")

    # ======================================================
    # Security Information
    # ======================================================
    c.setFillColor(blue)

    c.setFont("Helvetica-Bold", 9)
    c.drawString(55, 105, "Certificate ID")
    c.drawString(55, 82, "SHA-256 Hash")
    c.drawString(55, 34, "Digital Signature")

    c.setFont("Helvetica", 8)
    c.drawString(145, 105, cid)

    hash_lines = [hash_value[i:i + 34] for i in range(0, len(hash_value), 34)]

    yy = 82
    for line in hash_lines[:2]:
        c.drawString(145, yy, line)
        yy -= 10

    c.drawString(145, 34, "RSA Signed Successfully")

    # ======================================================
    # QR Code
    # ======================================================
    qr_img = ImageReader(qr_path)

    c.drawImage(qr_img, width - 115, 24, width=76, height=76)

    c.setFont("Helvetica", 8)
    c.drawCentredString(width - 77, 12, "Scan to Verify")

    # ======================================================
    # Footer
    # ======================================================
    c.setStrokeColor(blue)
    c.line(170, 20, width - 170, 20)

    c.setFillColor(blue)
    c.setFont("Helvetica-Bold", 10)
    c.drawCentredString(width / 2, 8, "Secure • Authentic • Digitally Verified")

    c.save()

    return pdf_path


# ---------------------------------------
# LOGIN
# ---------------------------------------

@app.route("/", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("certificates.db")
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username, password)
        )

        user = cursor.fetchone()
        conn.close()

        if user:
            session["user"] = user["full_name"]
            session["username"] = user["username"]
            return redirect(url_for("dashboard"))

        return render_template(
            "login.html",
            error="Invalid Username or Password"
        )

    return render_template("login.html")


# ---------------------------------------
# REGISTER
# ---------------------------------------

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        full_name = request.form["full_name"]
        username = request.form["username"]
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]
        security_answer = request.form["security_answer"]

        if password != confirm_password:

            return render_template(
                "register.html",
                error="Passwords do not match."
            )

        conn = sqlite3.connect("certificates.db")
        cursor = conn.cursor()

        try:

            cursor.execute("""
            INSERT INTO users
            (full_name, username, password, security_answer)
            VALUES(?,?,?,?)
            """, (
                full_name,
                username,
                password,
                security_answer
            ))

            conn.commit()
            conn.close()

            return redirect(url_for("login"))

        except sqlite3.IntegrityError:

            conn.close()

            return render_template(
                "register.html",
                error="Username already exists."
            )

    return render_template("register.html")


# ---------------------------------------
# RESET PASSWORD
# ---------------------------------------

@app.route("/reset_password", methods=["GET", "POST"])
def reset_password():

    if request.method == "POST":

        username = request.form["username"]
        security_answer = request.form["security_answer"]
        new_password = request.form["new_password"]

        conn = sqlite3.connect("certificates.db")
        cursor = conn.cursor()

        cursor.execute("""
        SELECT * FROM users
        WHERE username=? AND security_answer=?
        """, (
            username,
            security_answer
        ))

        user = cursor.fetchone()

        if user:

            cursor.execute("""
            UPDATE users
            SET password=?
            WHERE username=?
            """, (
                new_password,
                username
            ))

            conn.commit()
            conn.close()

            return redirect(url_for("login"))

        conn.close()

        return render_template(
            "reset_password.html",
            error="Incorrect Username or Security Answer."
        )

    return render_template("reset_password.html")


# ---------------------------------------
# DASHBOARD
# ---------------------------------------

@app.route("/dashboard")
def dashboard():

    if "user" not in session:
        return redirect(url_for("login"))

    conn = sqlite3.connect("certificates.db")
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM certificates")
    issued = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM certificates WHERE status='Valid'"
    )
    verified = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM certificates WHERE status='Revoked'"
    )
    revoked = cursor.fetchone()[0]

    conn.close()

    return render_template(
        "dashboard.html",
        username=session["user"],
        issued=issued,
        verified=verified,
        revoked=revoked
    )


# ---------------------------------------
# CREATE PAGE
# ---------------------------------------

@app.route("/create")
def create_certificate():

    if "user" not in session:
        return redirect(url_for("login"))

    return render_template("create_certificate.html")


# ---------------------------------------
# GENERATE CERTIFICATE
# ---------------------------------------

@app.route("/generate", methods=["POST"])
def generate():

    if "user" not in session:
        return redirect(url_for("login"))

    name = request.form["student_name"]
    usn = request.form["usn"]
    course = request.form["course"]
    cgpa = request.form["cgpa"]
    issue_date = request.form["issue_date"]

    conn = sqlite3.connect("certificates.db")
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM certificates")
    count = cursor.fetchone()[0] + 1

    certificate_id = f"CV2026{count:04d}"

    data = name + usn + course + cgpa + issue_date

    certificate_hash = hashlib.sha256(data.encode()).hexdigest()

    with open("keys/private.pem", "rb") as key_file:

        private_key = serialization.load_pem_private_key(
            key_file.read(),
            password=None
        )

    signature = private_key.sign(
        certificate_hash.encode(),
        padding.PKCS1v15(),
        hashes.SHA256()
    )

    ip = get_local_ip()

    verify_url = f"http://{ip}:5000/verify/{certificate_id}"

    pdf_path = create_certificate_pdf(
        certificate_id,
        name,
        usn,
        course,
        cgpa,
        issue_date,
        certificate_hash,
        verify_url
    )

    cursor.execute("""
    INSERT INTO certificates(
        certificate_id,
        student_name,
        usn,
        course,
        cgpa,
        issue_date,
        hash,
        signature,
        pdf_name,
        status
    )
    VALUES(?,?,?,?,?,?,?,?,?,?)
    """, (
        certificate_id,
        name,
        usn,
        course,
        cgpa,
        issue_date,
        certificate_hash,
        signature.hex(),
        os.path.basename(pdf_path),
        "Valid"
    ))

    conn.commit()
    conn.close()

    return render_template(
        "result.html",
        certificate_id=certificate_id,
        student_name=name,
        usn=usn,
        course=course,
        cgpa=cgpa,
        issue_date=issue_date,
        hash=certificate_hash,
        signature=signature.hex()
    )


# ---------------------------------------
# DOWNLOAD PDF
# ---------------------------------------

@app.route("/download/<cid>")
def download(cid):

    return send_from_directory(
        "generated",
        f"{cid}.pdf",
        as_attachment=True
    )


# ---------------------------------------
# ISSUED CERTIFICATES
# ---------------------------------------

@app.route("/issued")
def issued():

    if "user" not in session:
        return redirect(url_for("login"))

    conn = sqlite3.connect("certificates.db")
    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()

    cursor.execute("""
    SELECT * FROM certificates
    ORDER BY id DESC
    """)

    certificates = cursor.fetchall()

    conn.close()

    return render_template(
        "issued.html",
        certificates=certificates
    )


# ---------------------------------------
# VERIFY SEARCH PAGE
# ---------------------------------------

@app.route("/verify", methods=["GET", "POST"])
def verify_search():

    if request.method == "POST":

        cid = request.form["certificate_id"]

        return redirect(url_for("verify", cid=cid))

    return render_template("verify_search.html")


# ---------------------------------------
# VERIFY CERTIFICATE
# ---------------------------------------

@app.route("/verify/<cid>")
def verify(cid):

    conn = sqlite3.connect("certificates.db")
    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM certificates WHERE certificate_id=?",
        (cid,)
    )

    certificate = cursor.fetchone()

    conn.close()

    if certificate is None:
        return "Certificate Not Found"

    data = (
        certificate["student_name"] +
        certificate["usn"] +
        certificate["course"] +
        certificate["cgpa"] +
        certificate["issue_date"]
    )

    current_hash = hashlib.sha256(data.encode()).hexdigest()

    if current_hash != certificate["hash"]:
        status = "Tampered"
    else:
        status = certificate["status"]

    return render_template(
        "verify.html",
        certificate=certificate,
        status=status
    )


# ---------------------------------------
# REVOKE
# ---------------------------------------

@app.route("/revoke/<cid>")
def revoke(cid):

    conn = sqlite3.connect("certificates.db")
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE certificates SET status='Revoked' WHERE certificate_id=?",
        (cid,)
    )

    conn.commit()
    conn.close()

    return redirect(url_for("issued"))


# ---------------------------------------
# LOGOUT
# ---------------------------------------

@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("login"))


# ---------------------------------------
# RUN APP
# ---------------------------------------

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )