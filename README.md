# Edoble Intern Certificate Verification System

A comprehensive certificate verification and generation system built for Edoble, designed to manage and verify internship certificates with QR code integration and PDF generation.

## 🌟 Features

### Core Functionality
- **Certificate Creation**: Admin panel for creating intern certificates
- **QR Code Generation**: Automatic QR code generation for each certificate
- **PDF Generation**: Professional PDF certificates using JPG templates
- **Certificate Verification**: Public verification system with unique IDs
- **Status Management**: Toggle certificate validity (valid/invalid)
- **Preview & Download**: Certificate preview and download functionality

### Admin Features
- **Dashboard**: Comprehensive admin dashboard with statistics
- **Certificate Management**: Create, view, delete, and manage certificates
- **QR Code Management**: Regenerate and view QR codes
- **Status Control**: Toggle certificate validity status
- **Bulk Operations**: Efficient certificate management

### User Features
- **Public Verification**: Easy certificate verification by ID or QR code
- **Certificate Preview**: Visual preview of certificates
- **Download Options**: PDF download and print functionality
- **QR Code Scanning**: Mobile-friendly QR code verification

## 🚀 AWS Deployment

### Prerequisites
1. **AWS Account**: Active AWS account with appropriate permissions
2. **AWS CLI**: Install and configure AWS CLI
3. **EB CLI**: Install Elastic Beanstalk CLI
4. **Python 3.11**: Ensure Python 3.11 is available

### Quick Deployment

#### Option 1: Using Deployment Script
```bash
# Make deployment script executable
chmod +x deploy.sh

# Run deployment
./deploy.sh
```

#### Option 2: Manual Deployment
```bash
# Install EB CLI
pip install awsebcli

# Initialize EB application
eb init --platform python-3.11 --region us-east-1

# Create environment
eb create edoble-certificate-prod --instance-type t3.small --single-instance

# Deploy
eb deploy
```

### Environment Configuration

1. **Copy Environment Template**:
   ```bash
   cp env.example .env
   ```

2. **Update Configuration**:
   - Set `SECRET_KEY` to a strong secret
   - Configure database URL (SQLite for dev, RDS for production)
   - Set AWS credentials and region
   - Configure S3 bucket for file storage

3. **Database Options**:
   - **Development**: SQLite (default)
   - **Production**: Amazon RDS (PostgreSQL/MySQL)

### AWS Services Used

- **Elastic Beanstalk**: Application hosting
- **RDS**: Database (optional, for production)
- **S3**: File storage (optional, for production)
- **CloudFront**: CDN (optional, for performance)
- **Route 53**: DNS management (optional)

## 📦 Local Development

### Installation

1. **Clone Repository**:
   ```bash
   git clone <repository-url>
   cd certificate
   ```

2. **Create Virtual Environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set Environment Variables**:
   ```bash
   cp env.example .env
   # Edit .env with your configuration
   ```

5. **Run Application**:
   ```bash
   python run.py
   ```

### Default Access
- **Application**: http://localhost:5000
- **Admin Login**: http://localhost:5000/login
- **Credentials**: admin / admin123

## 🗄️ Database Schema

### Certificate Table
- `id` - Primary key
- `unique_id` - Unique certificate identifier
- `holder_name` - Intern name
- `course_name` - Internship program/project
- `issue_date` - Completion date
- `issuer_name` - Issuing organization (Edoble)
- `issuer_logo` - Company logo path
- `verification_url` - Verification URL
- `created_at` - Creation timestamp
- `is_valid` - Certificate validity status

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the root directory:

```env
# Flask Configuration
SECRET_KEY=your-super-secret-key-change-this-in-production
FLASK_ENV=production
FLASK_DEBUG=False

# Database Configuration
DATABASE_URL=sqlite:///certificates.db
# For production, consider using RDS:
# DATABASE_URL=postgresql://username:password@your-rds-endpoint:5432/certificates

# AWS Configuration
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key

# S3 Configuration (for file storage)
S3_BUCKET=your-certificate-bucket
S3_REGION=us-east-1

# Application Configuration
UPLOAD_FOLDER=uploads
MAX_CONTENT_LENGTH=16777216  # 16MB max file size
```

### Application Settings
- **Database**: SQLite (can be upgraded to PostgreSQL/MySQL)
- **File Storage**: Local file system (can be upgraded to S3)
- **QR Code**: PNG format
- **PDF**: A4 format with Edoble branding

## 🎨 Customization

### Edoble Branding
The system is fully customized for Edoble with:
- Company logo and branding
- Edoble color scheme (#2c3e50, #3498db)
- Company tagline and mission
- Contact information integration
- Professional certificate design

### Certificate Design
Certificates include:
- Edoble company header
- "Code with a Purpose" tagline
- Professional layout
- QR code for verification
- Company contact details

## 🔒 Security Features

- **Password Hashing** - Secure password storage
- **Session Management** - Flask-Login integration
- **Input Validation** - Form validation and sanitization
- **File Upload Security** - Secure file handling
- **CSRF Protection** - Cross-site request forgery protection

## 📱 API Endpoints

### Public Endpoints
- `GET /` - Home page with verification
- `GET /verify/<unique_id>` - Certificate verification
- `GET /search` - Search certificates

### Admin Endpoints
- `GET /login` - Admin login page
- `POST /login` - Admin authentication
- `GET /admin/dashboard` - Admin dashboard
- `GET /admin/create_certificate` - Certificate creation form
- `POST /admin/create_certificate` - Create certificate

## 🚀 Performance Optimization

### For AWS Production
1. **Database**: Use Amazon RDS for better performance
2. **File Storage**: Use S3 for scalable file storage
3. **CDN**: Use CloudFront for static assets
4. **Load Balancer**: Use Application Load Balancer
5. **Auto Scaling**: Configure auto-scaling groups

### Monitoring
- **CloudWatch**: Application and infrastructure monitoring
- **X-Ray**: Distributed tracing
- **Health Checks**: Automated health monitoring

## 🔧 Troubleshooting

### Common Issues
1. **Template Not Found**: Ensure `image_2.jpg` is in the uploads folder
2. **Font Issues**: System will fallback to default fonts
3. **QR Code Generation**: Check file permissions for uploads folder
4. **Database Issues**: Ensure database file is writable

### AWS-Specific Issues
1. **Deployment Failures**: Check EB logs with `eb logs`
2. **Environment Issues**: Use `eb health` to check environment status
3. **Configuration Issues**: Verify environment variables in EB console

## 📈 Scaling Considerations

### Horizontal Scaling
- Use multiple EC2 instances behind a load balancer
- Implement session storage (Redis/ElastiCache)
- Use shared file storage (S3/EFS)

### Vertical Scaling
- Upgrade instance types for better performance
- Use RDS with read replicas
- Implement caching strategies

## 🔄 CI/CD Pipeline

### GitHub Actions (Optional)
```yaml
name: Deploy to AWS
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy to EB
        uses: einaregilsson/beanstalk-deploy@v21
        with:
          aws_access_key: ${{ secrets.AWS_ACCESS_KEY }}
          aws_secret_key: ${{ secrets.AWS_SECRET_KEY }}
          application_name: edoble-certificate
          environment_name: edoble-certificate-prod
          region: us-east-1
          version_label: ${{ github.sha }}
```

## 📞 Support

For technical support or questions:
- **Email**: edoble.official@gmail.com
- **Website**: www.edoble.in
- **Phone**: +91 82481 85491

## 📄 License

This project is proprietary software developed for Edoble. All rights reserved.

---

**Built with ❤️ by Edoble Team**
*Code with a Purpose - Build smart. Think bold. Impact real.* #   c e r t i f i c a t e _ v e r f i c a t i o n 
 
 
