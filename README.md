# Quality Rejection Management System (QRMS)

A comprehensive Streamlit-based Quality Rejection Management System designed for manufacturing process optimization and detailed rejection tracking.

## Features

### 🔐 Authentication & User Management
- Role-based access control (Super Admin, Admin, User)
- Secure password hashing with SHA256
- Multi-tier permission system
- User creation, management, and credential tracking

### 📊 Data Management
- Interactive dashboard with rejection analytics
- Real-time data entry for quality rejections
- Modular rejection type mapping
- Batch data entry capabilities
- Export functionality for reports

### 📧 Automated Reporting
- Daily email reports with rejection summaries
- Scheduled report delivery
- Configurable email settings
- Test email functionality

### 🛠️ Administrative Features
- Module and rejection type management
- User permission management
- Data visualization with Plotly charts
- CSV data export capabilities

## Quick Start

### Prerequisites
- Python 3.11+
- Streamlit
- Required packages (see requirements below)

### Installation

1. Clone the repository:
```bash
git clone <your-repository-url>
cd qrms
```

2. Install dependencies:
```bash
pip install streamlit pandas plotly schedule
```

3. Run the application:
```bash
streamlit run login.py --server.port 5000
```

4. Access the application at `http://localhost:5000`

## Default Login Credentials

**Super Administrator:**
- Username: `superadmin`
- Password: `admin123`

**Administrator:**
- Username: `admin`
- Password: `admin456`

**Quality Control User:**
- Username: `qcuser`
- Password: `user789`

> ⚠️ **Important**: Change these default passwords immediately after first login in a production environment.

## Project Structure

```
qrms/
├── login.py                 # Main entry point and authentication
├── pages/
│   ├── 00_Dashboard.py      # Analytics dashboard
│   ├── 01_Data_Entry.py     # Rejection data entry
│   ├── 02_Manage_Types.py   # Rejection type management
│   ├── 03_Email_Settings.py # Email configuration
│   ├── 04_Batch_Entry.py    # Bulk data entry
│   └── 05_User_Management.py # User administration
├── utils/
│   ├── auth.py              # Authentication manager
│   ├── data_manager.py      # Data operations
│   ├── email_sender.py      # Email functionality
│   └── scheduler.py         # Report scheduling
├── data/                    # Data storage directory
└── .streamlit/
    └── config.toml          # Streamlit configuration
```

## User Roles & Permissions

### Super Admin
- Full system access
- User management
- All data operations
- System configuration

### Admin
- Module and type management
- Data export
- View dashboard and data
- Limited user management

### User
- Data entry
- View dashboard
- View own data

## Configuration

### Streamlit Configuration
The application uses a custom Streamlit configuration in `.streamlit/config.toml`:

```toml
[server]
headless = true
address = "0.0.0.0"
port = 5000
```

### Email Configuration
Configure email settings through the Email Settings page in the application or modify the email configuration in the utils directory.

## Data Storage

The application uses JSON files for data storage:
- `data/users.json` - User accounts and credentials
- `data/rejections.csv` - Rejection records
- `data/rejection_types.csv` - Rejection type definitions
- `data/modules.csv` - Module definitions

## Development

### Adding New Features
1. Create new pages in the `pages/` directory
2. Follow the existing naming convention: `##_Page_Name.py`
3. Use the authentication manager for access control
4. Follow the established UI patterns

### Security Considerations
- All passwords are hashed using SHA256
- Role-based access control is enforced on all pages
- Session state management for authentication
- Secure file handling for data operations

## Deployment

### Replit Deployment
This application is optimized for Replit deployment:
1. Ensure all dependencies are installed
2. Configure the workflow to run `streamlit run login.py --server.port 5000`
3. Deploy using Replit's deployment features

### Production Deployment
For production environments:
1. Change all default passwords
2. Configure proper email SMTP settings
3. Set up proper data backup procedures
4. Consider using a proper database instead of JSON files
5. Implement SSL/TLS encryption

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions, please create an issue in the repository or contact the development team.