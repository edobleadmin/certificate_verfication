# 🚀 AWS Deployment Guide for Edoble Certificate System

This guide provides step-by-step instructions for deploying your Edoble Certificate Verification System on AWS.

## 📋 Prerequisites

### 1. AWS Account Setup
- [ ] Create AWS account at https://aws.amazon.com
- [ ] Set up billing alerts
- [ ] Create IAM user with appropriate permissions
- [ ] Configure AWS CLI with your credentials

### 2. Required Tools
- [ ] AWS CLI installed and configured
- [ ] EB CLI installed (`pip install awsebcli`)
- [ ] Git for version control
- [ ] Python 3.11

### 3. AWS Services You'll Use
- **Elastic Beanstalk**: Application hosting
- **RDS** (optional): Database for production
- **S3** (optional): File storage
- **CloudFront** (optional): CDN
- **Route 53** (optional): DNS management

## 🚀 Quick Deployment

### Option 1: Automated Deployment
```bash
# Make deployment script executable
chmod +x deploy.sh

# Run deployment
./deploy.sh
```

### Option 2: Manual Deployment
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

## 📝 Step-by-Step Deployment

### Step 1: Prepare Your Application

1. **Ensure all files are committed**:
   ```bash
   git add .
   git commit -m "Prepare for AWS deployment"
   ```

2. **Copy environment template**:
   ```bash
   cp env.example .env
   ```

3. **Update environment variables**:
   ```bash
   # Edit .env file with your configuration
   nano .env
   ```

### Step 2: Configure AWS Credentials

1. **Install AWS CLI**:
   ```bash
   # For Windows
   # Download from https://aws.amazon.com/cli/
   
   # For macOS
   brew install awscli
   
   # For Linux
   curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
   unzip awscliv2.zip
   sudo ./aws/install
   ```

2. **Configure AWS CLI**:
   ```bash
   aws configure
   # Enter your AWS Access Key ID
   # Enter your AWS Secret Access Key
   # Enter your default region (e.g., us-east-1)
   # Enter your output format (json)
   ```

### Step 3: Initialize Elastic Beanstalk

1. **Install EB CLI**:
   ```bash
   pip install awsebcli
   ```

2. **Initialize EB application**:
   ```bash
   eb init
   ```

3. **Follow the prompts**:
   - Select your region
   - Create new application
   - Choose Python platform
   - Set up SSH (optional)

### Step 4: Create Environment

1. **Create production environment**:
   ```bash
   eb create edoble-certificate-prod --instance-type t3.small --single-instance
   ```

2. **Wait for environment creation** (5-10 minutes)

3. **Check environment status**:
   ```bash
   eb status
   ```

### Step 5: Configure Environment Variables

1. **Set environment variables in EB console**:
   - Go to AWS Elastic Beanstalk console
   - Select your environment
   - Go to Configuration → Software
   - Add environment variables:
     ```
     SECRET_KEY=your-super-secret-key
     FLASK_ENV=production
     DATABASE_URL=sqlite:///certificates.db
     ```

### Step 6: Deploy Application

1. **Deploy to EB**:
   ```bash
   eb deploy
   ```

2. **Check deployment status**:
   ```bash
   eb health
   ```

3. **Open your application**:
   ```bash
   eb open
   ```

## 🔧 Advanced Configuration

### Database Configuration

#### Option 1: SQLite (Development)
```env
DATABASE_URL=sqlite:///certificates.db
```

#### Option 2: RDS PostgreSQL (Production)
1. **Create RDS instance**:
   - Go to RDS console
   - Create PostgreSQL instance
   - Note the endpoint and credentials

2. **Update environment variables**:
   ```env
   DATABASE_URL=postgresql://username:password@your-rds-endpoint:5432/certificates
   ```

### File Storage Configuration

#### Option 1: Local Storage (Development)
```env
UPLOAD_FOLDER=uploads
```

#### Option 2: S3 Storage (Production)
1. **Create S3 bucket**:
   ```bash
   aws s3 mb s3://your-certificate-bucket
   ```

2. **Update environment variables**:
   ```env
   S3_BUCKET=your-certificate-bucket
   AWS_REGION=us-east-1
   ```

### SSL/HTTPS Configuration

1. **Request SSL certificate**:
   - Go to Certificate Manager
   - Request public certificate
   - Add your domain

2. **Configure HTTPS in EB**:
   - Go to EB console
   - Configuration → Load balancer
   - Add HTTPS listener
   - Attach your certificate

## 📊 Monitoring and Logs

### View Application Logs
```bash
eb logs
```

### Monitor Application Health
```bash
eb health
```

### Set up CloudWatch Alarms
1. Go to CloudWatch console
2. Create alarms for:
   - CPU utilization
   - Memory usage
   - Request count
   - Error rate

## 🔄 CI/CD Pipeline

### GitHub Actions Setup

1. **Create `.github/workflows/deploy.yml`**:
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

2. **Add secrets to GitHub**:
   - Go to repository settings
   - Add secrets:
     - `AWS_ACCESS_KEY`
     - `AWS_SECRET_KEY`

## 🚨 Troubleshooting

### Common Issues

#### 1. Deployment Failures
```bash
# Check EB logs
eb logs

# Check environment health
eb health

# Restart environment
eb restart
```

#### 2. Environment Variables Not Working
- Verify in EB console → Configuration → Software
- Check application logs for errors
- Restart environment after changes

#### 3. Database Connection Issues
- Verify RDS security groups
- Check database endpoint
- Test connection from EB environment

#### 4. File Upload Issues
- Check S3 bucket permissions
- Verify IAM roles
- Check file size limits

### Performance Optimization

#### 1. Auto Scaling
```bash
# Configure auto scaling
eb config
# Add auto scaling configuration
```

#### 2. Load Balancer
- Enable application load balancer
- Configure health checks
- Set up SSL termination

#### 3. Caching
- Use ElastiCache for Redis
- Implement application-level caching
- Use CloudFront for static assets

## 💰 Cost Optimization

### Instance Types
- **Development**: t3.micro ($8-10/month)
- **Production**: t3.small ($15-20/month)
- **High Traffic**: t3.medium ($30-40/month)

### Database Options
- **SQLite**: Free (development only)
- **RDS t3.micro**: $15-20/month
- **RDS t3.small**: $30-40/month

### Storage Options
- **Local Storage**: Free (limited)
- **S3**: $0.023/GB/month
- **CloudFront**: $0.085/GB (first 10TB)

## 🔒 Security Best Practices

### 1. Environment Variables
- Never commit secrets to Git
- Use EB environment variables
- Rotate secrets regularly

### 2. Database Security
- Use RDS with encryption
- Configure security groups
- Enable automated backups

### 3. Application Security
- Enable HTTPS
- Configure CORS properly
- Implement rate limiting

### 4. Access Control
- Use IAM roles
- Limit admin access
- Enable MFA

## 📈 Scaling Strategies

### Horizontal Scaling
1. **Multiple Instances**:
   - Configure auto scaling
   - Use load balancer
   - Implement session storage

2. **Database Scaling**:
   - Use RDS read replicas
   - Implement connection pooling
   - Consider Aurora Serverless

### Vertical Scaling
1. **Instance Upgrades**:
   - t3.small → t3.medium → t3.large
   - Monitor performance metrics
   - Scale based on usage

2. **Database Upgrades**:
   - Upgrade RDS instance class
   - Add more storage
   - Enable performance insights

## 🎯 Production Checklist

- [ ] Environment variables configured
- [ ] Database properly set up
- [ ] SSL certificate installed
- [ ] Monitoring configured
- [ ] Backups enabled
- [ ] Security groups configured
- [ ] Auto scaling enabled
- [ ] Health checks working
- [ ] Logs being collected
- [ ] Alerts configured

## 📞 Support

For deployment issues:
- **AWS Support**: Available in AWS console
- **EB Documentation**: https://docs.aws.amazon.com/elasticbeanstalk/
- **Edoble Support**: edoble.official@gmail.com

---

**Happy Deploying! 🚀**

*Built with ❤️ by Edoble Team* 