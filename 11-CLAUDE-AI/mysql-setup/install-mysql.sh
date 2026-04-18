#!/bin/bash
# MySQL Installation Script for PHI-Canto Hybrid System

echo "🚀 Installing MySQL for PHI-Canto tracking system..."

# Update package list
sudo apt update

# Install MySQL server and client
sudo apt install -y mysql-server mysql-client python3-pip

# Install Python MySQL connector
pip3 install mysql-connector-python

# Start MySQL service
sudo service mysql start

# Enable MySQL to start on boot
sudo systemctl enable mysql

echo "✅ MySQL installation complete!"
echo ""
echo "Next steps:"
echo "1. Run: sudo mysql_secure_installation  (optional, for security)"
echo "2. Create database: sudo mysql < 01-database-schema.sql"
echo "3. Import sample data: sudo mysql < 02-sample-data.sql"
echo "4. Test connection: python3 phi_canto_db.py"
echo ""
echo "If you get authentication errors, run:"
echo "  sudo mysql"
echo "  ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'your_password';"
echo "  FLUSH PRIVILEGES;"
echo "  EXIT;"