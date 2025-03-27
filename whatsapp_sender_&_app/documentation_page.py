import streamlit as st
from datetime import datetime

def show_documentation():
    st.markdown(
    '''
    <h1 style="background-image: linear-gradient(to right, #4F959D, #98D2C0); 
             -webkit-background-clip: text; 
             color: transparent; 
             margin: 20px 0;">
        Client Credits Manager Documentation
    </h1>
    ''', 
    unsafe_allow_html=True
    )

    # Introduction
    st.markdown(
    '''
    <h2 style="background-image: linear-gradient(to left, #FFF0BD, #FDAB9E); 
             -webkit-background-clip: text; 
             color: transparent; 
             margin: 20px 0;">
        Introduction
    </h2>
    ''', 
    unsafe_allow_html=True
    )
    
    st.markdown("""
    This documentation provides a comprehensive guide to the Client Credits Manager application.
    The application is built using Streamlit and provides functionality for managing client credits,
    sending WhatsApp messages, and maintaining a backup system.
    """)

    # System Requirements
    st.markdown(
    '''
    <h2 style="background-image: linear-gradient(to left, #FFF0BD, #FDAB9E); 
             -webkit-background-clip: text; 
             color: transparent; 
             margin: 20px 0;">
        System Requirements
    </h2>
    ''', 
    unsafe_allow_html=True
    )
    
    st.markdown("""
    The application requires the following dependencies:
    - Python 3.7 or higher
    - Streamlit 1.35.0
    - Pandas 2.2.2
    - PyWhatKit 5.4
    - PyAutoGUI 0.9.54
    - Rich 13.7.1
    """)

    # Installation
    st.markdown(
    '''
    <h2 style="background-image: linear-gradient(to left, #FFF0BD, #FDAB9E); 
             -webkit-background-clip: text; 
             color: transparent; 
             margin: 20px 0;">
        Installation
    </h2>
    ''', 
    unsafe_allow_html=True
    )
    
    st.markdown("""
    1. Clone the repository
    2. Install dependencies using pip:
       ```bash
       pip install -r requirements.txt
       ```
    3. Run the application:
       ```bash
       python app_dashboard_client_credits_manager.py
       ```
    """)

    # Features
    st.markdown(
    '''
    <h2 style="background-image: linear-gradient(to left, #FFF0BD, #FDAB9E); 
             -webkit-background-clip: text; 
             color: transparent; 
             margin: 20px 0;">
        Features
    </h2>
    ''', 
    unsafe_allow_html=True
    )
    
    features = {
        "Client Management": [
            "Add new clients",
            "Update client information",
            "Delete clients",
            "Search clients"
        ],
        "Credit Management": [
            "Add credits to client accounts",
            "Subtract credits from client accounts",
            "Track credit history"
        ],
        "WhatsApp Integration": [
            "Send automated messages",
            "Queue management",
            "Message history"
        ],
        "Backup System": [
            "Automatic backups",
            "Manual backup creation",
            "Backup restoration"
        ],
        "Settings Management": [
            "Configure backup intervals",
            "Set low credit thresholds",
            "Enable/disable notifications"
        ]
    }

    for feature, items in features.items():
        with st.expander(f"📌 {feature}", expanded=True):
            for item in items:
                st.markdown(f"- {item}")

    # User Interface
    st.markdown(
    '''
    <h2 style="background-image: linear-gradient(to left, #FFF0BD, #FDAB9E); 
             -webkit-background-clip: text; 
             color: transparent; 
             margin: 20px 0;">
        User Interface
    </h2>
    ''', 
    unsafe_allow_html=True
    )
    
    ui_components = {
        "Dashboard": [
            "Overview of client database",
            "Recent activity",
            "Low credit alerts"
        ],
        "Navigation Menu": [
            "Dashboard",
            "Run WhatsApp Sender",
            "Update Database",
            "Add Client",
            "Delete Client",
            "Update Phone",
            "Backup & Restore",
            "Settings"
        ],
        "Statistics Display": [
            "Total clients",
            "Total credits",
            "Average credits",
            "Low credit clients"
        ]
    }

    for component, items in ui_components.items():
        with st.expander(f"📊 {component}", expanded=True):
            for item in items:
                st.markdown(f"- {item}")

    # Database Management
    st.markdown(
    '''
    <h2 style="background-image: linear-gradient(to left, #FFF0BD, #FDAB9E); 
             -webkit-background-clip: text; 
             color: transparent; 
             margin: 20px 0;">
        Database Management
    </h2>
    ''', 
    unsafe_allow_html=True
    )
    
    st.markdown("""
    The application uses a CSV file for data storage with the following structure:
    
    ### Data Structure
    - **Clients**: Client names
    - **Phone_Numbers**: Contact information
    - **Credits**: Account balance
    - **Last_Updated**: Timestamp of last modification
    - **Status**: Client account status
    
    ### Data Validation
    - Phone number format validation
    - Credit amount validation
    - Duplicate entry prevention
    
    ### Data Backup
    - Automatic backups
    - Manual backup creation
    - Backup restoration
    """)

    # Backup and Restore
    st.markdown(
    '''
    <h2 style="background-image: linear-gradient(to left, #FFF0BD, #FDAB9E); 
             -webkit-background-clip: text; 
             color: transparent; 
             margin: 20px 0;">
        Backup and Restore
    </h2>
    ''', 
    unsafe_allow_html=True
    )
    
    backup_features = {
        "Automatic Backups": [
            "Configurable backup intervals",
            "Automatic backup creation",
            "Backup file rotation"
        ],
        "Manual Backups": [
            "Create backup on demand",
            "Backup file naming with timestamps",
            "Backup file organization"
        ],
        "Restore Functionality": [
            "Select backup to restore",
            "Safety backup creation before restore",
            "Validation of backup data"
        ]
    }

    for feature, items in backup_features.items():
        with st.expander(f"💾 {feature}", expanded=True):
            for item in items:
                st.markdown(f"- {item}")

    # WhatsApp Integration
    st.markdown(
    '''
    <h2 style="background-image: linear-gradient(to left, #FFF0BD, #FDAB9E); 
             -webkit-background-clip: text; 
             color: transparent; 
             margin: 20px 0;">
        WhatsApp Integration
    </h2>
    ''', 
    unsafe_allow_html=True
    )
    
    whatsapp_features = {
        "Message Types": [
            "Welcome messages",
            "Credit addition notifications",
            "Credit deduction notifications"
        ],
        "Message Queue": [
            "Queue management",
            "Message preview",
            "Queue clearing"
        ],
        "Automation": [
            "Automated message sending",
            "Scheduled messages",
            "Message history tracking"
        ]
    }

    for feature, items in whatsapp_features.items():
        with st.expander(f"📱 {feature}", expanded=True):
            for item in items:
                st.markdown(f"- {item}")

    # Settings
    st.markdown(
    '''
    <h2 style="background-image: linear-gradient(to left, #FFF0BD, #FDAB9E); 
             -webkit-background-clip: text; 
             color: transparent; 
             margin: 20px 0;">
        Settings
    </h2>
    ''', 
    unsafe_allow_html=True
    )
    
    settings_features = {
        "Backup Settings": [
            "Enable/disable auto backup",
            "Set backup interval",
            "Configure backup retention"
        ],
        "Credit Settings": [
            "Set low credit threshold",
            "Configure credit alerts"
        ],
        "Notification Settings": [
            "Enable/disable notifications",
            "Configure notification types"
        ]
    }

    for feature, items in settings_features.items():
        with st.expander(f"⚙️ {feature}", expanded=True):
            for item in items:
                st.markdown(f"- {item}")

    # Footer
    st.markdown("---")
    st.markdown(f"Documentation last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    show_documentation() 