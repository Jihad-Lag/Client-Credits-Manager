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
import subprocess
from documentation_page import show_documentation


# -===== Settings Manager =====-
def load_settings():
    settings_path = Path("./database/settings.json")
    default_settings = {
        "auto_backup": True,
        "backup_interval": 30,
        "low_credit_threshold": 100,
        "notification_enabled": True,
        "last_backup_time": None
    }
    
    try:
        if settings_path.exists():
            with open(settings_path, 'r') as f:
                saved_settings = json.load(f)
                return {**default_settings, **saved_settings}
        return default_settings
    except Exception as e:
        st.error(f"Error loading settings: {str(e)}")
        return default_settings

def save_settings(settings):
    settings_path = Path("./database/settings.json")
    try:
        settings_path.parent.mkdir(exist_ok=True)
        with open(settings_path, 'w') as f:
            json.dump(settings, f, indent=4)
        return True
    except Exception as e:
        st.error(f"Error saving settings: {str(e)}")
        return False

# -===== Configuration Page =====-
st.set_page_config(
    page_title="Client Credits Manager",
    page_icon="💶",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -===== Dataset =====-
dataset_path = "./database/clients_data.csv"
database_dir = os.path.dirname(dataset_path)
if not os.path.exists(database_dir):
    os.makedirs(database_dir)

# -===== Configuration : ( Cache - Settings - Reading Dataset - Warning Time ) =====-
if "df_cache" not in st.session_state:
    st.session_state.df_cache = [] 
if "df_current" not in st.session_state:
    try:
        dataset = pd.read_csv(dataset_path, index_col=0)
        st.session_state.df_current = dataset.copy()
    except FileNotFoundError:
        st.session_state.df_current = pd.DataFrame(columns=["Clients", "Phone_Numbers", "Credits", "Last_Updated","Status"])
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
if "phone_update_history" not in st.session_state:
    st.session_state.phone_update_history = []
if "settings" not in st.session_state:
    st.session_state.settings = load_settings()
df = st.session_state.df_current

# -===== Functions : ( Save - Change - Restore & Create Backup - Warning Time & Show - Json Message - Historic Whatsapp Sender) =====-

def validate_phone_number(phone):
    """Validate phone number format and ensure it has country code"""
    try:
       
        phone = str(phone)
        phone = re.sub(r'[^\d+]', '', phone)

        if not phone.startswith('+'):
            phone = '+' + phone

        phone = re.sub(r'^\+0+', '+', phone)

        if len(phone) < 10: 
            return False, phone

        pattern = re.compile(r'^\+\d{9,15}$')
        if not pattern.match(phone):
            return False, phone
            
        return True, phone
    except Exception as e:
        return False, str(phone)

def format_phone_number(phone):
    """Format phone number for display"""
    try:

        phone = str(phone)
        digits = re.sub(r'\D', '', phone)

        if not phone.startswith('+'):
            digits = '+' + digits

        formatted = re.sub(r'(\+\d{1,3})(\d{3})(\d{3})(\d+)', r'\1 \2 \3 \4', digits)
        return formatted
    except:
        return str(phone)

def json_message_add_amount(name_client, number_phone_client, amount_credits, updated_credit):
    try:
        json_path = Path("./database/contact.json")
        json_path.parent.mkdir(exist_ok=True)

        if json_path.exists() and json_path.stat().st_size > 0:  
            try:
                data = json.loads(json_path.read_text(encoding='utf-8'))
            except json.JSONDecodeError:
                data = {}  
        else:
            data = {}

        client_number = len(data) + 1
        client_key = f"client_{client_number}"

        data[client_key] = {
            "number_phone": str(number_phone_client).replace(" ", ""),
            "message": f"Dear Mr./Mrs. {name_client.strip()},\nWe inform you that your credit has been updated. An amount of {round(amount_credits,2)} was added, raising your current total to {round(updated_credit,2)}.\nPlease note this adjustment and respect agreed deadlines.\nFor any questions, feel free to contact us.\nDate & Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n",
        }

        tmp_path = json_path.with_suffix('.tmp')
        tmp_path.write_text(json.dumps(data, indent=4, ensure_ascii=False), encoding='utf-8')
        tmp_path.replace(json_path)

        st.sidebar.success(f"✅ Added {name_client.strip()} to the JSON Contacts: Historic Whatsapp Sender")
        return True

    except ValueError as ve:
        st.error(f"Validation Error: {ve}")
    except PermissionError:
        st.error("Permission denied: Cannot access file")
    except Exception as e:
        st.error(f"Unexpected error: {str(e)}")
        if 'tmp_path' in locals() and tmp_path.exists():
            tmp_path.unlink()
    return False

def json_message_sub_amount(name_client, number_phone_client, amount_credits, updated_credit):
    try:
        json_path = Path("./database/contact.json")
        json_path.parent.mkdir(exist_ok=True)

        if json_path.exists() and json_path.stat().st_size > 0:  
            try:
                data = json.loads(json_path.read_text(encoding='utf-8'))
            except json.JSONDecodeError:
                data = {}  
        else:
            data = {}

        client_number = len(data) + 1
        client_key = f"client_{client_number}"

        data[client_key] = {
            "number_phone": str(number_phone_client).replace(" ", ""),
            "message": f"Dear Mr./Mrs. {name_client.strip()},\nYour credit has been updated. An amount of {round(amount_credits,2)} was deducted, reducing your current total to {round(updated_credit,2)}.\nPlease review this adjustment and ensure compliance with agreed terms.\nContact us with any questions.\nDate & Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n",
        }

        tmp_path = json_path.with_suffix('.tmp')
        tmp_path.write_text(json.dumps(data, indent=4, ensure_ascii=False), encoding='utf-8')
        tmp_path.replace(json_path)

        st.sidebar.success(f"✅ Added {name_client.strip()} to the JSON Contacts: Historic Whatsapp Sender")
        return True

    except ValueError as ve:
        st.error(f"Validation Error: {ve}")
    except PermissionError:
        st.error("Permission denied: Cannot access file")
    except Exception as e:
        st.error(f"Unexpected error: {str(e)}")
        if 'tmp_path' in locals() and tmp_path.exists():
            tmp_path.unlink()
    return False

def json_message_welcome(name_client, number_phone_client, amount_credits):
    try:
        json_path = Path("./database/contact.json")
        json_path.parent.mkdir(exist_ok=True)

        if json_path.exists() and json_path.stat().st_size > 0:  
            try:
                data = json.loads(json_path.read_text(encoding='utf-8'))
            except json.JSONDecodeError:
                data = {}  
        else:
            data = {}

        client_number = len(data) + 1
        client_key = f"client_{client_number}"

        data[client_key] = {
            "number_phone": str(number_phone_client).replace(" ", ""),
            "message": f"Dear {name_client.strip()},\nWelcome to our credit system! Your account is now active with an initial credit of {round(amount_credits,2)}.\nYou can start using your credits immediately. For any assistance, contact our support team.\nDate & Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n",
        }

        tmp_path = json_path.with_suffix('.tmp')
        tmp_path.write_text(json.dumps(data, indent=4, ensure_ascii=False), encoding='utf-8')
        tmp_path.replace(json_path)

        st.sidebar.success(f"✅ Added {name_client.strip()} to the JSON Contacts: Historic Whatsapp Sender")
        return True

    except ValueError as ve:
        st.error(f"Validation Error: {ve}")
    except PermissionError:
        st.error("Permission denied: Cannot access file")
    except Exception as e:
        st.error(f"Unexpected error: {str(e)}")
        if 'tmp_path' in locals() and tmp_path.exists():
            tmp_path.unlink()
    return False

def whatsapp_messaging_system():
    st.markdown(
    '''
    <h2 style="background-image: linear-gradient(to left, #FFF0BD, #FDAB9E); 
             -webkit-background-clip: text; 
             color: transparent; 
             margin: 10px 0;">
        Run WhatsApp Sender
    </h2>
    ''', 
    unsafe_allow_html=True
    )
    with st.expander("📖 Detailed Instructions for Instructors"):
        st.markdown(
    '''
    <style>
    
    .instructor-tip {
        background-color: #1A1A1A;
        border-left: 4px solid #4CAF50;
        color: white;
        padding: 10px;
        margin: 10px 0;
    }
    
    /* Code Block Styling */
    .stCodeBlock {
        background-color: #2C2C2C !important;
        color: #E0E0E0 !important;
    }
    
    /* Text and Markdown Styling */
    .stMarkdown, .stText {
        color: white !important;
    }

    /* Expander Styling */
    .stExpander {
        background-color: #1A1A1A !important;
        color: white !important;
    }
    </style>
    ''', 
    unsafe_allow_html=True
    )
        st.subheader("📚 Instructor Guide")
        st.markdown('<div class="instructor-tip"><strong>💡 Multiple Ways to Open Command Prompt</strong></div>', unsafe_allow_html=True)
        methods = [
        "1- Press `Win + R`, type `cmd`, and press `Enter`.",
        "2- Search `cmd` in the Windows Start Menu and click it.",
        "3- Press `Shift + Right Click` inside a folder and select `Open PowerShell/Command Prompt here`.",
        "4- In File Explorer, type `cmd` in the address bar and press `Enter`.",
        "5- Use Task Manager: Press `Ctrl + Shift + Esc`, go to `File` > `Run new task`, and type `cmd`."
         ]  

        for method in methods:
          st.write(method)
    
    
        st.markdown('<div class="instructor-tip"><strong>🛠️ Troubleshooting Tips for Students</strong></div>', unsafe_allow_html=True)
        troubleshooting_tips = [
        "Ensure Python is installed and added to system PATH.",
        "Verify the script location is correct.",
        "Check for any required dependencies before running.",
        "Run as administrator if permission issues occur."
        ]
    
        for tip in troubleshooting_tips:
         st.write(f"- {tip}")

    

    st.markdown(
    '''
    <h2 style="background-image: linear-gradient(to left, #D17D98, #B3D8A8); 
             -webkit-background-clip: text; 
             color: transparent; 
             margin: 20px 0;">
        Activate Tableau WhatsApp Sender
    </h2>
    ''', 
    unsafe_allow_html=True
    )
    cmd_command = "start cmd /k \"for /r %i in (whatsapp_sender_bot_dashboard.py) do @if exist \"%i\" python \"%i\"\""
    st.code(cmd_command, language="cmd")

    
    st.write("✅ Run the above command and wait. The script will execute automatically without requiring keyboard input or closing tabs.")

    if st.button("Run Command Automatically"):
       message_container = st.empty()
       message_container.info("Verify the Whatssap Sender script that is running on your CMD")

       with st.spinner("Launching WhatsApp sender..."):
            
            try:
                
                result = subprocess.run(
                    cmd_command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
                
                if result.returncode == 0:
                    time.sleep(0.5)
                    message_container.empty()
                    st.success("✅ WhatsApp Sender launched successfully!")
                    
                else:
                    st.error("❌ Failed to launch WhatsApp Sender")
                    with st.expander("Error Details", expanded=True):
                        st.code(result.stderr if result.stderr else "No error output", language="text")
                    
            except subprocess.CalledProcessError as e:
                st.error(f"Command failed with error: {e.returncode}")
                st.code(e.stderr, language="text")
            except Exception as e:
                st.error(f"Unexpected error: {str(e)}")
                st.warning("Please ensure:"
                           "\n1. Python is in your system PATH"
                           "\n2. The script exists in your directory structure"
                           "\n3. No antivirus is blocking the operation")





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
    df_copy = st.session_state.df_current.copy()
    if "Last_Updated" in df_copy.columns:
        df_copy["Last_Updated"] = pd.to_datetime(df_copy["Last_Updated"])
    st.session_state.df_cache.append(df_copy)
    st.session_state.changes_made = True
    reset_warning_timer() 



def save_changes_to_file():
    
    df_to_save = st.session_state.df_current.copy()
    if "Last_Updated" in df_to_save.columns:
        df_to_save["Last_Updated"] = pd.to_datetime(df_to_save["Last_Updated"])
    df_to_save.to_csv(dataset_path, index=True)
    st.session_state.changes_made = False
    st.session_state.df_cache = [] 
    st.sidebar.success("✅ Changes saved!")

def create_backup():
    """Create a backup of the current database with improved error handling"""
    try:
        if not os.path.exists(st.session_state.backup_path):
            os.makedirs(st.session_state.backup_path)
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = os.path.join(st.session_state.backup_path, f"backup_{timestamp}.csv")
    
        st.session_state.df_current.to_csv(backup_file, index=True)
        
        st.session_state.settings["last_backup_time"] = datetime.now().isoformat()
        save_settings(st.session_state.settings)
        
        
        
        cleanup_old_backups()
        
        return backup_file
    except Exception as e:
        st.error(f"Error creating backup: {str(e)}")
        return None
    
        

def cleanup_old_backups():
    """Keep only the 10 most recent backups"""
    try:
        backups = []
        for ext in ['.csv']:
            backups.extend([os.path.join(st.session_state.backup_path, f) 
                          for f in os.listdir(st.session_state.backup_path) 
                          if f.endswith(ext)])
        
        if len(backups) > 20:
            sorted_backups = sorted(backups, key=os.path.getctime)
            for old_backup in sorted_backups[:-20]:
                os.remove(old_backup)
    except Exception as e:
        st.warning(f"Error cleaning old backups: {str(e)}")

def restore_backup(backup_file):
    """Restore from a backup file with improved error handling"""
    try:
        if not os.path.exists(backup_file):
            raise FileNotFoundError(f"Backup file not found: {backup_file}")
        
        pre_restore_backup = create_backup()
        if pre_restore_backup:
            st.info("Created safety backup before restore")
        
        if backup_file.endswith('.csv'):
            backup_df = pd.read_csv(backup_file, index_col=0)
            
            if 'Last_Updated' in backup_df.columns:
                backup_df['Last_Updated'] = pd.to_datetime(backup_df['Last_Updated'], format='mixed')
        elif backup_file.endswith('.json'):
            backup_df = pd.read_json(backup_file)
            
            if 'Last_Updated' in backup_df.columns:
                backup_df['Last_Updated'] = pd.to_datetime(backup_df['Last_Updated'], format='mixed')
        else:
            raise ValueError("Unsupported backup file format")
        
        required_columns = ["Clients", "Phone_Numbers", "Credits", "Last_Updated","Status"]
        if not all(col in backup_df.columns for col in required_columns):
            raise ValueError("Backup file is missing required columns")
        
        st.session_state.df_current = backup_df.copy()
        st.session_state.changes_made = True
        
        save_changes_to_file()
        
        return True
    except Exception as e:
        st.error(f"Error restoring backup: {str(e)}")
        return False

def check_auto_backup():
    """Check if automatic backup is needed"""
    if not st.session_state.settings["auto_backup"]:
        return
        
    last_backup_time = st.session_state.settings.get("last_backup_time")
    if last_backup_time:
        last_backup = datetime.fromisoformat(last_backup_time)
        time_since_backup = (datetime.now() - last_backup).total_seconds() / 60
        
        if time_since_backup >= st.session_state.settings["backup_interval"]:
            backup_file = create_backup()
            if backup_file:
                st.sidebar.success("Auto-backup created successfully")

def manage_contact_queue():
    """Manage the WhatsApp message queue"""
    json_path = Path("./database/contact.json")
    
    try:
        if json_path.exists() and json_path.stat().st_size > 0:
            with open(json_path, 'r', encoding='utf-8') as f:
                clients = json.load(f)
                
            if clients:
                st.markdown(
                '''
                <h3 style="background-image: linear-gradient(to left, #D17D98, #B3D8A8); 
                         -webkit-background-clip: text; 
                         color: transparent; 
                         margin: 20px 0;">
                    Message Queue
                </h3>
                ''', 
                unsafe_allow_html=True
                )

                queue_df = pd.DataFrame([
                    {
                        "Phone": data["number_phone"],
                        "Message Preview": data["message"][:50] + "..."
                    }
                    for data in clients.values()
                ])
                
                st.dataframe(queue_df, width=1000)
                
                
                if st.button("Clear Queue"):
                    with open(json_path, 'w', encoding='utf-8') as f:
                        json.dump({}, f)
                        st.success("Queue cleared successfully!")
                        time.sleep(1)
                        st.rerun()
        
    except Exception as e:
        st.error(f"Error managing message queue: {str(e)}")

# -===== Functions : ( Verification Number Phone - Show Up Database - Statistics Columns - Check Low & Database Credits) =====-

def Show_up_client_Database():
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
            if "Last_Updated" in df_display.columns:
                df_display["Last_Updated"] = pd.to_datetime(df_display["Last_Updated"]).dt.strftime('%Y-%m-%d %H:%M:%S')
            if "Phone_Numbers" in df_display.columns:
                df_display["Phone_Numbers"] = df_display["Phone_Numbers"].apply(format_phone_number)
            st.dataframe(df_display, width=1000, hide_index=True)
        else:
            st.info("No clients in the database. Add clients using the sidebar.")
    else:
        st.info("No clients in the database. Add clients using the sidebar.")

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
    
    
def low_credit_clients_show_up_df():
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
        display_df = low_credit_clients[["Clients", "Phone_Numbers", "Credits"]].copy()
        display_df["Phone_Numbers"] = display_df["Phone_Numbers"].apply(format_phone_number)
        display_df["Credits"] = display_df["Credits"].apply(lambda x: f"${float(x):,.2f}")
        st.dataframe(display_df, width=1000)


def check_low_credits():
    """Check for clients with low credits"""
    low_credit_clients = st.session_state.df_current[
        st.session_state.df_current["Credits"] < st.session_state.settings["low_credit_threshold"]
    ]
    if not low_credit_clients.empty:
        st.warning(f"⚠️ {len(low_credit_clients)} clients have low credits (below ${st.session_state.settings['low_credit_threshold']})")
        return low_credit_clients
    return None


# -===== Features : ( [ Add - Delete - Search - Update - Change Number Client ] Clients ) =====-

def add_client(name, phone, credits, status="Active"):
    """Add a new client to the database with validation"""
    save_state_to_cache()
    
    if not name or not phone or credits is None:
        raise ValueError("All fields are required")
    
    is_valid, formatted_phone = validate_phone_number(phone)
    if not is_valid:
        raise ValueError(f"Invalid phone number format: {phone}. Please use format: +1234567890")
    
    if credits < 0:
        raise ValueError("Credits cannot be negative")

    if formatted_phone in st.session_state.df_current["Phone_Numbers"].values:
        raise ValueError("Phone number already exists")

    new_client = pd.DataFrame({
        "Clients": [name],
        "Phone_Numbers": [formatted_phone],
        "Credits": [credits],
        "Last_Updated": [datetime.now()],
        "Status": [status]
    })
    
    # Add the new client to the current DataFrame
    st.session_state.df_current = pd.concat([st.session_state.df_current, new_client], ignore_index=True)
    
    # Send welcome message
    json_message_welcome(name_client=name, number_phone_client=formatted_phone, amount_credits=credits)
    
    return st.session_state.df_current



def delete_client(name=None, phone=None):
    """Delete a client from the database with validation"""
    if "df_current" not in st.session_state:
        raise ValueError("Dataset not initialized in session state")
    
    df = st.session_state.df_current
    
    required_columns = {"Clients", "Phone_Numbers"}
    if not required_columns.issubset(df.columns):
        missing = required_columns - set(df.columns)
        raise ValueError(f"Missing required columns: {', '.join(missing)}")
    
    if not name and not phone:
        raise ValueError("Must provide either name or phone number")
    if name and phone:
        raise ValueError("Provide only one identifier (name OR phone)")
    
    name = str(name).strip().lower() if name else None
    phone = str(phone).strip() if phone else None
    
    clean_names = df["Clients"].str.strip().str.lower().dropna()
    clean_phones = df["Phone_Numbers"].astype(str).str.strip().dropna()
    
    try:
        if name:
            if name not in clean_names.values:
                raise ValueError(f"Client '{name}' not found")
            mask = clean_names != name
            st.session_state.df_current = df[mask]
            
        elif phone:
            if not validate_phone_number(phone)[0]:
                raise ValueError(f"Invalid phone format: {phone}")
            if phone not in clean_phones.values:
                raise ValueError(f"Phone '{phone}' not found")
            mask = clean_phones != phone
            st.session_state.df_current = df[mask]
        
        save_state_to_cache()
        return True
    
    except Exception as e:
        st.error(f"Error deleting client: {str(e)}")
        return False

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
        df.index.astype(str).str.contains(search_query, na=False)
    )
    
    return df[mask]

def update_client_phone(name=None, current_phone=None, new_phone=None):
    """Update client's phone number with validation"""
    
    if "df_current" not in st.session_state:
        raise ValueError("Dataset not initialized in session state")
    
    df = st.session_state.df_current
    
    required_columns = {"Clients", "Phone_Numbers"}
    if not required_columns.issubset(df.columns):
        missing = required_columns - set(df.columns)
        raise ValueError(f"Missing columns: {', '.join(missing)}")
    
    if not name and not current_phone:
        raise ValueError("Must provide name or current phone")
    if name and current_phone:
        raise ValueError("Provide only one identifier (name OR current_phone)")
    
    is_valid, formatted_new_phone = validate_phone_number(new_phone)
    if not is_valid:
        raise ValueError(f"Invalid new phone format: {new_phone}. Please use format: +1234567890")
    
    try:
        name = str(name).strip().lower() if name else None
        current_phone = str(current_phone).strip() if current_phone else None
        
        clean_names = df["Clients"].str.strip().str.lower()
        clean_phones = df["Phone_Numbers"].astype(str).str.strip()
        
        if name:
            if name not in clean_names.values:
                raise ValueError(f"Client '{name}' not found")
            mask = clean_names == name
        else:
            if current_phone not in clean_phones.values:
                raise ValueError(f"Phone '{current_phone}' not found")
            mask = clean_phones == current_phone
        
        if mask.any():
            if formatted_new_phone in clean_phones.values:
                raise ValueError("New phone number already exists in database")
            
            old_phone = df.loc[mask, "Phone_Numbers"].iloc[0]
            client_name = df.loc[mask, "Clients"].iloc[0]
            
            df.loc[mask, "Phone_Numbers"] = formatted_new_phone
            df.loc[mask, "Last_Updated"] = datetime.now()
            st.session_state.df_current = df
            
            if 'phone_update_history' not in st.session_state:
                st.session_state.phone_update_history = []
            
            st.session_state.phone_update_history.append({
                'timestamp': datetime.now(),
                'client_name': client_name,
                'old_phone': old_phone,
                'new_phone': formatted_new_phone
            })
            
            if len(st.session_state.phone_update_history) > 100:
                st.session_state.phone_update_history = st.session_state.phone_update_history[-100:]
            
            save_state_to_cache()
            return True
        
        raise ValueError("No matching client found")
    
    except Exception as e:
        st.error(f"Update failed: {str(e)}")
        return False


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
    number_phone_client = df.loc[client_index, "Phone_Numbers"]

    st.sidebar.write(f"Client name: {selected_client}")
    st.sidebar.write(f"Current credits: {round(current_credits, 2)}")

    
    operation = st.sidebar.radio("Operation", ["Add", "Subtract"])
    amount = st.sidebar.number_input("Amount", min_value=0.0, value=0.0, step=0.1)

    if st.sidebar.button("Update Credits"):
        if operation == "Add":
            updated_credits = modify_credits(client_index, amount, "add")
            st.sidebar.success(f"Credits added: {round(amount, 2)}")
            json_message_add_amount(name_client=selected_client,number_phone_client=number_phone_client,amount_credits=amount,updated_credit=updated_credits)
            save_changes_to_file()
            time.sleep(10)
            st.rerun()

        elif operation == "Subtract":
            if amount > current_credits:
                st.sidebar.error("Cannot subtract more than available credits.")

                return
            updated_credits = modify_credits(client_index, amount, "subtract")
            st.sidebar.warning(f"Credits subtracted: {round(amount, 2)}")
            json_message_sub_amount(name_client=selected_client,number_phone_client=number_phone_client,amount_credits=amount,updated_credit=updated_credits)
            save_changes_to_file()
            time.sleep(5)
            st.rerun()
        
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
        "Run WhatsApp Sender",
        "Update Database",
        "Add Client",
        "Delete Client",
        "Update Phone",
        "Backup & Restore",
        "Documentation",
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
        try:
            recent_activity = st.session_state.df_current.copy()
            recent_activity["Last_Updated"] = pd.to_datetime(recent_activity["Last_Updated"])
            recent_activity = recent_activity.sort_values("Last_Updated", ascending=False).head(5)
            
            if not recent_activity.empty:
                display_df = recent_activity.copy()
                display_df["Last_Updated"] = display_df["Last_Updated"].dt.strftime('%Y-%m-%d %H:%M:%S')
                display_df["Credits"] = display_df["Credits"].apply(lambda x: f"${float(x):,.2f}")
                display_df["Phone_Numbers"] = display_df["Phone_Numbers"].apply(format_phone_number)
                
                st.dataframe(
                    display_df,
                    column_config={
                        "Last_Updated": "Date/Time",
                        "Clients": "Client Name",
                        "Phone_Numbers": "Phone Number",
                        "Credits": "Credits",
                        "Status": "Status"
                    },
                    width=1000,
                    hide_index=True
                )
            else:
                st.info("No recent activity data available")
        except Exception as e:
            st.error(f"Error displaying recent activity: {str(e)}")
    else:
        st.warning("No recent activity data available")

    

elif navigation_bar == "Update Database":
    st.session_state["page"] = "update"
    modify_page()

elif navigation_bar == "Run WhatsApp Sender":
    st.session_state["page"] = "whatsapp sender"
    whatsapp_messaging_system()

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
                    save_changes_to_file()
                    time.sleep(2)
                    st.rerun()
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
                    save_changes_to_file()
                    time.sleep(2)
                    st.rerun()
                except Exception as e:
                    st.error(f"Error deleting client: {str(e)}")



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
            save_settings(st.session_state.settings)
            st.rerun()

elif navigation_bar == "Update Phone":
    st.session_state["page"] = "update_phone"
    st.sidebar.header("Update Client Phone Number")
    
    with st.sidebar.form("update_phone_form"):
        st.markdown("""
            <div style='background-color: #000000; color: #ffffff; padding: 15px; border-radius: 5px; margin-bottom: 15px;'>
                <p style='margin: 0; font-weight: bold;'>⚠️ Important Guidelines:</p>
                <ul style='margin: 5px 0; padding-left: 20px;'>
                    <li>Phone numbers must include country code</li>
                    <li>Example: +1234567890</li>
                    <li>No spaces or special characters</li>
                    <li>Must be unique in database</li>
                </ul>
            </div>
        """, unsafe_allow_html=True)
        
        search_method = st.radio(
            "Find client by:",
            ["Name", "Current Phone Number"],
            help="Choose how to identify the client"
        )
        
        if search_method == "Name":
            client_names = sorted(st.session_state.df_current["Clients"].unique().tolist())
            search_value = st.selectbox(
                "Select Client Name",
                options=client_names,
                help="Select the client whose phone number you want to update"
            )
        else:
            phone_numbers = sorted(st.session_state.df_current["Phone_Numbers"].unique().tolist())
            search_value = st.selectbox(
                "Select Current Phone Number",
                options=phone_numbers,
                help="Select the current phone number you want to update"
            )
        
        new_phone = st.text_input(
            "New Phone Number",
            placeholder="Enter new phone number with country code",
            help="Enter the new phone number including country code (e.g., +1234567890)"
        )
        submitted = st.form_submit_button("Update Phone")
        
        if submitted:
            try:
                if not new_phone:
                    st.error("Please enter a new phone number")
                else:
                    if search_method == "Name":
                        success = update_client_phone(name=search_value, new_phone=new_phone)
                       
                    else:
                        success = update_client_phone(current_phone=search_value, new_phone=new_phone)
                        
                        
                    
                    if success:
                        st.success("Phone number updated successfully!")
                        save_changes_to_file()
                        time.sleep(1)
                        st.rerun()
            except Exception as e:
                st.error(f"Update failed: {str(e)}")
elif navigation_bar == "Documentation":
    st.session_state["page"] = "documentation"
    show_documentation()

Show_up_client_Database()

if st.session_state.changes_made and should_show_warning():
    elapsed = (datetime.now() - st.session_state.last_warning_time).total_seconds()
    remaining = max(0, st.session_state.warning_duration - elapsed)
    
    st.sidebar.warning(f"⚠️ Remember to save your changes! ({int(remaining)}s)")


manage_contact_queue()
check_auto_backup()

