# Client Credits Manager

![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)

## Introduction
A comprehensive solution for managing client credits with WhatsApp integration and automated backups.

## Features

### 📌 Client Management
- Add new clients
- Update client information
- Delete clients
- Search clients

### 💳 Credit Management
- Add credits to accounts
- Subtract credits
- Track credit history

### 📱 WhatsApp Integration
- Automated messages
- Queue management
- Message history

### 💾 Backup System
- Automatic backups
- Manual backup creation
- Backup restoration

### ⚙️ Settings Management
- Configure backup intervals
- Set credit thresholds
- Notification settings

## System Requirements
- Python 3.7+
- Dependencies:
- Streamlit 1.35.0
Pandas 2.2.2
PyWhatKit 5.4
PyAutoGUI 0.9.54
Rich 13.7.1

# Client Management System

## User Interface

### 📊 Dashboard
- **Client database overview** - View all client records at a glance  
- **Recent activity** - Track latest credit changes and updates  
- **Low credit alerts** - Highlighted warnings for accounts below threshold  

### 📊 Navigation Menu
- **Dashboard** - Main overview screen  
- **Run WhatsApp Sender** - Message queue management  
- **Update Database** - Modify existing records  
- **Add/Delete Client** - Client lifecycle management  
- **Backup & Restore** - Data protection controls  
- **Settings** - System configuration  

### 📊 Statistics
| Metric | Description |
|--------|-------------|
| Total Clients | Current active accounts |
| Total Credits | Sum of all client balances |
| Average Credits | Mean credit value across clients |
| Low Credit Clients | Accounts requiring attention |

## Database Management

### Data Structure
| Column | Type | Description |
|--------|------|-------------|
| Clients | String | Client full names |
| Phone_Numbers | String | Verified contact numbers |
| Credits | Numeric | Current account balance |
| Last_Updated | DateTime | Last modification timestamp |
| Status | String | Active/Inactive status |

### Data Validation
- **Phone numbers**: Format verification (+XX XXX XXXX XXX)  
- **Credit amounts**: Positive number enforcement  
- **Duplicate prevention**: Unique client/phone checks  

## Backup System

### Automatic Backups
- ⏰ **Configurable intervals**: Set hourly/daily/weekly  
- 🔄 **File rotation**: Maintains last 7 backups  
- 🕒 **Timestamped files**: YYYY-MM-DD_HH-MM format
- 
## Conclusion  
The Client Credits Manager provides an all-in-one solution for:  
✔️ **Streamlined client credit tracking**  
✔️ **Automated WhatsApp communication**  
✔️ **Robust data protection**  

