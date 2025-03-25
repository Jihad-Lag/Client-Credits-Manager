# ----- Created_By_Jihad_Laglil -----

# -===== Import Libraries =====-
import streamlit as st
import pandas as pd
import time
from datetime import datetime, timedelta
import re
import os
import json
from pathlib import Path

# -===== Configuration Page =====-
st.set_page_config(
    page_title="Client Credits Manager",
    page_icon="💶",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -===== Dataset =====-
dataset_path = "./database/clients_data.csv"

# -===== Configuration : ( Cache - Settings - Reading Dataset - Warning Time ) =====-
if "df_cache" not in st.session_state:
    st.session_state.df_cache = [] 
if "df_current" not in st.session_state:
    try:
        dataset = pd.read_csv(dataset_path, index_col=0)
        st.session_state.df_current = dataset.copy()
    except FileNotFoundError:
        st.session_state.df_current = pd.DataFrame(columns=["Clients", "Phone_Numbers", "Credits", "Last_Updated", "Notes", "Status"])
if "cache_size" not in st.session_state:
    st.session_state.cache_size = 20  
if "changes_made" not in st.session_state:
    st.session_state.changes_made = False  
if "last_warning_time" not in st.session_state:
    st.session_state.last_warning_time = datetime.now()
if "warning_duration" not in st.session_state:
    st.session_state.warning_duration = 5 
if "backup_path" not in st.session_state:
    st.session_state.backup_path = "backups"
    if not os.path.exists(st.session_state.backup_path):
        os.makedirs(st.session_state.backup_path)
if "settings" not in st.session_state:
    st.session_state.settings = {
        "auto_backup": True,
        "backup_interval": 30,  
        "low_credit_threshold": 100,
        "notification_enabled": True
    }
df = st.session_state.df_current

# -===== Functions : ( Save - Undo Change - Restore & Create Backup - Warning Time & Show ) =====-

def should_show_warning():
    if not st.session_state.changes_made:
        return False
    time_elapsed = (datetime.now() - st.session_state.last_warning_time).total_seconds()
    return time_elapsed < st.session_state.warning_duration


def reset_warning_timer():
    st.session_state.last_warning_time = datetime.now()


def save_state_to_cache():
    if len(st.session_state.df_cache) >= st.session_state.cache_size:
        st.session_state.df_cache.pop(0)  
    st.session_state.df_cache.append(st.session_state.df_current.copy())
    st.session_state.changes_made = True
    reset_warning_timer() 


def undo_changes():
    if st.session_state.df_cache:
        st.session_state.df_current = st.session_state.df_cache.pop()
        reset_warning_timer()  
        return True
    return False


def save_changes_to_file():
    st.session_state.df_current.to_csv(dataset_path, index=True)
    st.session_state.changes_made = False
    st.session_state.df_cache = [] 

def create_backup():
    """Create a backup of the current database"""
    try:
        if not os.path.exists(st.session_state.backup_path):
            os.makedirs(st.session_state.backup_path)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = os.path.join(st.session_state.backup_path, f"backup_{timestamp}.csv")
        st.session_state.df_current.to_csv(backup_file, index=True)
        json_backup = os.path.join(st.session_state.backup_path, f"backup_{timestamp}.json")
        st.session_state.df_current.to_json(json_backup, orient='records')
        
        return backup_file
    except Exception as e:
        st.error(f"Error creating backup: {str(e)}")
        return None

def restore_backup(backup_file):
    """Restore from a backup file"""
    try:
        if not os.path.exists(backup_file):
            raise FileNotFoundError(f"Backup file not found: {backup_file}")
        if backup_file.endswith('.csv'):
            backup_df = pd.read_csv(backup_file, index_col=0)
        elif backup_file.endswith('.json'):
            backup_df = pd.read_json(backup_file)
        else:
            raise ValueError("Unsupported backup file format")
        required_columns = ["Clients", "Phone_Numbers", "Credits", "Last_Updated", "Notes", "Status"]
        if not all(col in backup_df.columns for col in required_columns):
            raise ValueError("Backup file is missing required columns")
        st.session_state.df_current = backup_df.copy()
        st.session_state.changes_made = True
        
        return True
    except Exception as e:
        st.error(f"Error restoring backup: {str(e)}")
        return False

# -===== Functions : ( Verification Number Phone - Show Up Database - Statistics Columns - Check Low & Database Credits) =====-

def Show_up_client_Database():
        if "filtered_view" not in st.session_state:
         st.markdown(
    '''
    <h2 style="background-image: linear-gradient(to left, #FFF0BD, #FDAB9E); 
             -webkit-background-clip: text; 
             color: transparent; 
             margin: 20px 0;">
        Client Database
    </h2>
    ''', 
    unsafe_allow_html=True
    )
         df_current = st.session_state.df_current
        if not df_current.empty:
           df_display = df_current.copy()
        if "Credits" in df_display.columns:
            df_display["Credits"] = df_display["Credits"].apply(lambda x: f"${float(x):,.2f}")
            st.dataframe(df_display, width=1000)
        else:
         st.info("No clients in the database. Add clients using the sidebar.")

def validate_phone_number(phone):
    """Validate phone number format"""
    pattern = re.compile(r'^\+?1?\d{9,15}$')
    return bool(pattern.match(phone))



def show_statistics():
    """Display database statistics"""
    if st.session_state.df_current.empty:
        return
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_clients = len(st.session_state.df_current)
        st.metric("Total Clients", total_clients)
    
    with col2:
        total_credits = st.session_state.df_current["Credits"].sum()
        st.metric("Total Credits", f"$ {total_credits:,.2f}")
    
    with col3:
        avg_credits = st.session_state.df_current["Credits"].mean()
        st.metric("Average Credits", f"$ {avg_credits:,.2f}")
    
    with col4:
        low_credit_clients = len(st.session_state.df_current[st.session_state.df_current["Credits"] < st.session_state.settings["low_credit_threshold"]])
        st.metric("Low Credit Clients", low_credit_clients)
    
    
def  low_credit_clients_show_up_df():
 low_credit_clients = check_low_credits()
 if low_credit_clients is not None:
    st.markdown(
    '''
    <h2 style="background-image: linear-gradient(to left, #FFF0BD, #FDAB9E); 
             -webkit-background-clip: text; 
             color: transparent; 
             margin: 20px 0;">
        Low Credit Clients
    </h2>
    ''', 
    unsafe_allow_html=True
    )
    st.dataframe(low_credit_clients[["Clients", "Phone_Numbers", "Credits"]], width=1000)


def check_low_credits():
    """Check for clients with low credits"""
    low_credit_clients = st.session_state.df_current[
        st.session_state.df_current["Credits"] < st.session_state.settings["low_credit_threshold"]
    ]
    if not low_credit_clients.empty:
        st.warning(f"⚠️ {len(low_credit_clients)} clients have low credits (below ${st.session_state.settings['low_credit_threshold']})")
        return low_credit_clients
    return None


# -===== Features : ( [ Add - Delete - Search - Update ] Clients ) =====-

def add_client(name, phone, credits, status="Active"):
    """Add a new client to the database with validation"""
    save_state_to_cache()
    
    if not name or not phone or credits is None:
        raise ValueError("All fields are required")
    
    if not validate_phone_number(phone):
        raise ValueError("Invalid phone number format")
    
    if credits < 0:
        raise ValueError("Credits cannot be negative")

    if phone in st.session_state.df_current["Phone_Numbers"].values:
        raise ValueError("Phone number already exists")

    new_client = pd.DataFrame({
        "Clients": [name],
        "Phone_Numbers": [phone],
        "Credits": [credits],
        "Last_Updated": [datetime.now()],
        "Status": [status]
    })
    st.session_state.df_current = pd.concat([st.session_state.df_current, new_client], ignore_index=True)
    return st.session_state.df_current

def delete_client(name=None, phone=None):
    """Delete a client from the database with validation"""
    global df
    if "Clients" not in df.columns or "Phone_Numbers" not in df.columns:
        raise ValueError("Required columns don't exist in the dataset.")
    
    save_state_to_cache() 
    
    
    if not name and not phone:
        raise ValueError("Either name or phone number must be provided")
    
    
    if name:
        if name not in st.session_state.df_current["Clients"].values:
            raise ValueError(f"Client '{name}' not found")
        st.session_state.df_current = st.session_state.df_current[st.session_state.df_current["Clients"] != name]
    elif phone:
        if not validate_phone_number(phone):
            raise ValueError("Invalid phone number format")
        if phone not in st.session_state.df_current["Phone_Numbers"].values:
            raise ValueError(f"Phone number '{phone}' not found")
        st.session_state.df_current = st.session_state.df_current[st.session_state.df_current["Phone_Numbers"] != phone]

def search_clients(search_query):
    """Search for clients with improved functionality"""
    if "Clients" not in df.columns:
        raise ValueError("Required columns don't exist in the dataset.")
    
    if not search_query:
        return pd.DataFrame()

    search_query = search_query.lower()
    
    mask = (
        df["Clients"].astype(str).str.lower().str.contains(search_query, na=False) |
        df["Phone_Numbers"].astype(str).str.contains(search_query, na=False) |
        df["Notes"].astype(str).str.lower().str.contains(search_query, na=False) |
        df.index.astype(str).str.contains(search_query, na=False)
    )
    
    return df[mask]


def modify_credits(client_index, amount, operation):
    """Modify client credits with validation"""
    save_state_to_cache()  
 
    if amount <= 0:
        raise ValueError("Amount must be greater than 0")
    
    current_credits = st.session_state.df_current.loc[client_index, "Credits"]
    
    if operation == "add":
        st.session_state.df_current.loc[client_index, "Credits"] += amount
    elif operation == "subtract":
        if amount > current_credits:
            raise ValueError("Cannot subtract more than available credits")
        st.session_state.df_current.loc[client_index, "Credits"] -= amount
    st.session_state.df_current.loc[client_index, "Last_Updated"] = datetime.now()
    
    return st.session_state.df_current.loc[client_index, "Credits"]

def update_client_status(client_index, new_status):
    """Update client status"""
    save_state_to_cache()
    st.session_state.df_current.loc[client_index, "Status"] = new_status
    st.session_state.df_current.loc[client_index, "Last_Updated"] = datetime.now()


def modify_page():
    df = st.session_state.df_current

    if df.empty or "Clients" not in df.columns or "Credits" not in df.columns:
        st.sidebar.error("No data available.")
        return

    df["Credits"] = pd.to_numeric(df["Credits"], errors="coerce").fillna(0).astype(float).round(2)


    client_names = df["Clients"].tolist()
    

    if not client_names:
        st.sidebar.error("No clients available.")
        return
    
    
    selected_client = st.sidebar.selectbox("Choose a client", client_names)


    client_row = df[df["Clients"] == selected_client]
    if client_row.empty:
        st.sidebar.error("Client not found.")
        return

   
    client_index = client_row.index[0]
    current_credits = df.loc[client_index, "Credits"]

    st.sidebar.write(f"Client name: {selected_client}")
    st.sidebar.write(f"Current credits: {round(current_credits, 2)}")

    
    operation = st.sidebar.radio("Operation", ["Add", "Subtract"])
    amount = st.sidebar.number_input("Amount", min_value=0.0, value=0.0, step=0.01)

    if st.sidebar.button("Update Credits"):
        if operation == "Add":
            updated_credits = modify_credits(client_index, amount, "add")
            st.sidebar.success(f"Credits added: {round(amount, 2)}")
        elif operation == "Subtract":
            if amount > current_credits:
                st.sidebar.error("Cannot subtract more than available credits.")
                return
            updated_credits = modify_credits(client_index, amount, "subtract")
            st.sidebar.warning(f"Credits subtracted: {round(amount, 2)}")

        
        st.sidebar.write(f"New credit balance: {round(updated_credits, 2)}")


# -=================================== Streamlit Dashboard ===================================-
#== Title ==-
st.markdown(
    '''
    <h1 style="background-image: linear-gradient(to right, #4F959D, #98D2C0); 
             -webkit-background-clip: text; 
             color: transparent; 
             margin: 20px 0;">
        Client Credits Manager
    </h1>
    ''', 
    unsafe_allow_html=True
)
#========== Buttons And Functionality ==========-
col1, col2, col3 = st.columns([1,1,1])
st.markdown(
    """
    <style>
    .stButton {
        display: flex;
        gap: 0px;
        justify-content: center;
        align-items: center;
        
    }
    .stButton button {
        padding: 10px 30px;  
        
    }
    </style>
    """,
    unsafe_allow_html=True
)


with col1:
    if st.button("Save Changes"):
        save_changes_to_file()
        st.success("Changes saved to database!")
        time.sleep(1)
        st.rerun()

with col2:
    if st.button("Undo"):
        if undo_changes():
            df = st.session_state.df_current
            st.success("Last change undone!")
        else:
            st.warning("Nothing to undo!")


with col3:
    if st.button("Create Backup"):
        backup_file = create_backup()
        st.success(f"Backup created: {os.path.basename(backup_file)}")

st.markdown('<div>', unsafe_allow_html=True)

#== Database Statictics ==-
show_statistics()

#=================== Pages ===================-

if "page" not in st.session_state:
    st.session_state["page"] = "search"

navigation_bar = st.sidebar.selectbox(
    "Navigation",
    [
        "Dashboard",
        "Update Database",
        "Add Client",
        "Delete Client",
        "Search Client",
        "Backup & Restore",
        "Settings"
    ],
)

if navigation_bar == "Dashboard":
    st.session_state["page"] = "dashboard"
    low_credit_clients_show_up_df()
    st.markdown(
    '''
    <h2 style="background-image: linear-gradient(to left, #FFF0BD, #FDAB9E); 
             -webkit-background-clip: text; 
             color: transparent; 
             margin: 20px 0;">
        Recent Activity
    </h2>
    ''', 
    unsafe_allow_html=True
    )
    if "Last_Updated" in st.session_state.df_current.columns:
        recent_activity = st.session_state.df_current.sort_values("Last_Updated", ascending=False).head(5)
        st.dataframe(recent_activity, width=1000)
    

elif navigation_bar == "Update Database":
    st.session_state["page"] = "update"
    modify_page()
    

elif navigation_bar == "Add Client":
    st.session_state["page"] = "add"
    st.sidebar.header("Add New Client")
    
    with st.sidebar.form("add_client_form"):
        client_name = st.text_input(
            "Client Name", 
            placeholder="Enter client name here",
            help="Enter the full name of the client"
        )
        phone = st.text_input(
            "Phone Number", 
            placeholder="Enter phone number",
            help="Enter a valid phone number (9-15 digits)"
        )
        credits = st.number_input(
            "Initial Credits",
            min_value=0.0,
            value=0.0,
            step=0.10,
            help="Enter the initial credit amount"
        )
        status = st.selectbox(
            "Status",
            ["Active", "Inactive", "Pending", "Blocked"],
            help="Select the client's status"
        )
      
        submitted = st.form_submit_button("Add Client")
        
        if submitted:
            if not client_name or not phone or credits is None:
                st.error("Please fill in all required fields.")
            elif not validate_phone_number(phone):
                st.error("Please enter a valid phone number.")
            else:
                try:
                    add_client(client_name, phone, credits, status)
                    st.success(f"Client added: {client_name}, Phone: {phone}, Credits: ${credits:,.2f}")
                except Exception as e:
                    st.error(f"Error adding client: {str(e)}")

elif navigation_bar == "Delete Client":
    st.session_state["page"] = "delete"
    st.sidebar.header("Delete Client")
    
    with st.sidebar.form("delete_client_form"):
        choice_delete_option = st.radio(
            "Choose deletion method", 
            ["Phone Number", "Client Name"],
            help="Select how you want to identify the client to delete"
        )

        if choice_delete_option == "Client Name":
            client_name = st.text_input(
                "Client Name", 
                placeholder="Enter client name here"
            )
            phone = None
        else:
            phone = st.text_input(
                "Phone Number", 
                placeholder="Enter phone number"
            )
            client_name = None

        submitted = st.form_submit_button("Delete Client")
        
        if submitted:
            if not client_name and not phone:
                st.error("Please provide either client name or phone number.")
            else:
                try:
                    delete_client(name=client_name, phone=phone)
                    st.success(f"Client deleted: {client_name if client_name else phone}")
                except Exception as e:
                    st.error(f"Error deleting client: {str(e)}")

elif navigation_bar == "Search Client":
    st.session_state["page"] = "search"
    st.sidebar.header("Search Client")
    
    with st.sidebar.form("search_form"):
        search_query = st.text_input(
            "🔍 Search by Name, Phone, or Notes:", 
            placeholder="Enter search term",
            help="Search for clients by name, phone number, or notes"
        )
        submitted = st.form_submit_button("Search")
        
        if submitted:
            result = search_clients(search_query)
            if isinstance(result, pd.DataFrame) and not result.empty:
                st.success(f"Found {len(result)} client(s)")
                st.session_state.filtered_view = result
            else:
                st.warning("No clients found.")
                st.session_state.filtered_view = pd.DataFrame(columns=df.columns)

elif navigation_bar == "Backup & Restore":
    st.session_state["page"] = "backup"
    st.markdown(
    '''
    <h2 style="background-image: linear-gradient(to left, #FFF0BD, #FDAB9E); 
             -webkit-background-clip: text; 
             color: transparent; 
             margin: 20px 0;">
        Backup & Restore
    </h2>
    ''', 
    unsafe_allow_html=True
    )

    st.markdown(
    '''
    <h3 style="background-image: linear-gradient(to left, #D17D98, #B3D8A8); 
             -webkit-background-clip: text; 
             color: transparent; 
             margin: 20px 0;">
        Create Backup
    </h3>
    ''', 
    unsafe_allow_html=True
    )
    
    if st.button("Create New Backup"):
        backup_file = create_backup()
        if backup_file:
            st.success(f"Backup created successfully: {os.path.basename(backup_file)}")
    
    
    st.markdown(
    '''
    <h3 style="background-image: linear-gradient(to left, #D17D98, #B3D8A8); 
             -webkit-background-clip: text; 
             color: transparent; 
             margin: 20px 0;">
        Available Backups
    </h3>
    ''', 
    unsafe_allow_html=True
    )
    backups = []
    for ext in ['.csv']:
        backups.extend([f for f in os.listdir(st.session_state.backup_path) if f.endswith(ext)])
    
    if backups:
        backup_files = sorted(backups, reverse=True)
        selected_backup = st.selectbox(
            "Select a backup to restore",
            backup_files,
            help="Choose a backup file to restore from"
        )
        
       
        backup_path = os.path.join(st.session_state.backup_path, selected_backup)
        backup_time = datetime.fromtimestamp(os.path.getmtime(backup_path))
        st.info(f"Backup created on: {backup_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        if st.button("Restore Selected Backup"):
            if restore_backup(backup_path):
                st.success(f"Successfully restored backup: {selected_backup}")
                time.sleep(1)
                st.rerun()
    else:
        st.info("No backup files found.")

elif navigation_bar == "Settings":
    st.session_state["page"] = "settings"
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
    
    with st.form("settings_form"):
        st.markdown(
    '''
    <h3 style="background-image: linear-gradient(to left, #D17D98, #B3D8A8); 
             -webkit-background-clip: text; 
             color: transparent; 
             margin: 20px 0;">
        General Settings
    </h3>
    ''', 
    unsafe_allow_html=True
    )
        st.session_state.settings["auto_backup"] = st.checkbox(
            "Enable Auto Backup",
            value=st.session_state.settings["auto_backup"],
            help="Automatically create backups at regular intervals"
        )
        
        if st.session_state.settings["auto_backup"]:
            st.session_state.settings["backup_interval"] = st.number_input(
                "Backup Interval (minutes)",
                min_value=5,
                max_value=1440,
                value=st.session_state.settings["backup_interval"],
                help="How often to create automatic backups"
            )
        
        st.session_state.settings["low_credit_threshold"] = st.number_input(
            "Low Credit Threshold ($)",
            min_value=0,
            value=st.session_state.settings["low_credit_threshold"],
            help="Amount below which a client is considered to have low credits"
        )
        
        st.session_state.settings["notification_enabled"] = st.checkbox(
            "Enable Notifications",
            value=st.session_state.settings["notification_enabled"],
            help="Show notifications for important events"
        )
        

        submitted = st.form_submit_button("Save Settings")
        if submitted:
            st.success("Settings saved successfully!")



Show_up_client_Database()

if st.session_state.changes_made and should_show_warning():
    elapsed = (datetime.now() - st.session_state.last_warning_time).total_seconds()
    remaining = max(0, st.session_state.warning_duration - elapsed)
    
    st.sidebar.warning(f"⚠️ Remember to save your changes! ({int(remaining)}s)")
    if st.sidebar.button("Save Now"):
        save_changes_to_file()
        st.sidebar.success("Changes saved!")
        time.sleep(1)
        st.rerun()