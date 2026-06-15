import tkinter as tk
from tkinter import ttk, scrolledtext
from machineInfo import extract_ipv6_info, print_machine_info
import threading
from Echomessage import echo_server, echo_client
import time
from Sntpmodules import sntp_client
import ErrSet
import os
from Chatserver import ChatServer,send
from Chatclient import ChatClient,receive
import sys
from io import StringIO
import tkinter.messagebox

class BaseModule:
   # Base class inherited by all modules.

    def __init__(self, parent_frame, root):
        self.parent_frame = parent_frame
        self.root = root
        self.container = None

    def create_container(self):
        #we use this function Creates the main container for the module
        self.container = tk.Frame(self.parent_frame, bg='white')
        self.container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        return self.container

    def clear(self):

        if self.container:
            self.container.destroy()

    def render(self):
        #to   Creates and renders the module’s content
        raise NotImplementedError("Subclass must implement render()")


class MachineInfoModule(BaseModule):
    "for first module"
    def render(self):
        # Draws the machine information on screen
        self.create_container()

        try:
            host_name, ip_address = print_machine_info()
            interfaces_data = extract_ipv6_info()

            grid_container = tk.Frame(self.container, bg='white')
            grid_container.pack(fill=tk.BOTH, expand=True)

            # TOP LEFT: HOST NAME AND IP ADDRESS
            left_top_frame = tk.Frame(grid_container, bg='#FCECEC', relief=tk.FLAT, bd=0)
            left_top_frame.grid(row=0, column=0, sticky='nsew', padx=10, pady=10)

            info_container = tk.Frame(left_top_frame, bg='#FCECEC')
            info_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

            tk.Label(
                info_container,
                text="HOST NAME:",
                font=('Segoe UI', 11, 'bold'),
                bg='#FCECEC',
                fg='#1a1a2e',
                anchor='w'
            ).pack(fill=tk.X, pady=(5, 2))

            hostname_frame = tk.Frame(info_container, bg='#F5D5D5', relief=tk.FLAT)
            hostname_frame.pack(fill=tk.X, pady=(0, 15))
            tk.Label(
                hostname_frame,
                text=host_name,
                font=('Segoe UI', 10),
                bg='#F5D5D5',
                fg='#1a1a2e',
                anchor='w'
            ).pack(padx=10, pady=8)

            tk.Label(
                info_container,
                text="IP ADDRESS:",
                font=('Segoe UI', 11, 'bold'),
                bg='#FCECEC',
                fg='#1a1a2e',
                anchor='w'
            ).pack(fill=tk.X, pady=(5, 2))

            ip_frame = tk.Frame(info_container, bg='#F5D5D5', relief=tk.FLAT)
            ip_frame.pack(fill=tk.X)
            tk.Label(
                ip_frame,
                text=ip_address,
                font=('Segoe UI', 10),
                bg='#F5D5D5',
                fg='#1a1a2e',
                anchor='w'
            ).pack(padx=10, pady=8)

            # BOTTOM LEFT: NETWORK INTERFACE NAMES
            left_bottom_frame = tk.Frame(grid_container, bg='#E8EEF2', relief=tk.FLAT, bd=0)
            left_bottom_frame.grid(row=1, column=0, sticky='nsew', padx=10, pady=10)

            interfaces_container = tk.Frame(left_bottom_frame, bg='#E8EEF2')
            interfaces_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
                #title
            tk.Label(
                interfaces_container,
                text="NETWORK INTERFACES",
                font=('Segoe UI', 12, 'bold'),
                bg='#E8EEF2',
                fg='#1a1a2e'
            ).pack(pady=(5, 10))

            interfaces_frame = tk.Frame(interfaces_container, bg='#D5E0E8')
            interfaces_frame.pack(fill=tk.BOTH, expand=True)

            interfaces_text = tk.Text(
                interfaces_frame,
                font=('Consolas', 10),
                bg='#D5E0E8',
                fg='#1a1a2e',
                relief=tk.FLAT,
                height=10,
                wrap=tk.WORD,
                bd=0
            )
            interfaces_text.pack(fill=tk.BOTH, expand=True)

            for iface in interfaces_data:
                interfaces_text.insert(tk.END, f"• {iface['interface']}\n", 'interface')

            interfaces_text.tag_config('interface', font=('Consolas', 10, 'bold'), foreground='#1a1a2e')
            interfaces_text.config(state=tk.DISABLED)

            # RIGHT SIDE: DETAILED NETWORK INFO
            right_frame = tk.Frame(grid_container, bg='#EAF7F0', relief=tk.FLAT, bd=0)
            right_frame.grid(row=0, column=1, rowspan=2, sticky='nsew', padx=10, pady=10)

            details_container = tk.Frame(right_frame, bg='#EAF7F0')
            details_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

            tk.Label(
                details_container,
                text="NETWORK INTERFACES\nAND IP ADDRESSES",
                font=('Segoe UI', 12, 'bold'),
                bg='#EAF7F0',
                fg='#1a1a2e',
                justify='center'
            ).pack(pady=(5, 10))

            # ScrolledText: Text widget + automatic scrollbar
            details_text = scrolledtext.ScrolledText(
                details_container,
                font=('Consolas', 9),
                bg='#D5EFE0',
                fg='#1a1a2e',
                relief=tk.FLAT,
                wrap=tk.WORD
            )
            details_text.pack(fill=tk.BOTH, expand=True)

            for iface in interfaces_data:
                details_text.insert(tk.END, f"{'=' * 50}\n", 'separator')
                details_text.insert(tk.END, f"Interface: {iface['interface']}\n", 'header')
                details_text.insert(tk.END, f"{'=' * 50}\n", 'separator')

                if iface.get('error'):
                    details_text.insert(tk.END, f"❌ Error: {iface['error']}\n\n", 'error')
                elif iface.get('warning'):
                    details_text.insert(tk.END, f"⚠️ Warning: {iface['warning']}\n\n", 'warning')
                elif iface.get('ips'):
                    details_text.insert(tk.END, "\nIP Addresses:\n", 'subheader')
                    for ip in iface['ips']:
                        if ':' in ip:
                            details_text.insert(tk.END, f"  ➤ [IPv6] {ip}\n", 'ipv6')
                        else:
                            details_text.insert(tk.END, f"  ➤ [IPv4] {ip}\n", 'ipv4')
                    details_text.insert(tk.END, "\n")
                else:
                    details_text.insert(tk.END, "No IP addresses found\n\n", 'noip')
            # TEXT STYLES
            details_text.tag_config('separator', foreground='#999999')
            details_text.tag_config('header', font=('Consolas', 10, 'bold'), foreground='#e94560')
            details_text.tag_config('subheader', font=('Consolas', 9, 'bold'), foreground='#2e7d32')
            details_text.tag_config('ipv4', foreground='#1565c0', font=('Consolas', 9, 'bold'))
            details_text.tag_config('ipv6', foreground='#43a047', font=('Consolas', 9))
            details_text.tag_config('error', foreground='#d32f2f')
            details_text.tag_config('warning', foreground='#f57c00')
            details_text.tag_config('noip', foreground='#757575')
            details_text.config(state=tk.DISABLED)

            grid_container.grid_columnconfigure(0, weight=1, minsize=300)
            grid_container.grid_columnconfigure(1, weight=2, minsize=400)
            grid_container.grid_rowconfigure(0, weight=1)
            grid_container.grid_rowconfigure(1, weight=1)

        except Exception as e:
            error_frame = tk.Frame(self.container, bg='white')
            error_frame.pack(expand=True, fill=tk.BOTH, padx=50, pady=50)

            error_icon = tk.Label(
                error_frame,
                text="❌",
                font=('Segoe UI', 48),
                bg='white',
                fg='#ff0000'
            )
            error_icon.pack(pady=(0, 15))

            error_label = tk.Label(
                error_frame,
                text=f"Hata Oluştu!\n\n{str(e)}",
                font=('Segoe UI', 12),
                bg='white',
                fg='#ff0000',
                justify='center'
            )
            error_label.pack()



class EchoTestModule(BaseModule):

    def render(self):

          # For creates the GUI layout for echo test.
        self.create_container()


        settings_frame = tk.Frame(self.container, bg='#f0f0f0', relief=tk.RIDGE, bd=2)
        settings_frame.pack(fill=tk.X, pady=(0, 15))

        settings_inner = tk.Frame(settings_frame, bg='#f0f0f0')
        settings_inner.pack(padx=15, pady=15)

        # Mode selection
        tk.Label(settings_inner, text="Mode:", font=('Segoe UI', 10, 'bold'),
                 bg='#f0f0f0').grid(row=0, column=0, sticky='w', padx=5)

        self.echo_mode = tk.StringVar(value="")
        mode_menu = ttk.Combobox(settings_inner, textvariable=self.echo_mode,
                                 values=["server", "client"], state="readonly", width=10)
        mode_menu.grid(row=0, column=1, padx=5)

        # Host input
        tk.Label(settings_inner, text="Host:", font=('Segoe UI', 10, 'bold'),
                 bg='#f0f0f0').grid(row=0, column=2, sticky='w', padx=(15, 5))

        self.echo_host_entry = tk.Entry(settings_inner, font=('Segoe UI', 10), width=15)
        self.echo_host_entry.grid(row=0, column=3, padx=5)

        # Port input
        tk.Label(settings_inner, text="Port:", font=('Segoe UI', 10, 'bold'),
                 bg='#f0f0f0').grid(row=0, column=4, sticky='w', padx=(15, 5))

        self.echo_port_entry = tk.Entry(settings_inner, font=('Segoe UI', 10), width=8)
        self.echo_port_entry.grid(row=0, column=5, padx=5)

        # Start buton
        self.echo_start_btn = tk.Button(
            settings_inner,
            text="▶ Start",
            font=('Segoe UI', 10, 'bold'),
            bg='#4CAF50',
            fg='white',
            cursor='hand2',
            padx=15,
            pady=5,
            command=self.start_echo_test
        )
        self.echo_start_btn.grid(row=0, column=6, padx=(20, 0))

        # Log frame
        log_frame = tk.Frame(self.container, bg='#E8F5E9', relief=tk.RIDGE, bd=2)
        log_frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(log_frame, text="📋 Loglar", font=('Segoe UI', 11, 'bold'),
                 bg='#E8F5E9', fg='#1a1a2e').pack(pady=8)

        self.echo_log_text = scrolledtext.ScrolledText(
            log_frame,
            font=('Consolas', 9),
            bg='#F1F8F4',
            fg='#1a1a2e',
            relief=tk.FLAT,
            wrap=tk.WORD,
            height=18
        )
        self.echo_log_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        self.echo_log_text.insert(tk.END, "Hazır. Mode seçip 'Başlat' butonuna tıklayın...\n")
        self.echo_log_text.config(state=tk.DISABLED)

    def start_echo_test(self):
         #for start the Echo test

        mode = self.echo_mode.get()
        host = self.echo_host_entry.get()

        try:
            port = int(self.echo_port_entry.get())
        except ValueError:
            self.append_echo_log("❌ Geçersiz port numarası!")
            return

        self.echo_start_btn.config(state=tk.DISABLED, text="⏳ Çalışıyor...")
        self.echo_log_text.config(state=tk.NORMAL)
        self.echo_log_text.delete(1.0, tk.END)
        self.echo_log_text.config(state=tk.DISABLED)

        def run_test():
            #Runs the echo test in a separate thread (background task)

            try:
                if mode == "server":# if it isi server mode
                    self.append_echo_log("🔄 Server başlatılıyor...")

                    def run_background_client():
                        time.sleep(2)#Wait 2 seconds
                        echo_client(host, port, callback=None)

                    client_thread = threading.Thread(target=run_background_client, daemon=True)
                    client_thread.start()

                    result = echo_server(host, port, callback=self.append_echo_log)

                else:
                    self.append_echo_log("🔄 Client hazırlanıyor...")

                    def run_background_server():
                        echo_server(host, port, callback=None)

                    server_thread = threading.Thread(target=run_background_server, daemon=True)
                    server_thread.start()

                    time.sleep(1)
                    result = echo_client(host, port, callback=self.append_echo_log)

            except Exception as e:
                self.append_echo_log(f"❌ Hata: {str(e)}")
            finally:
                self.root.after(0, lambda: self.echo_start_btn.config(
                    state=tk.NORMAL, text="▶ Başlat"
                ))

        thread = threading.Thread(target=run_test, daemon=True)
        thread.start()

    def append_echo_log(self, message):
        def update():
            self.echo_log_text.config(state=tk.NORMAL)
            self.echo_log_text.insert(tk.END, message + "\n")
            self.echo_log_text.see(tk.END)
            self.echo_log_text.config(state=tk.DISABLED)

        self.root.after(0, update)



class SntpModule(BaseModule):
    # Module that retrieves and displays real time from an NTP server

    def render(self):
        #Creates the SNTP module interface
        self.create_container()

        # TITLE AND START BUTTON
        header_frame = tk.Frame(self.container, bg='#FCECEC')
        header_frame.pack(fill=tk.X, pady=(0, 20))

        tk.Label(header_frame, text="DO YOU WANT TO LEARN THE TIME?",
                 font=('Segoe UI', 14, 'bold'), bg='#FCECEC', fg='#1a1a2e').pack(side=tk.LEFT, padx=20, pady=15)

        self.sntp_start_btn = tk.Button(header_frame, text="START", font=('Segoe UI', 12, 'bold'),
                                        bg='#e94560', fg='white', padx=40, pady=10, bd=0,
                                        command=self.start_sntp_query)
        self.sntp_start_btn.pack(side=tk.RIGHT, padx=20, pady=15)

        #RESULT AREA
        self.sntp_result_frame = tk.Frame(self.container, bg='white')
        self.sntp_result_frame.pack(fill=tk.BOTH, expand=True)

    def start_sntp_query(self):
        #when START is presseded,retrieves the time information from the NTP server
        self.sntp_start_btn.config(state=tk.DISABLED, text="LOADING...")
        for widget in self.sntp_result_frame.winfo_children():
            widget.destroy()

        def fetch():
            try:

                ntp_time = sntp_client()
                self.root.after(0, lambda: self.display_sntp_results(ntp_time))
            except Exception as e:
                self.root.after(0, lambda: tk.Label(self.sntp_result_frame, text=f"❌ Error: {e}",
                                                    bg='white', fg='red', font=('Segoe UI', 12)).pack(expand=True))
            finally:# If an error occurs
                self.root.after(0, lambda: self.sntp_start_btn.config(state=tk.NORMAL, text="START"))

        threading.Thread(target=fetch, daemon=True).start()

    def display_sntp_results(self, ntp_time):
        #to  Display the retrieved NTP time on screen
        for widget in self.sntp_result_frame.winfo_children():# # Clear previous content
            widget.destroy()

        result = tk.Frame(self.sntp_result_frame, bg='white')
        result.pack(expand=True, fill=tk.BOTH, padx=40, pady=20)
        # NTP time box
        ntp_frame = tk.Frame(result, bg='#FCECEC')
        ntp_frame.pack(fill=tk.BOTH, expand=True)
        tk.Label(ntp_frame, text="NTP SERVER TIME:", font=('Segoe UI', 12, 'bold'),
                 bg='#FCECEC', fg='#1a1a2e').pack(anchor='w', padx=25, pady=(20, 8))
        inner = tk.Frame(ntp_frame, bg='#F5D5D5')
        inner.pack(fill=tk.BOTH, expand=True, padx=25, pady=(0, 20))
        tk.Label(inner, text=ntp_time, font=('Consolas', 11),
                 bg='#F5D5D5', fg='#1a1a2e').pack(expand=True, pady=12)


class ChatModule(BaseModule):
    #Module for message exchange between Server and Client
    def render(self):
        #Creates the chat module interface
        self.create_container()

        # SETTINGS PANEL
        top = tk.Frame(self.container, bg='#FCECEC', relief=tk.FLAT, bd=0)
        top.pack(fill=tk.X, pady=(0, 15))
        top_inner = tk.Frame(top, bg='#FCECEC')
        top_inner.pack(padx=20, pady=15)

        # Host selection
        tk.Label(top_inner, text="Host:", font=('Segoe UI', 10, 'bold'), bg='#FCECEC').grid(row=0, column=0, padx=5)
        self.chat_host = ttk.Combobox(top_inner, font=('Segoe UI', 10), width=13,
                                      values=["127.0.0.1", "0.0.0.0", "localhost"], state="readonly")
        self.chat_host.grid(row=0, column=1, padx=5)
        # Port input
        tk.Label(top_inner, text="Port:", font=('Segoe UI', 10, 'bold'), bg='#FCECEC').grid(row=0, column=2,
                                                                                            padx=(15, 5))
        self.chat_port = tk.Entry(top_inner, font=('Segoe UI', 10), width=8, bg='#F5D5D5')
        self.chat_port.grid(row=0, column=3, padx=5)
        # START button
        self.chat_start_btn = tk.Button(top_inner, text="▶ START", font=('Segoe UI', 10, 'bold'),
                                        bg='#4CAF50', fg='white', padx=20, pady=8, bd=0, command=self.start_chat)
        self.chat_start_btn.grid(row=0, column=4, padx=(20, 5))
        # STOP button
        self.chat_stop_btn = tk.Button(top_inner, text="⬛ STOP", font=('Segoe UI', 10, 'bold'),
                                       bg='#f44336', fg='white', padx=20, pady=8, bd=0, state=tk.DISABLED,
                                       command=self.stop_chat)
        self.chat_stop_btn.grid(row=0, column=5, padx=5)

        # MESSAGE PANELS
        panels = tk.Frame(self.container, bg='white')
        panels.pack(fill=tk.X, pady=(0, 15))

        # Server Panel
        server_frame = tk.Frame(panels, bg='#E8EEF2', relief=tk.FLAT, bd=0)
        server_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        tk.Label(server_frame, text="🖥️ SERVER", font=('Segoe UI', 12, 'bold'),
                 bg='#E8EEF2', fg='#1a1a2e').pack(pady=15)

        server_input_frame = tk.Frame(server_frame, bg='#E8EEF2')
        server_input_frame.pack(fill=tk.X, padx=15, pady=(0, 15))

        self.server_msg = tk.Entry(server_input_frame, font=('Segoe UI', 11),
                                   bg='#D5E0E8', state=tk.DISABLED, relief=tk.FLAT)
        self.server_msg.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10), ipady=8)
        # Server SEND button
        self.server_send_btn = tk.Button(server_input_frame, text="📤 SEND",
                                         font=('Segoe UI', 10, 'bold'),
                                         bg='#0f3460', fg='white', padx=20, pady=8, bd=0,
                                         cursor='hand2', state=tk.DISABLED,
                                         command=self.send_server_msg)
        self.server_send_btn.pack(side=tk.RIGHT)

        # Client Panel
        client_frame = tk.Frame(panels, bg='#EAF7F0', relief=tk.FLAT, bd=0)
        client_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))

        tk.Label(client_frame, text="👤 CLIENT", font=('Segoe UI', 12, 'bold'),
                 bg='#EAF7F0', fg='#1a1a2e').pack(pady=15)

        client_input_frame = tk.Frame(client_frame, bg='#EAF7F0')
        client_input_frame.pack(fill=tk.X, padx=15, pady=(0, 15))

        self.client_msg = tk.Entry(client_input_frame, font=('Segoe UI', 11),
                                   bg='#D5EFE0', state=tk.DISABLED, relief=tk.FLAT)
        self.client_msg.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10), ipady=8)
        # Client SEND button
        self.client_send_btn = tk.Button(client_input_frame, text="📤 SEND",
                                         font=('Segoe UI', 10, 'bold'),
                                         bg='#0f3460', fg='white', padx=20, pady=8, bd=0,
                                         cursor='hand2', state=tk.DISABLED,
                                         command=self.send_client_msg)
        self.client_send_btn.pack(side=tk.RIGHT)

        # Log
        log_frame = tk.Frame(self.container, bg='#FCECEC', relief=tk.FLAT, bd=0)
        log_frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(log_frame, text="📋 CHAT LOG", font=('Segoe UI', 11, 'bold'),
                 bg='#FCECEC', fg='#1a1a2e').pack(pady=8)

        self.chat_log = scrolledtext.ScrolledText(log_frame, font=('Consolas', 9), bg='#F5D5D5', fg='#1a1a2e',
                                                  relief=tk.FLAT, wrap=tk.WORD, height=15)
        self.chat_log.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))
        self.chat_log.insert(tk.END, "Ready. Click START to begin chat...\n")
        self.chat_log.config(state=tk.DISABLED)

        self.chat_server = None
        self.chat_client = None

    def start_chat(self):
        #Starts the chat system
        # Get user inputs
        host = self.chat_host.get().strip()
        port_str = self.chat_port.get().strip()

        if not host or not port_str:
            self.append_chat_log("❌ Please select Host and enter Port!")
            return

        try:
            port = int(port_str)
        except ValueError:
            self.append_chat_log("❌ Invalid port number!")
            return
        # Enable buttons and input fields
        for btn in [self.server_send_btn, self.client_send_btn, self.chat_stop_btn]:
            btn.config(state=tk.NORMAL)
        for entry in [self.server_msg, self.client_msg]:
            entry.config(state=tk.NORMAL)
        self.chat_start_btn.config(state=tk.DISABLED)

        self.append_chat_log("🚀 Starting chat system...")

        def run_server():
            """Runs the server in a separate thread"""
            try:
                self.chat_server = ChatServer(port, host)
                self.append_chat_log(f"✅ Server started on {host}:{port}")
                self.chat_server.run()
            except Exception as e:
                self.append_chat_log(f"❌ Server error: {e}")

        def run_client():
            """Runs the client in a separate thread"""
            try:
                time.sleep(1.5)
                # The client cannot connect to 0.0.0.0, use localhost
                client_host = '127.0.0.1' if host == '0.0.0.0' else host


                old_stdin = sys.stdin
                sys.stdin = StringIO()

                # Create instance from ChatClient class
                self.chat_client = ChatClient("User1", port, client_host)
                self.append_chat_log(f"✅ Client connected to {client_host}:{port}")

                sys.stdin = old_stdin# Restore stdin

                def receive_messages():
                    """Inner function that listens for incoming messages"""
                    while self.chat_client.connected:
                        try:
                            data = receive(self.chat_client.sock)
                            if data:
                                self.append_chat_log(f"[RECEIVED] {data}")
                        except:
                            break

                threading.Thread(target=receive_messages, daemon=True).start()
            except Exception as e:
                self.append_chat_log(f"❌ Client error: {e}")

        # Start server and client in separate threads
        threading.Thread(target=run_server, daemon=True).start()
        threading.Thread(target=run_client, daemon=True).start()

    def stop_chat(self):
        """Stops the chat system"""
        if self.chat_server:
            try:
                self.chat_server.save_chat_log()# Save chat history to file
            except:
                pass
        if self.chat_client:
            try:
                self.chat_client.connected = False
            except:
                pass

        for btn in [self.server_send_btn, self.client_send_btn, self.chat_stop_btn]:
            btn.config(state=tk.DISABLED)
        for entry in [self.server_msg, self.client_msg]:
            entry.config(state=tk.DISABLED)
        self.chat_start_btn.config(state=tk.NORMAL)

        self.append_chat_log("🔴 Chat stopped!")

    def send_server_msg(self):
        #Sends message from the server
        msg = self.server_msg.get().strip()# Get message from input
        if msg and self.chat_server: # If message and server exist
            try:
                broadcast = f"\n#[server]>> {msg}"
                self.chat_server.chat_log.append(broadcast)
                for output in self.chat_server.outputs:
                    send(output, broadcast)

                self.append_chat_log(f"[SERVER] >> {msg}")
                self.server_msg.delete(0, tk.END) # Clear input box
            except Exception as e:
                self.append_chat_log(f"❌ Error: {e}")

    def send_client_msg(self):
        #Sends message from the client
        msg = self.client_msg.get().strip()
        if msg and self.chat_client and self.chat_client.connected:
            try:
                send(self.chat_client.sock, msg)# Send via socket

                self.append_chat_log(f"[CLIENT] >> {msg}")
                self.client_msg.delete(0, tk.END) # Clear input box
            except Exception as e:
                self.append_chat_log(f"❌ Error: {e}")

    def append_chat_log(self, message):
        #Appends a message to the chat log
        def update():
            self.chat_log.config(state=tk.NORMAL)
            self.chat_log.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] {message}\n")
            self.chat_log.see(tk.END)
            self.chat_log.config(state=tk.DISABLED)

        self.root.after(0, update)


class ErrorManagerModule(BaseModule):
    #  Module that configures socket settings and displays error logs
    def __init__(self, parent_frame, root):
        # Constructor - Inherits from BaseModule and adds extra features
        super().__init__(parent_frame, root)
        self.show_all_logs = False

    def render(self):
        #To creates the Error Manager interface
        self.create_container()


        settings_frame = tk.Frame(self.container, bg='#E8EEF2')
        settings_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))

        settings_inner = tk.Frame(settings_frame, bg='#E8EEF2')
        settings_inner.pack(padx=25, pady=20, fill=tk.BOTH, expand=True)

        tk.Label(settings_inner, text="SOCKET SETTINGS", font=('Segoe UI', 13, 'bold'),
                 bg='#E8EEF2', fg='#1a1a2e').pack(anchor='w', pady=(0, 15))

        grid = tk.Frame(settings_inner, bg='#E8EEF2')
        grid.pack(fill=tk.X)

        # Inputs
        #TIMEOUT SETTING
        tk.Label(grid, text="Timeout (seconds):", font=('Segoe UI', 10, 'bold'),
                 bg='#E8EEF2').grid(row=0, column=0, sticky='w', pady=8, padx=(0, 15))
        self.timeout_entry = tk.Entry(grid, font=('Segoe UI', 10), width=15, bg='#D5E0E8')
        self.timeout_entry.grid(row=0, column=1, pady=8)
        #SEND BUFFER SETTING
        tk.Label(grid, text="Send Buffer (bytes):", font=('Segoe UI', 10, 'bold'),
                 bg='#E8EEF2').grid(row=1, column=0, sticky='w', pady=8, padx=(0, 15))
        self.send_buf_entry = tk.Entry(grid, font=('Segoe UI', 10), width=15, bg='#D5E0E8')
        self.send_buf_entry.grid(row=1, column=1, pady=8)
        #RECEIVE BUFFER SETTING
        tk.Label(grid, text="Receive Buffer (bytes):", font=('Segoe UI', 10, 'bold'),
                 bg='#E8EEF2').grid(row=2, column=0, sticky='w', pady=8, padx=(0, 15))
        self.recv_buf_entry = tk.Entry(grid, font=('Segoe UI', 10), width=15, bg='#D5E0E8')
        self.recv_buf_entry.grid(row=2, column=1, pady=8)

        # Checkboxes
        checks = tk.Frame(settings_inner, bg='#E8EEF2')
        checks.pack(fill=tk.X, pady=(20, 0))

        self.blocking_var = tk.BooleanVar(value=False)
        tk.Checkbutton(checks, text="Blocking Mode", font=('Segoe UI', 10, 'bold'),
                       variable=self.blocking_var, bg='#E8EEF2', selectcolor='#D5E0E8').pack(anchor='w', pady=5)

        self.logging_var = tk.BooleanVar(value=False)
        tk.Checkbutton(checks, text="Enable Logging", font=('Segoe UI', 10, 'bold'),
                       variable=self.logging_var, bg='#E8EEF2', selectcolor='#D5E0E8').pack(anchor='w', pady=5)

        self.error_handling_var = tk.BooleanVar(value=False)
        tk.Checkbutton(checks, text="Enable Error Handling", font=('Segoe UI', 10, 'bold'),
                       variable=self.error_handling_var, bg='#E8EEF2', selectcolor='#D5E0E8').pack(anchor='w', pady=5)

        # SAVE
        tk.Button(settings_inner, text="💾 SAVE SETTINGS", font=('Segoe UI', 11, 'bold'),
                  bg='#e94560', fg='white', padx=20, pady=10, bd=0, command=self.save_error_settings).pack(pady=(20, 0))

        # Log
        log_frame = tk.Frame(self.container, bg='#FCECEC')
        log_frame.pack(fill=tk.BOTH, expand=True)

        log_inner = tk.Frame(log_frame, bg='#FCECEC')
        log_inner.pack(padx=25, pady=20, fill=tk.BOTH, expand=True)

        log_header = tk.Frame(log_inner, bg='#FCECEC')
        log_header.pack(fill=tk.X, pady=(0, 10))
        tk.Label(log_header, text="ERROR LOG", font=('Segoe UI', 13, 'bold'),
                 bg='#FCECEC').pack(side=tk.LEFT)

        btn_container = tk.Frame(log_header, bg='#FCECEC')
        btn_container.pack(side=tk.RIGHT)

        # 📋 Button: Show/hide all logs
        tk.Button(btn_container, text="📋", font=('Segoe UI', 9, 'bold'), bg='#0f3460', fg='white',
                  padx=12, pady=5, bd=0, command=self.toggle_all_logs).pack(side=tk.LEFT, padx=(0, 5))
        # ⚙️ Button: Show current settings
        tk.Button(btn_container, text="⚙️", font=('Segoe UI', 9, 'bold'), bg='#0f3460', fg='white',
                  padx=12, pady=5, bd=0, command=self.show_settings_detail).pack(side=tk.LEFT, padx=(0, 5))
        # 🔄 Button: Refresh logs
        tk.Button(btn_container, text="🔄", font=('Segoe UI', 9, 'bold'), bg='#0f3460', fg='white',
                  padx=12, pady=5, bd=0, command=self.refresh_error_log).pack(side=tk.LEFT)

        self.error_log_text = scrolledtext.ScrolledText(log_inner, font=('Consolas', 9),
                                                        bg='#F5D5D5', relief=tk.FLAT, height=8)
        self.error_log_text.pack(fill=tk.BOTH, expand=True)
        self.refresh_error_log()

    def toggle_all_logs(self):
        """
               Toggle between showing all logs or only ERROR_MANAGER logs
               Triggered by the 📋 button
               """
        self.show_all_logs = not self.show_all_logs
        self.refresh_error_log()

    def refresh_error_log(self):
        """
              Reads logs from error_log.txt and displays them
              """
        self.error_log_text.config(state=tk.NORMAL)
        self.error_log_text.delete(1.0, tk.END)

        # Check if log file exists
        if os.path.exists("error_log.txt"):
            try:
                with open("error_log.txt", "r", encoding="utf-8") as f:
                    for line in f:
                        if self.show_all_logs or "[ERROR_MANAGER]" in line:
                            self.error_log_text.insert(tk.END, line)

                if self.error_log_text.get(1.0, tk.END).strip() == "":
                    self.error_log_text.insert(tk.END, "No logs yet.")
            except Exception as e:
                self.error_log_text.insert(tk.END, f"Error: {e}")
        else:
            self.error_log_text.insert(tk.END, "No log file found.")

        self.error_log_text.config(state=tk.DISABLED)

    def show_settings_detail(self):
        #  Reads current settings from settings.txt
        if os.path.exists("settings.txt"):# Check if settings file exist
            try:

                self.error_log_text.config(state=tk.NORMAL)# Make editable
                # Separator start
                self.error_log_text.insert(tk.END, "\n" + "=" * 50 + "\n")
                self.error_log_text.insert(tk.END, "CURRENT SETTINGS:\n")
                self.error_log_text.insert(tk.END, "=" * 50 + "\n")
                # Read file and display only lines containing '='
                with open("settings.txt", "r", encoding="utf-8") as f:
                    for line in f:
                        if "=" in line:
                            self.error_log_text.insert(tk.END, line)

                self.error_log_text.insert(tk.END, "=" * 50 + "\n\n")
                self.error_log_text.see(tk.END)
                self.error_log_text.config(state=tk.DISABLED)
            except Exception as e:# File read error
                tkinter.messagebox.showerror("Error", f"Cannot read settings: {e}")
        else:
            tkinter.messagebox.showinfo("Info", "No settings file found. Save settings first!")

    def save_error_settings(self):
        # Saves the user-entered settings to ErrSet.py
        try:
            #EMPTY INPUT VALIDATION
            if not self.timeout_entry.get().strip():
                tkinter.messagebox.showerror("Error", "Please enter Timeout value!")
                return
            if not self.send_buf_entry.get().strip():
                tkinter.messagebox.showerror("Error", "Please enter Send Buffer value!")
                return
            if not self.recv_buf_entry.get().strip():
                tkinter.messagebox.showerror("Error", "Please enter Receive Buffer value!")
                return
           #SAVE SETTINGS
            timeout_val = self.timeout_entry.get().strip()
            ErrSet.settings['timeout'] = None if timeout_val.lower() == 'none' else float(timeout_val)

            ErrSet.settings['send_buf'] = int(self.send_buf_entry.get())
            ErrSet.settings['recv_buf'] = int(self.recv_buf_entry.get())

            ErrSet.settings['blocking'] = self.blocking_var.get()
            ErrSet.settings['enable_logging'] = self.logging_var.get()
            ErrSet.settings['handle_errors'] = self.error_handling_var.get()
            ErrSet.save()

            self.refresh_error_log()

            tkinter.messagebox.showinfo("Success", "Settings saved to settings.txt!")
        except Exception as e:
            tkinter.messagebox.showerror("Error", str(e))


#MAIN GUI CLASS
class NetworkDiagnosticGUI:
    """
      Main application class
      - Menu management
      - Module loading
      - General interface layout
      """
    def __init__(self, root):

        # Initializes the main window and sets up the basic layout

        self.root = root
        self.root.title("Network Diagnostic Tool")
        self.root.geometry("1000x650")
        self.root.configure(bg='#1a1a2e')

        # STATE VARIABLES
        self.menu_visible = False
        self.selected_module = None
        self.current_module_instance = None

        # Modül mapping'i
        self.modules = {
            "machine_info": MachineInfoModule,
            "echo_test": EchoTestModule,
            "sntp_time": SntpModule,
            "chat_module": ChatModule,
            "error_manager": ErrorManagerModule
        }

        # MAIN CONTAINER
        self.main_container = tk.Frame(root, bg='#1a1a2e')
        self.main_container.pack(fill=tk.BOTH, expand=True)

        # Header
        self.create_header()

        # Content area
        self.content_frame = tk.Frame(self.main_container, bg='#f5f5f5')
        self.content_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Welcome message
        self.show_welcome()

    def create_header(self):
        #Creates the top header bar.

        self.header = tk.Frame(self.main_container, bg='#16213e', height=60)
        self.header.pack(side=tk.TOP, fill=tk.X)
        self.header.pack_propagate(False)

        #MAIN MENU BUTTON
        self.menu_btn = tk.Button(
            self.header,
            text="☰ Main menü",
            font=('Segoe UI', 12, 'bold'),
            bg='#0f3460',
            fg='#e94560',
            bd=0,
            padx=25,
            pady=15,
            cursor='hand2',
            activebackground='#e94560',
            activeforeground='white',
            command=self.toggle_menu
        )
        self.menu_btn.pack(side=tk.LEFT, padx=15, pady=10)

        # Hover efect
        self.menu_btn.bind('<Enter>', lambda e: self.menu_btn.config(bg='#e94560', fg='white'))
        self.menu_btn.bind('<Leave>', lambda e: self.menu_btn.config(bg='#0f3460', fg='#e94560'))

    def toggle_menu(self):
        #Opens or closes the sidebar menu.
        if self.menu_visible:
            self.hide_menu()
        else:
            self.show_menu()

    def show_menu(self):
        #  Displays the sidebar menu
        if self.menu_visible:
            return


        self.clear_content()

        self.menu_visible = True

        # Sidebar frame
        self.sidebar = tk.Frame(self.main_container, bg='#16213e', width=240)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y, before=self.content_frame)
        self.sidebar.pack_propagate(False)

        # MENU HEADER
        menu_header = tk.Frame(self.sidebar, bg='#0f3460', height=50)
        menu_header.pack(fill=tk.X, pady=(0, 2))
        menu_header.pack_propagate(False)

        header_label = tk.Label(
            menu_header,
            text="Main Menu",
            font=('Segoe UI', 13, 'bold'),
            bg='#0f3460',
            fg='white'
        )
        header_label.pack(pady=12)

        # Each menu item
        self.menu_items = [
            ("machine_info", "Machine Info", "📊"),
            ("echo_test", "Echo Test", "🔄"),
            ("sntp_time", "SNTP Time", "⏰"),
            ("chat_module", "Chat Module", "💬"),
            ("error_manager", "Error and Setting Manager", "⚙️")
        ]

        for item_id, item_text, icon in self.menu_items:
            self.create_menu_item(item_id, f"{icon}  {item_text}")

    def create_menu_item(self, item_id, text):
        # Creates a single sidebar menu item

        # Outer frame for button
        btn_frame = tk.Frame(self.sidebar, bg='#16213e')
        btn_frame.pack(fill=tk.X, pady=1)

        btn = tk.Button(
            btn_frame,
            text=text,
            font=('Segoe UI', 11),
            bg='#16213e',
            fg='white',
            bd=0,
            padx=20,
            pady=15,
            anchor='w',
            cursor='hand2',
            activebackground='#e94560',
            activeforeground='white',
            command=lambda: self.load_module(item_id, text)
        )
        btn.pack(fill=tk.BOTH, expand=True)

        # Hover efekct
        def on_enter(e):
            if self.selected_module != item_id:
                btn.config(bg='#0f3460')

        def on_leave(e):
            if self.selected_module != item_id:
                btn.config(bg='#16213e')

        btn.bind('<Enter>', on_enter)
        btn.bind('<Leave>', on_leave)

        # STORE BUTTON REFERENCE
        if not hasattr(self, 'menu_buttons'):
            self.menu_buttons = {}
        self.menu_buttons[item_id] = btn

    def hide_menu(self):
        # Hides the sidebar menu
        if hasattr(self, 'sidebar'):
            self.sidebar.destroy()
        self.menu_visible = False
        if hasattr(self, 'menu_buttons'):
            self.menu_buttons = {}

    def show_welcome(self):
        # Displays the welcome message.
        self.clear_content()

        welcome_container = tk.Frame(self.content_frame, bg='#f5f5f5')
        welcome_container.pack(fill=tk.BOTH, expand=True)

        # center frame
        center_frame = tk.Frame(welcome_container, bg='white', relief=tk.FLAT)
        center_frame.place(relx=0.5, rely=0.5, anchor='center')

        top_line = tk.Frame(center_frame, bg='#e94560', height=4, width=80)
        top_line.pack(pady=(20, 15))

        welcome_text = tk.Label(
            center_frame,
            text="Please select an operation\nfrom the\nMain Menu",
            font=('Segoe UI', 32, 'bold'),
            bg='white',
            fg='#16213e',
            justify='center'
        )
        welcome_text.pack(padx=80, pady=20)

        # line of bottom
        bottom_line = tk.Frame(center_frame, bg='#0f3460', height=4, width=80)
        bottom_line.pack(pady=(15, 20))

    def clear_content(self):
        #Clears all widgets inside the content area.
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def load_module(self, module_id, module_name):
        #Loads and displays the selected module.
        self.selected_module = module_id

        #  UPDATE MENU BUTTON COLORS
        if hasattr(self, 'menu_buttons'):
            for btn_id, btn in self.menu_buttons.items():
                if btn_id == module_id:
                    btn.config(bg='#e94560', fg='white')
                else:
                    btn.config(bg='#16213e', fg='white')

        self.clear_content()

        module_container = tk.Frame(self.content_frame, bg='#f5f5f5')
        module_container.pack(fill=tk.BOTH, expand=True, padx=30, pady=25)

        title_frame = tk.Frame(module_container, bg='#f5f5f5')
        title_frame.pack(fill=tk.X, pady=(0, 25))

        accent = tk.Frame(title_frame, bg='#e94560', width=5, height=35)
        accent.pack(side=tk.LEFT, padx=(0, 15))

        title = tk.Label(
            title_frame,
            text=module_name,
            font=('Segoe UI', 24, 'bold'),
            bg='#f5f5f5',
            fg='#16213e'
        )
        title.pack(side=tk.LEFT)

        #MODULE CONTENT AREA
        self.module_content = tk.Frame(
            module_container,
            bg='white',
            relief=tk.FLAT,
            highlightbackground='#e0e0e0',
            highlightthickness=1
        )
        self.module_content.pack(fill=tk.BOTH, expand=True)

        # If another module is open, clear it first
        if self.current_module_instance:
            self.current_module_instance.clear()

        #  LOAD NEW MODULE
        module_class = self.modules.get(module_id)
        if module_class:
            self.current_module_instance = module_class(self.module_content, self.root)
            self.current_module_instance.render()
        else:
            self.show_placeholder(module_name)

        self.current_module = module_id

    def show_placeholder(self, module_name):
        #Displays a placeholder if the module is not yet implemented.
        placeholder_frame = tk.Frame(self.module_content, bg='white')
        placeholder_frame.place(relx=0.5, rely=0.5, anchor='center')

        icon_label = tk.Label(
            placeholder_frame,
            text="🔧",
            font=('Segoe UI', 48),
            bg='white'
        )
        icon_label.pack(pady=(0, 15))

        placeholder = tk.Label(
            placeholder_frame,
            text=f"{module_name} modülü içeriği\nburada gösterilecek...",
            font=('Segoe UI', 13),
            bg='white',
            fg='#666666',
            justify='center'
        )
        placeholder.pack()

    def get_content_frame(self):

             #Returns the module content frame.


        return self.module_content if hasattr(self, 'module_content') else None


if __name__ == "__main__":
    root = tk.Tk()
    app = NetworkDiagnosticGUI(root)
    root.mainloop()