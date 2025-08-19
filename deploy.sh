#!/bin/bash

# AWS Elastic Beanstalk Deployment Script
# Make sure you have AWS CLI and EB CLI installed

echo "🚀 Starting AWS deployment for Edoble Certificate System..."

# Check if EB CLI is installed
if ! command -v eb &> /dev/null; then
    echo "❌ EB CLI not found. Please install it first:"
    echo "pip install awsebcli"
    exit 1
fi

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI not found. Please install it first:"
    echo "https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html"
    exit 1
fi

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp env.example .env
    echo "⚠️  Please update .env file with your configuration before deploying"
fi

# Initialize EB application if not already done
if [ ! -f .elasticbeanstalk/config.yml ]; then
    echo "🔧 Initializing Elastic Beanstalk application..."
    eb init --platform python-3.11 --region us-east-1
fi

# Create environment if it doesn't exist
if ! eb status &> /dev/null; then
    echo "🌍 Creating Elastic Beanstalk environment..."
    eb create edoble-certificate-prod --instance-type t3.small --single-instance
else
    echo "📦 Deploying to existing environment..."
    eb deploy
fi

echo "✅ Deployment completed!"
echo "🌐 Your application should be available at:"
eb status 