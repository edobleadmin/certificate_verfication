from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import qrcode
import os
import uuid
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from io import BytesIO
import base64
from PIL import Image as PILImage, ImageDraw, ImageFont
import io
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///certificates.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.environ.get('UPLOAD_FOLDER', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = int(os.environ.get('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))  # 16MB default

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Database Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

class Certificate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    unique_id = db.Column(db.String(100), unique=True, nullable=False)
    holder_name = db.Column(db.String(200), nullable=False)
    course_name = db.Column(db.String(200), nullable=False)
    issue_date = db.Column(db.DateTime, nullable=False)
    issuer_name = db.Column(db.String(200), nullable=False)
    issuer_logo = db.Column(db.String(500))
    verification_url = db.Column(db.String(500), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_valid = db.Column(db.Boolean, default=True)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def generate_qr_code(data, filename):
    """Generate QR code and save to file"""
    try:
        # Ensure the upload directory exists
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        img_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        img.save(img_path)
        print(f"✅ QR code generated successfully: {img_path}")
        return img_path
    except Exception as e:
        print(f"❌ Error generating QR code: {e}")
        return None

def get_qr_code_path(unique_id):
    """Get the path to a QR code file for a certificate"""
    qr_filename = f"qr_{unique_id}.png"
    qr_path = os.path.join(app.config['UPLOAD_FOLDER'], qr_filename)
    return qr_path if os.path.exists(qr_path) else None

def generate_certificate_pdf(certificate):
    """Generate PDF certificate using JPG template with overlaid text"""
    try:
        # Path to the JPG template
        template_path = os.path.join(app.config['UPLOAD_FOLDER'], 'image_2.jpg')
        
        if not os.path.exists(template_path):
            print(f"❌ Template not found: {template_path}")
            # Fallback to original PDF generation
            return generate_certificate_pdf_fallback(certificate)
        
        # Open the template image
        template_img = PILImage.open(template_path)
        
        # Convert to RGB if necessary
        if template_img.mode != 'RGB':
            template_img = template_img.convert('RGB')
        
        # Create a copy to work with
        certificate_img = template_img.copy()
        draw = ImageDraw.Draw(certificate_img)
        
        # Try to load a font, fallback to default if not available
        try:
            # Try to use a professional font
            title_font = ImageFont.truetype("arial.ttf", 48)
            name_font = ImageFont.truetype("arial.ttf", 36)
            text_font = ImageFont.truetype("arial.ttf", 24)
            small_font = ImageFont.truetype("arial.ttf", 18)
        except:
            # Fallback to default font
            title_font = ImageFont.load_default()
            name_font = ImageFont.load_default()
            text_font = ImageFont.load_default()
            small_font = ImageFont.load_default()
        
        # Get image dimensions
        img_width, img_height = certificate_img.size
        
        # Define colors
        title_color = (44, 62, 80)  # Dark blue
        name_color = (52, 152, 219)  # Blue
        text_color = (52, 73, 94)  # Dark gray
        
        # Calculate positions (you may need to adjust these based on your template)
        center_x = img_width // 2
        
        # Certificate title
        title_text = "Certificate of Internship Completion"
        title_bbox = draw.textbbox((0, 0), title_text, font=title_font)
        title_width = title_bbox[2] - title_bbox[0]
        title_x = center_x - (title_width // 2)
        title_y = img_height * 0.15  # 15% from top
        draw.text((title_x, title_y), title_text, font=title_font, fill=title_color)
        
        # "This is to certify that" text
        certify_text = "This is to certify that"
        certify_bbox = draw.textbbox((0, 0), certify_text, font=text_font)
        certify_width = certify_bbox[2] - certify_bbox[0]
        certify_x = center_x - (certify_width // 2)
        certify_y = img_height * 0.35  # 35% from top
        draw.text((certify_x, certify_y), certify_text, font=text_font, fill=text_color)
        
        # Intern name
        name_text = certificate.holder_name
        name_bbox = draw.textbbox((0, 0), name_text, font=name_font)
        name_width = name_bbox[2] - name_bbox[0]
        name_x = center_x - (name_width // 2)
        name_y = img_height * 0.42  # 42% from top
        draw.text((name_x, name_y), name_text, font=name_font, fill=name_color)
        
        # "has successfully completed the internship program"
        program_text = "has successfully completed the internship program"
        program_bbox = draw.textbbox((0, 0), program_text, font=text_font)
        program_width = program_bbox[2] - program_bbox[0]
        program_x = center_x - (program_width // 2)
        program_y = img_height * 0.52  # 52% from top
        draw.text((program_x, program_y), program_text, font=text_font, fill=text_color)
        
        # Course/Program name
        course_text = certificate.course_name
        course_bbox = draw.textbbox((0, 0), course_text, font=name_font)
        course_width = course_bbox[2] - course_bbox[0]
        course_x = center_x - (course_width // 2)
        course_y = img_height * 0.59  # 59% from top
        draw.text((course_x, course_y), course_text, font=name_font, fill=name_color)
        
        # Issue date
        date_text = f"Issued on: {certificate.issue_date.strftime('%B %d, %Y')}"
        date_bbox = draw.textbbox((0, 0), date_text, font=text_font)
        date_width = date_bbox[2] - date_bbox[0]
        date_x = center_x - (date_width // 2)
        date_y = img_height * 0.70  # 70% from top
        draw.text((date_x, date_y), date_text, font=text_font, fill=text_color)
        
        # Certificate ID
        id_text = f"Certificate ID: {certificate.unique_id}"
        id_bbox = draw.textbbox((0, 0), id_text, font=small_font)
        id_width = id_bbox[2] - id_bbox[0]
        id_x = center_x - (id_width // 2)
        id_y = img_height * 0.78  # 78% from top
        draw.text((id_x, id_y), id_text, font=small_font, fill=text_color)
        
        # Add QR code if it exists
        qr_filename = f"qr_{certificate.unique_id}.png"
        qr_path = get_qr_code_path(certificate.unique_id)
        
        if qr_path and os.path.exists(qr_path):
            try:
                # Open QR code image
                qr_img = PILImage.open(qr_path)
                
                # Resize QR code to appropriate size
                qr_size = min(img_width, img_height) // 8  # 1/8 of the smaller dimension
                qr_img = qr_img.resize((qr_size, qr_size), PILImage.Resampling.LANCZOS)
                
                # Position QR code in bottom right corner
                qr_x = img_width - qr_size - 50  # 50px from right edge
                qr_y = img_height - qr_size - 50  # 50px from bottom edge
                
                # Paste QR code onto certificate
                certificate_img.paste(qr_img, (qr_x, qr_y))
                print(f"✅ QR code added to certificate: {qr_path}")
            except Exception as e:
                print(f"❌ Error adding QR code to certificate: {e}")
        
        # Convert to PDF
        pdf_buffer = BytesIO()
        
        # Save as PDF using reportlab
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Image as RLImage
        
        doc = SimpleDocTemplate(pdf_buffer, pagesize=letter)
        story = []
        
        # Convert PIL image to reportlab image
        img_buffer = BytesIO()
        certificate_img.save(img_buffer, format='JPEG', quality=95)
        img_buffer.seek(0)
        
        # Create reportlab image
        rl_img = RLImage(img_buffer, width=8*inch, height=6*inch, kind='proportional')
        story.append(rl_img)
        
        doc.build(story)
        pdf_buffer.seek(0)
        
        print(f"✅ Certificate generated successfully using JPG template")
        return pdf_buffer
        
    except Exception as e:
        print(f"❌ Error generating certificate with JPG template: {e}")
        # Fallback to original PDF generation
        return generate_certificate_pdf_fallback(certificate)

def generate_certificate_pdf_fallback(certificate):
    """Fallback PDF generation method (original implementation)"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    story = []
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=28,
        spaceAfter=30,
        alignment=1,
        textColor=colors.HexColor('#2c3e50')
    )
    
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Heading2'],
        fontSize=16,
        spaceAfter=20,
        alignment=1,
        textColor=colors.HexColor('#3498db')
    )
    
    # Add Edoble branding and title
    story.append(Paragraph("EDOBLE", title_style))
    story.append(Paragraph("Code with a Purpose - Build smart. Think bold. Impact real.", subtitle_style))
    story.append(Spacer(1, 30))
    
    # Add certificate title
    story.append(Paragraph("Certificate of Internship Completion", title_style))
    story.append(Spacer(1, 20))
    
    # Add certificate details
    story.append(Paragraph(f"<b>This is to certify that</b>", styles['Normal']))
    story.append(Spacer(1, 10))
    story.append(Paragraph(f"<b>{certificate.holder_name}</b>", styles['Heading2']))
    story.append(Spacer(1, 10))
    story.append(Paragraph(f"has successfully completed the internship program", styles['Normal']))
    story.append(Spacer(1, 10))
    story.append(Paragraph(f"<b>{certificate.course_name}</b>", styles['Heading2']))
    story.append(Spacer(1, 20))
    story.append(Paragraph(f"Issued on: {certificate.issue_date.strftime('%B %d, %Y')}", styles['Normal']))
    story.append(Spacer(1, 10))
    story.append(Paragraph(f"Issuer: {certificate.issuer_name}", styles['Normal']))
    story.append(Spacer(1, 20))
    story.append(Paragraph(f"Certificate ID: {certificate.unique_id}", styles['Normal']))
    story.append(Spacer(1, 30))
    
    # Add Edoble company details
    story.append(Paragraph("Empowering Innovation, Delivering Impact", styles['Normal']))
    story.append(Spacer(1, 10))
    story.append(Paragraph("Chennai, Tamil Nadu – India", styles['Normal']))
    story.append(Spacer(1, 10))
    story.append(Paragraph("Phone: +91 82481 85491 | Email: edoble.official@gmail.com", styles['Normal']))
    story.append(Spacer(1, 10))
    story.append(Paragraph("Website: www.edoble.in", styles['Normal']))
    
    # Add QR code
    qr_filename = f"qr_{certificate.unique_id}.png"
    qr_path = generate_qr_code(certificate.verification_url, qr_filename)
    if qr_path and os.path.exists(qr_path):
        try:
            img = Image(qr_path, width=1*inch, height=1*inch)
            story.append(Spacer(1, 20))
            story.append(img)
            print(f"✅ QR code added to PDF: {qr_path}")
        except Exception as e:
            print(f"❌ Error adding QR code to PDF: {e}")
    else:
        print(f"⚠️ QR code not found or could not be generated: {qr_path}")
    
    doc.build(story)
    buffer.seek(0)
    return buffer

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid username or password')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        flash('Access denied')
        return redirect(url_for('index'))
    
    certificates = Certificate.query.order_by(Certificate.created_at.desc()).all()
    today = datetime.now().date()
    
    # Calculate certificates created this month
    this_month_count = sum(1 for cert in certificates if cert.created_at.date() >= today)
    
    return render_template('admin_dashboard.html', certificates=certificates, today=today, this_month_count=this_month_count)

@app.route('/admin/create_certificate', methods=['GET', 'POST'])
@login_required
def create_certificate():
    if not current_user.is_admin:
        flash('Access denied')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        holder_name = request.form['holder_name']
        course_name = request.form['course_name']
        issue_date = datetime.strptime(request.form['issue_date'], '%Y-%m-%d')
        issuer_name = request.form['issuer_name']
        
        # Generate unique ID
        unique_id = str(uuid.uuid4())[:8].upper()
        verification_url = f"{request.host_url}verify/{unique_id}"
        
        # Handle logo upload
        issuer_logo = None
        if 'issuer_logo' in request.files:
            file = request.files['issuer_logo']
            if file and file.filename:
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                issuer_logo = file_path
        
        certificate = Certificate(
            unique_id=unique_id,
            holder_name=holder_name,
            course_name=course_name,
            issue_date=issue_date,
            issuer_name=issuer_name,
            issuer_logo=issuer_logo,
            verification_url=verification_url
        )
        
        db.session.add(certificate)
        db.session.commit()
        
        # Generate PDF
        pdf_buffer = generate_certificate_pdf(certificate)
        
        flash('Certificate created successfully!')
        return send_file(
            pdf_buffer,
            as_attachment=True,
            download_name=f"certificate_{unique_id}.pdf",
            mimetype='application/pdf'
        )
    
    return render_template('create_certificate.html')

@app.route('/verify/<unique_id>')
def verify_certificate(unique_id):
    certificate = Certificate.query.filter_by(unique_id=unique_id).first()
    
    if certificate and certificate.is_valid:
        return render_template('verify_certificate.html', certificate=certificate, valid=True, now=datetime.now())
    else:
        return render_template('verify_certificate.html', certificate=None, valid=False, now=datetime.now())

@app.route('/search')
def search_certificate():
    unique_id = request.args.get('unique_id', '').strip()
    if unique_id:
        return redirect(url_for('verify_certificate', unique_id=unique_id))
    return redirect(url_for('index'))

@app.route('/api/certificates')
@login_required
def api_certificates():
    if not current_user.is_admin:
        return jsonify({'error': 'Access denied'}), 403
    
    certificates = Certificate.query.all()
    return jsonify([{
        'id': c.id,
        'unique_id': c.unique_id,
        'holder_name': c.holder_name,
        'course_name': c.course_name,
        'issue_date': c.issue_date.strftime('%Y-%m-%d'),
        'issuer_name': c.issuer_name,
        'verification_url': c.verification_url,
        'is_valid': c.is_valid
    } for c in certificates])

@app.route('/admin/delete_certificate/<unique_id>', methods=['POST'])
@login_required
def delete_certificate(unique_id):
    if not current_user.is_admin:
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    certificate = Certificate.query.filter_by(unique_id=unique_id).first()
    if certificate:
        try:
            # Delete associated QR code file if it exists
            qr_filename = f"qr_{unique_id}.png"
            qr_path = os.path.join(app.config['UPLOAD_FOLDER'], qr_filename)
            if os.path.exists(qr_path):
                try:
                    os.remove(qr_path)
                except OSError as e:
                    # Log the error but continue with certificate deletion
                    print(f"Warning: Could not delete QR code file {qr_path}: {e}")
            
            # Delete the certificate from database
            db.session.delete(certificate)
            db.session.commit()
            flash(f'Certificate for {certificate.holder_name} (ID: {unique_id}) deleted successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error deleting certificate: {str(e)}', 'error')
            print(f"Error deleting certificate {unique_id}: {e}")
    else:
        flash(f'Certificate with ID {unique_id} not found!', 'error')
    
    return redirect(url_for('admin_dashboard'))

@app.route('/qr/<unique_id>')
def get_qr_code(unique_id):
    """Serve QR code image for a certificate"""
    qr_path = get_qr_code_path(unique_id)
    
    if qr_path:
        return send_file(qr_path, mimetype='image/png')
    else:
        # Generate QR code if it doesn't exist
        certificate = Certificate.query.filter_by(unique_id=unique_id).first()
        if certificate:
            qr_filename = f"qr_{unique_id}.png"
            qr_path = generate_qr_code(certificate.verification_url, qr_filename)
            if qr_path and os.path.exists(qr_path):
                return send_file(qr_path, mimetype='image/png')
        
        # Return a default image or 404
        return "QR code not found", 404

@app.route('/admin/regenerate_qr/<unique_id>', methods=['POST'])
@login_required
def regenerate_qr_code(unique_id):
    """Regenerate QR code for a certificate"""
    if not current_user.is_admin:
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    certificate = Certificate.query.filter_by(unique_id=unique_id).first()
    if certificate:
        try:
            # Generate new QR code
            qr_filename = f"qr_{unique_id}.png"
            qr_path = generate_qr_code(certificate.verification_url, qr_filename)
            
            if qr_path and os.path.exists(qr_path):
                flash(f'QR code regenerated successfully for {certificate.holder_name}!', 'success')
            else:
                flash(f'Error regenerating QR code for {certificate.holder_name}', 'error')
        except Exception as e:
            flash(f'Error regenerating QR code: {str(e)}', 'error')
            print(f"Error regenerating QR code for {unique_id}: {e}")
    else:
        flash(f'Certificate with ID {unique_id} not found!', 'error')
    
    return redirect(url_for('admin_dashboard'))

@app.route('/certificate/<unique_id>/download')
def download_certificate(unique_id):
    """Download certificate PDF"""
    certificate = Certificate.query.filter_by(unique_id=unique_id).first()
    if certificate and certificate.is_valid:
        try:
            # Generate PDF
            pdf_buffer = generate_certificate_pdf(certificate)
            return send_file(
                pdf_buffer,
                as_attachment=True,
                download_name=f"edoble_certificate_{unique_id}.pdf",
                mimetype='application/pdf'
            )
        except Exception as e:
            flash(f'Error generating certificate: {str(e)}', 'error')
            return redirect(url_for('verify_certificate', unique_id=unique_id))
    else:
        flash('Certificate not found or invalid', 'error')
        return redirect(url_for('index'))

@app.route('/certificate/<unique_id>/preview')
def preview_certificate(unique_id):
    """Preview certificate PDF in browser"""
    certificate = Certificate.query.filter_by(unique_id=unique_id).first()
    if certificate and certificate.is_valid:
        try:
            # Generate PDF
            pdf_buffer = generate_certificate_pdf(certificate)
            return send_file(
                pdf_buffer,
                as_attachment=False,
                download_name=f"edoble_certificate_{unique_id}.pdf",
                mimetype='application/pdf'
            )
        except Exception as e:
            flash(f'Error generating certificate: {str(e)}', 'error')
            return redirect(url_for('verify_certificate', unique_id=unique_id))
    else:
        flash('Certificate not found or invalid', 'error')
        return redirect(url_for('index'))

@app.route('/admin/toggle_certificate_status/<unique_id>', methods=['POST'])
@login_required
def toggle_certificate_status(unique_id):
    """Toggle certificate status (valid/invalid)"""
    if not current_user.is_admin:
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    certificate = Certificate.query.filter_by(unique_id=unique_id).first()
    if certificate:
        try:
            # Toggle the status
            certificate.is_valid = not certificate.is_valid
            db.session.commit()
            
            status_text = "valid" if certificate.is_valid else "invalid"
            flash(f'Certificate for {certificate.holder_name} (ID: {unique_id}) marked as {status_text}!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating certificate status: {str(e)}', 'error')
            print(f"Error updating certificate status for {unique_id}: {e}")
    else:
        flash(f'Certificate with ID {unique_id} not found!', 'error')
    
    return redirect(url_for('admin_dashboard'))

def init_app():
    """Initialize the application"""
    with app.app_context():
        try:
            db.create_all()
            
            # Create admin user if not exists
            admin_user = User.query.filter_by(username='admin').first()
            if not admin_user:
                admin_user = User(
                    username='admin',
                    email='admin@example.com',
                    password_hash=generate_password_hash('admin123'),
                    is_admin=True
                )
                db.session.add(admin_user)
                db.session.commit()
                print("✅ Admin user created successfully")
        except Exception as e:
            print(f"❌ Error initializing app: {e}")

if __name__ == '__main__':
    init_app()
    app.run(debug=True, host='0.0.0.0', port=5000) 