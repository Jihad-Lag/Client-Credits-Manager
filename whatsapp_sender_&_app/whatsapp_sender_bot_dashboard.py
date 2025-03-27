import json
import pywhatkit
import time
import sys
import traceback
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
import socket
import pyautogui


json_path = Path("database/contact.json").absolute()

class WhatsAppSender:
    def __init__(self, json_path=json_path):
        self.console = Console()
        self.json_path = Path(json_path)
        self.message_queue = []
        self.failed_messages = []
        self.wait_time = 15
        self.tab_close_delay = 3
    
    def wait_for_exit(self):
     """Wait for user input and then force-close the CMD window"""
     self.console.print("\n[bold cyan]Press Enter two times to exit and close the CMD window...[/bold cyan]")
     try:
        input()  
     except KeyboardInterrupt:
        self.console.print("\n[red]Keyboard interrupt received. Exiting...[/red]")
 
     if sys.platform == 'win32':
        import os
        os.system("taskkill /f /im cmd.exe")
     else:
        sys.exit(0)  

    def diagnose_whatsapp_issues(self):
        """Basic system checks without WhatsApp Web verification"""
        self.console.print(Panel.fit(
            "[bold red]System Diagnostic Report[/bold red]\n" +
            "Running basic checks...", 
            title="🔍 Troubleshooting"
        ))

        checks = {
            "Internet Connection": self.check_internet(),
            "Dependencies": self.check_dependencies(),
        }

        if not all(checks.values()):
            self.console.print("[red]Critical issues detected. Cannot proceed.[/red]")
            return False
        
        return True

    def check_internet(self):
        try:
            socket.create_connection(("www.google.com", 80), timeout=5)
            self.console.print("[green]✓ Internet Connection: Stable[/green]")
            return True
        except Exception:
            self.console.print("[red]✗ Internet Connection: Unstable[/red]")
            return False

    def check_dependencies(self):
        try:
            import pyautogui
            import pyperclip
            self.console.print("[green]✓ Required Libraries: Installed[/green]")
            return True
        except ImportError as e:
            self.console.print(f"[red]✗ Missing Libraries: {e}[/red]")
            return False

    def load_messages(self):
        """Load messages from JSON file"""
        try:
            with open(self.json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                self.message_queue = []
                for client_key, client_data in data.items():
                    phone = client_data["number_phone"]
                    
                    self.message_queue.append({
                        "client": client_key,
                        "phone": phone,
                        "message": client_data["message"]
                    })
                
                return len(self.message_queue) > 0
        
        except Exception as e:
            self.console.print(f"[red]Error loading messages: {e}[/red]")
            return False

    def delete_sent_message(self, client_key):
        """Delete the sent message from the JSON file"""
        try:
            with open(self.json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if client_key in data:
                del data[client_key]
            
            with open(self.json_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            
            self.console.print(f"[yellow]Message for {client_key} deleted from JSON[/yellow]")
            return True
        
        except Exception as e:
            self.console.print(f"[red]Error deleting message: {e}[/red]")
            return False

    def send_message_safely(self, phone, message):
        """Core message sending functionality"""
        try:
            
            try:
                pyautogui.hotkey('ctrl', 'w')
                time.sleep(2)
            except:
                pass

            
            pywhatkit.sendwhatmsg_instantly(
                phone_no=phone,
                message=message,
                wait_time=self.wait_time,
                tab_close=True,
                close_time=self.tab_close_delay
            )
            
            return True
        
        except Exception as e:
            self.console.print(f"[red]Sending Error: {str(e)}[/red]")
            return False

    def debug_send_message(self, client, phone, message):
        """Message sending with logging"""
        try:
            self.console.print(Panel.fit(
                f"[bold]Sending Message[/bold]\n"
                f"To: {client}\n"
                f"Phone: {phone}\n"
                f"Message: {message[:50]}...",
                title="📤 Sending Attempt"
            ))

            if not self.send_message_safely(phone, message):
                raise Exception("Failed in safe sending method")

            self.console.print(f"[green]✓ Message sent to {client}[/green]")
            return True

        except Exception as e:
            error_msg = f"Failed to send to {client}: {str(e)}"
            self.console.print(Panel.fit(
                f"[bold red]Send Failure[/bold red]\n{error_msg}\n"
                f"Traceback:\n{traceback.format_exc()}",
                title="❌ Error"
            ))
            return False

    def run(self):
        """Main execution flow"""
        if not self.diagnose_whatsapp_issues():
            self.wait_for_exit()
            return

        if not self.load_messages():
            self.console.print("[yellow]No messages to send.[/yellow]")
            self.wait_for_exit()
            return

        for msg in self.message_queue:
            result = self.debug_send_message(
                msg['client'], 
                msg['phone'], 
                msg['message']
            )
            
            if result:
                self.delete_sent_message(msg['client'])
            else:
                self.failed_messages.append(msg)
            
            time.sleep(10) 

        
        self.console.print("\n[bold]Sending Summary:[/bold]")
        self.console.print(f"Total Messages: {len(self.message_queue)}")
        self.console.print(f"[green]Successful: {len(self.message_queue) - len(self.failed_messages)}[/green]")
        self.console.print(f"[red]Failed: {len(self.failed_messages)}[/red]")
        
        self.wait_for_exit()

def main():
    sender = WhatsAppSender()
    sender.run()

if __name__ == "__main__":
    main()