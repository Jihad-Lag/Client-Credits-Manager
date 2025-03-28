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
import platform
from win10toast import ToastNotifier
import ctypes
import subprocess
import os

json_path = Path("database/contact.json").absolute()

class WhatsAppSender:
    def __init__(self, json_path=json_path):
        self.console = Console()
        self.json_path = Path(json_path)
        self.message_queue = []
        self.failed_messages = []
        self.wait_time = 15 
        self.tab_close_delay = 10  
        self.typing_delay = 0.05
        self.toaster = ToastNotifier() if platform.system() == 'Windows' else None
    
    def show_notification(self, title, message, duration=5, is_error=False):
        """Show system notification with different styles"""
        try:
            # Windows Toast Notification
            if platform.system() == 'Windows' and self.toaster:
                self.toaster.show_toast(
                    title,
                    message,
                    duration=duration,
                    icon_path=None,
                    threaded=True
                )
            
            # Fallback to message box
            if platform.system() == 'Windows':
                style = 0x10 | 0x1 if is_error else 0x40 | 0x1  # MB_ICONERROR or MB_ICONINFORMATION
                ctypes.windll.user32.MessageBoxW(0, message, title, style)
            elif platform.system() == 'Darwin':  # macOS
                osascript = f'display notification "{message}" with title "{title}"'
                subprocess.run(['osascript', '-e', osascript])
            else:  # Linux
                subprocess.run(['notify-send', title, message])
                
        except Exception as e:
            self.console.print(f"[yellow]Could not show notification: {e}[/yellow]")

    def wait_for_exit(self):
        """Wait for user input and then exit"""
        self.console.print("\n[bold cyan]Press Enter to exit...[/bold cyan]")
        try:
            input()  
        except KeyboardInterrupt:
            self.console.print("\n[red]Keyboard interrupt received. Exiting...[/red]")
        sys.exit(0)

    def diagnose_whatsapp_issues(self):
        """Basic system checks"""
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
            import keyboard
            self.console.print("[green]✓ Required Libraries: Installed[/green]")
            return True
        except ImportError as e:
            self.console.print(f"[red]✗ Missing Libraries: {e}[/red]")
            return False

    def load_messages(self):
        """Load messages from JSON file"""
        try:
            if not self.json_path.exists():
                self.console.print(f"[red]Error: JSON file not found at {self.json_path}[/red]")
                return False
                
            with open(self.json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                self.message_queue = []
                for client_key, client_data in data.items():
                    if not client_data.get("number_phone"):
                        continue
                        
                    phone = client_data["number_phone"]
                    if not phone.startswith('+'):
                        phone = f"+{phone.lstrip('c')}"
                    
                    self.message_queue.append({
                        "client": client_key,
                        "phone": phone,
                        "message": client_data.get("message", "")
                    })
                
                return len(self.message_queue) > 0
        
        except json.JSONDecodeError as e:
            self.console.print(f"[red]Invalid JSON format: {e}[/red]")
            return False
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
        """Core message sending functionality with improved timing"""
        try:
            if not message.strip():
                self.console.print(f"[yellow]Skipping empty message for {phone}[/yellow]")
                return False
                
            # First open chat window
            pywhatkit.sendwhatmsg_instantly(
                phone_no=phone,
                message="",  
                wait_time=self.wait_time,
                tab_close=False,
                close_time=0
            )
            
            time.sleep(14)  # Wait for chat window to open
            
            # Type message line by line
            for line in message.split('\n'):
                pyautogui.write(line, interval=self.typing_delay)
                pyautogui.hotkey('shift', 'enter')  # New line
            
            pyautogui.press('enter')  # Send message
            time.sleep(5)
            
            # Close tab
            pyautogui.hotkey('ctrl', 'w')
            time.sleep(1)
            pyautogui.press('enter')  # Confirm close if needed
            time.sleep(1)
            
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
                f"[bold red]Send Failure[/bold red]\n{error_msg}",
                title="❌ Error"
            ))
            self.failed_messages.append({
                "client": client,
                "phone": phone,
                "message": message,
                "error": str(e)
            })
            return False

    def run(self):
        """Main execution flow with notifications"""
        try:
            self.console.print(Panel.fit(
                "[bold green]WhatsApp Automation System[/bold green]\n"
                "Starting message sending process...",
                title="🚀 Initializing"
            ))

            if not self.diagnose_whatsapp_issues():
                self.show_notification("WhatsApp Sender", "Initialization failed!", is_error=True)
                self.wait_for_exit()
                return

            if not self.load_messages():
                self.show_notification("WhatsApp Sender", "No valid messages to send", is_error=False)
                self.console.print("[yellow]No messages to send.[/yellow]")
                self.wait_for_exit()
                return

            total_messages = len(self.message_queue)
            self.show_notification("WhatsApp Sender", f"Starting to send {total_messages} messages")

            for msg in self.message_queue:
                result = self.debug_send_message(
                    msg['client'], 
                    msg['phone'], 
                    msg['message']
                )
                
                if result:
                    self.delete_sent_message(msg['client'])
                
                time.sleep(3)  # Reduced delay between messages

            # Final summary
            success_count = len(self.message_queue) - len(self.failed_messages)
            summary_msg = (
                f"Successfully sent {success_count}/{total_messages}\n"
                f"Failed: {len(self.failed_messages)}"
            )
            
            self.show_notification(
                "WhatsApp Sender - Completed",
                summary_msg,
                is_error=bool(self.failed_messages))
            
            self.console.print("\n[bold]Sending Summary:[/bold]")
            self.console.print(f"Total Messages: {total_messages}")
            self.console.print(f"[green]Successful: {success_count}[/green]")
            self.console.print(f"[red]Failed: {len(self.failed_messages)}[/red]")
            
            if self.failed_messages:
                self.console.print("\n[bold]Failed Messages:[/bold]")
                for msg in self.failed_messages:
                    self.console.print(f"- {msg['client']} ({msg['phone']}): {msg['error']}")
            
        except Exception as e:
            error_msg = f"Critical error: {str(e)}"
            self.show_notification("WhatsApp Sender - CRASHED", error_msg, is_error=True)
            self.console.print(Panel.fit(
                f"[bold red]Fatal Error[/bold red]\n{error_msg}\n"
                f"Traceback:\n{traceback.format_exc()}",
                title="❌ CRITICAL ERROR"
            ))
        finally:
            self.wait_for_exit()

def main():
    sender = WhatsAppSender()
    sender.run()

if __name__ == "__main__":
    main()