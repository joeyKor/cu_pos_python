import tkinter as tk
from tkinter import ttk, messagebox
from smartcard.System import readers
from smartcard.Exceptions import NoCardException, CardConnectionException
import time

class BankCardApp:
    def __init__(self, root):
        self.root = root
        self.root.title("IC Card Account Reader & Writer")
        self.root.geometry("650x500")
        self.root.configure(bg="#1E1E2E")
        
        # Application State
        self.last_card_state = "DISCONNECTED" # DISCONNECTED, PRESENT, READY
        self.active_reader = None
        self.connection = None
        self.card_atr = ""
        
        self.setup_styles()
        self.create_widgets()
        
        # Start the monitoring loop
        self.check_loop()

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure overall themes
        style.configure("TFrame", background="#1E1E2E")
        style.configure("TLabel", background="#1E1E2E", foreground="#F3F4F6", font=("Segoe UI", 10))
        
        # Group Frame
        style.configure("TLabelframe", background="#1E1E2E", foreground="#8B5CF6", bordercolor="#4B5563")
        style.configure("TLabelframe.Label", background="#1E1E2E", foreground="#8B5CF6", font=("Segoe UI", 11, "bold"))
        
        # Custom Buttons
        style.configure("Primary.TButton", 
                        background="#7C3AED", 
                        foreground="#FFFFFF", 
                        font=("Segoe UI", 10, "bold"),
                        borderwidth=0,
                        focusthickness=0)
        style.map("Primary.TButton",
                  background=[("active", "#6D28D9"), ("disabled", "#4B5563")],
                  foreground=[("disabled", "#9CA3AF")])
                  
        style.configure("Secondary.TButton", 
                        background="#374151", 
                        foreground="#F3F4F6", 
                        font=("Segoe UI", 10),
                        borderwidth=0,
                        focusthickness=0)
        style.map("Secondary.TButton",
                  background=[("active", "#4B5563")])

    def create_widgets(self):
        # 1. Main Header
        header = tk.Label(self.root, text="💳 Smart Card Account System", font=("Segoe UI", 18, "bold"), bg="#1E1E2E", fg="#8B5CF6")
        header.pack(pady=(20, 10))
        
        # 2. Card Reader Status Display
        status_frame = ttk.Frame(self.root)
        status_frame.pack(fill="x", padx=20, pady=5)
        
        self.lbl_reader_info = ttk.Label(status_frame, text="Reader: Detecting...", font=("Segoe UI", 10, "italic"), foreground="#9CA3AF")
        self.lbl_reader_info.pack(side="left")
        
        self.status_indicator = tk.Label(status_frame, text="● Reader Off", font=("Segoe UI", 10, "bold"), bg="#1E1E2E", fg="#EF4444")
        self.status_indicator.pack(side="right")
        
        # 3. Main Reading Display Box
        display_frame = tk.Frame(self.root, bg="#2A2B3D", bd=2, relief="groove")
        display_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        lbl_box_title = tk.Label(display_frame, text="READ ACCOUNT NUMBER", font=("Segoe UI", 9, "bold"), bg="#2A2B3D", fg="#9CA3AF")
        lbl_box_title.pack(anchor="w", padx=15, pady=(10, 0))
        
        # Large Textbox for displaying account number
        self.account_display_var = tk.StringVar(value="[ INSERT CARD ]")
        self.lbl_account_display = tk.Label(display_frame, 
                                            textvariable=self.account_display_var, 
                                            font=("Consolas", 26, "bold"), 
                                            bg="#2A2B3D", 
                                            fg="#10B981")
        self.lbl_account_display.pack(expand=True, fill="both", pady=10)
        
        self.lbl_atr_info = tk.Label(display_frame, text="ATR: --", font=("Consolas", 9), bg="#2A2B3D", fg="#6B7280")
        self.lbl_atr_info.pack(anchor="e", padx=15, pady=(0, 10))
        
        # 4. Writing Section (Register New Account)
        write_frame = ttk.LabelFrame(self.root, text=" Register New Account to Card ")
        write_frame.pack(fill="x", padx=20, pady=20)
        
        # Account input
        ttk.Label(write_frame, text="Account Number:").grid(row=0, column=0, sticky="w", padx=15, pady=10)
        self.ent_account_input = ttk.Entry(write_frame, font=("Segoe UI", 11), width=25)
        self.ent_account_input.grid(row=0, column=1, sticky="w", padx=5, pady=10)
        self.ent_account_input.insert(0, "123-456-789012") # Placeholder
        
        # PIN input (Default is FF FF FF)
        ttk.Label(write_frame, text="Card PIN (Hex):").grid(row=0, column=2, sticky="w", padx=10, pady=10)
        self.ent_pin_input = ttk.Entry(write_frame, font=("Consolas", 10), width=10)
        self.ent_pin_input.grid(row=0, column=3, sticky="w", padx=5, pady=10)
        self.ent_pin_input.insert(0, "FF FF FF")
        
        # Write Button
        self.btn_write = ttk.Button(write_frame, text="💾 Write to Card", command=self.write_account_to_card, style="Primary.TButton")
        self.btn_write.grid(row=0, column=4, padx=15, pady=10)
        self.btn_write.state(['disabled']) # Disable initially until card is ready

    def check_loop(self):
        try:
            rs = readers()
            if not rs:
                self.lbl_reader_info.config(text="No smart card readers detected.")
                self.status_indicator.config(text="● Reader Off", fg="#EF4444")
                self.set_disconnected_state()
            else:
                reader = rs[0]
                self.lbl_reader_info.config(text=f"Active Reader: {reader}")
                self.active_reader = reader
                
                # Check if card is present and try reading
                self.auto_read_card()
                
        except Exception as e:
            self.lbl_reader_info.config(text=f"Status: Error querying readers")
            self.set_disconnected_state()
            
        # Run loop every 800 milliseconds
        self.root.after(800, self.check_loop)

    def set_disconnected_state(self):
        self.last_card_state = "DISCONNECTED"
        self.connection = None
        self.card_atr = ""
        self.account_display_var.set("[ INSERT CARD ]")
        self.lbl_account_display.config(fg="#9CA3AF")
        self.lbl_atr_info.config(text="ATR: --")
        self.btn_write.state(['disabled'])

    def auto_read_card(self):
        if not self.active_reader:
            return
            
        # Optimization: If already connected and in READY state,
        # check if card is still there using a fast read instead of resetting connection.
        if self.connection is not None and self.last_card_state == "READY":
            try:
                # Send a lightweight read command of 1 byte to check card presence.
                # If the card is removed, this transmit will throw an exception.
                read_cmd = [0xFF, 0xB0, 0x00, 0x00, 0x01]
                self.connection.transmit(read_cmd)
                return  # Card is still present and active, do nothing.
            except Exception:
                # Transmit failed: card was removed.
                self.status_indicator.config(text="● Slot Empty", fg="#6B7280")
                self.set_disconnected_state()
                return

        try:
            conn = self.active_reader.createConnection()
            
            # Try to connect with default protocols
            connected = False
            for protocol in [1, 2, 3]: # T0, T1, RAW
                try:
                    conn.connect(protocol)
                    connected = True
                    break
                except Exception:
                    continue
            
            if not connected:
                # Force connect to trigger exception if no card is present
                conn.connect()
                
            self.connection = conn
            
            # If we reached here, connection succeeded!
            atr_bytes = conn.getATR()
            atr_hex = "".join([f"{x:02X} " for x in atr_bytes]).strip()
            self.card_atr = atr_hex
            self.lbl_atr_info.config(text=f"ATR: {atr_hex}")
            
            if self.last_card_state != "READY":
                self.status_indicator.config(text="● Reading Card...", fg="#F59E0B")
                self.root.update_idletasks()
                
                # Perform Read Sequence
                account_num = self.read_account_sequence()
                if account_num:
                    self.account_display_var.set(account_num)
                    self.lbl_account_display.config(fg="#10B981")
                    self.status_indicator.config(text="● Card Connected", fg="#10B981")
                    self.btn_write.state(['!disabled']) # Enable writing
                    self.last_card_state = "READY"
                else:
                    self.account_display_var.set("[ EMPTY / INVALID CARD ]")
                    self.lbl_account_display.config(fg="#F59E0B")
                    self.status_indicator.config(text="● Card Connected (No Data)", fg="#F59E0B")
                    self.btn_write.state(['!disabled']) # Enable writing anyway
                    self.last_card_state = "READY"
                    
        except NoCardException:
            # Card was removed or not inserted
            self.status_indicator.config(text="● Slot Empty", fg="#6B7280")
            self.set_disconnected_state()
            
        except CardConnectionException:
            # Reader exists but card handshake failed (e.g. unresponsive)
            self.status_indicator.config(text="● Unresponsive Card", fg="#EF4444")
            self.account_display_var.set("[ UNRESPONSIVE CARD ]")
            self.lbl_account_display.config(fg="#EF4444")
            self.btn_write.state(['disabled'])
            self.last_card_state = "DISCONNECTED"
            
        except Exception as e:
            self.status_indicator.config(text="● Error", fg="#EF4444")
            self.set_disconnected_state()

    def read_account_sequence(self):
        if not self.connection:
            return None
            
        try:
            # 1. Initialize SLE4442 card
            init_cmd = [0xFF, 0xA4, 0x00, 0x00, 0x01, 0x06]
            self.connection.transmit(init_cmd)
            
            # 2. Read 20 bytes from address 0x00
            read_cmd = [0xFF, 0xB0, 0x00, 0x00, 0x14]
            data, sw1, sw2 = self.connection.transmit(read_cmd)
            
            if sw1 == 0x90 and sw2 == 0x00:
                # Convert bytes to string, strip whitespace and non-printables
                decoded = "".join([chr(x) for x in data if 32 <= x <= 126])
                decoded_clean = decoded.strip()
                
                # Check if it looks like garbage (all FFs, all 00s, or mostly non-printables)
                if not decoded_clean or all(x == 0xFF for x in data) or all(x == 0x00 for x in data):
                    return None
                    
                return decoded_clean
                
        except Exception:
            pass
        return None

    def write_account_to_card(self):
        if not self.connection:
            messagebox.showwarning("Warning", "No card connected.")
            return
            
        account_str = self.ent_account_input.get().strip()
        if not account_str:
            messagebox.showwarning("Warning", "Please enter an account number.")
            return
            
        # Parse PIN from input (Hex format, default is FF FF FF)
        pin_str = self.ent_pin_input.get().replace(" ", "")
        try:
            pin_bytes = [int(pin_str[i:i+2], 16) for i in range(0, len(pin_str), 2)]
            if len(pin_bytes) != 3:
                raise ValueError("PIN must be exactly 3 bytes.")
        except Exception:
            messagebox.showerror("Error", "Invalid PIN format. Must be 3 hex bytes (e.g., FF FF FF).")
            return
            
        # Verify account number characters are printable ASCII
        try:
            account_bytes = list(account_str.encode('ascii'))
        except UnicodeEncodeError:
            messagebox.showerror("Error", "Account number must contain only ASCII characters (numbers, letters, hyphens).")
            return
            
        if len(account_bytes) > 20:
            messagebox.showwarning("Warning", "Account number is too long. Max 20 characters.")
            return
            
        # Pad with spaces to exactly 20 bytes
        account_bytes += [0x20] * (20 - len(account_bytes))
        
        self.btn_write.state(['disabled'])
        self.root.update_idletasks()
        
        try:
            # 1. Initialize Card
            init_cmd = [0xFF, 0xA4, 0x00, 0x00, 0x01, 0x06]
            self.connection.transmit(init_cmd)
            
            # 2. Verify PIN
            verify_cmd = [0xFF, 0x20, 0x00, 0x00, 0x03] + pin_bytes
            data, sw1, sw2 = self.connection.transmit(verify_cmd)
            
            # For SLE4442, SW1=90 and SW2=07 indicates success (resets the error counter to 3).
            # If it returns 90 00, it is also a success.
            # If it fails, SW2 will be decremented (e.g., 03, 01, 00).
            if not (sw1 == 0x90 and (sw2 == 0x00 or sw2 == 0x07)):
                # Map error counter bits to human-readable remaining attempts
                if sw2 == 0x07:
                    remaining = 3
                elif sw2 == 0x03:
                    remaining = 2
                elif sw2 == 0x01:
                    remaining = 1
                elif sw2 == 0x00:
                    remaining = 0
                else:
                    remaining = "unknown"
                messagebox.showerror("PIN Error", f"PIN verification failed. (SW: {sw1:02X} {sw2:02X})\nRemaining attempts: {remaining}")
                return
                
            # 3. Write data to address 0x00
            write_cmd = [0xFF, 0xD0, 0x00, 0x00, 0x14] + account_bytes
            data, sw1, sw2 = self.connection.transmit(write_cmd)
            
            if sw1 == 0x90 and sw2 == 0x00:
                messagebox.showinfo("Success", f"Account number '{account_str}' successfully written to card!")
                # Force refresh state
                self.last_card_state = "UPDATE"
                self.auto_read_card()
            else:
                messagebox.showerror("Error", f"Failed to write to card. (SW: {sw1:02X} {sw2:02X})")
                
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred during write operation: {e}")
        finally:
            self.btn_write.state(['!disabled'])

if __name__ == "__main__":
    root = tk.Tk()
    app = BankCardApp(root)
    root.mainloop()
