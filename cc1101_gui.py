import customtkinter as ctk
from tkinter import messagebox
import serial
import serial.tools.list_ports
import threading
import time

# Modern theme settings
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class CC1101GUI:
    def __init__(self, root):
        self.root = root
        self.root.title("CC1101 RF Controller")
        self.root.geometry("1200x800")

        # Color scheme
        self.colors = {
            'primary': '#1f538d',
            'success': '#2ecc71',
            'danger': '#e74c3c',
            'warning': '#f39c12',
            'info': '#3498db',
            'dark': '#1a1a1a',
            'light': '#ecf0f1'
        }

        self.serial_port = None
        self.is_connected = False
        self.rx_thread = None
        self.rx_running = False

        self.create_widgets()

    def create_widgets(self):
        # Main container with grid layout
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=1)

        # Top connection bar
        self.create_connection_frame()

        # Main content area
        content_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        content_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        content_frame.grid_columnconfigure(0, weight=1)
        content_frame.grid_rowconfigure(0, weight=1)

        # Tabview for different sections
        self.tabview = ctk.CTkTabview(content_frame, corner_radius=10)
        self.tabview.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        # Create tabs
        self.tabview.add("⚙️ RF Config")
        self.tabview.add("📦 Packet")
        self.tabview.add("🔄 Operations")
        self.tabview.add("💾 Recording")
        self.tabview.add("⚡ Advanced")

        self.create_rf_config_tab()
        self.create_packet_config_tab()
        self.create_operations_tab()
        self.create_recording_tab()
        self.create_advanced_tab()

        # Terminal at bottom
        self.create_terminal(content_frame)

    def create_connection_frame(self):
        conn_frame = ctk.CTkFrame(self.root, corner_radius=10, height=80)
        conn_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        conn_frame.grid_propagate(False)

        # Serial settings
        ctk.CTkLabel(conn_frame, text="COM Port:", font=("Segoe UI", 13, "bold")).grid(row=0, column=0, padx=(20, 5), pady=20)

        self.port_var = ctk.StringVar()
        self.port_combo = ctk.CTkComboBox(conn_frame, variable=self.port_var, width=150, command=lambda x: None)
        self.port_combo.grid(row=0, column=1, padx=5, pady=20)
        self.refresh_ports()

        refresh_btn = ctk.CTkButton(conn_frame, text="🔄", width=40, command=self.refresh_ports)
        refresh_btn.grid(row=0, column=2, padx=5)

        ctk.CTkLabel(conn_frame, text="Baud:", font=("Segoe UI", 13, "bold")).grid(row=0, column=3, padx=(20, 5))
        self.baud_var = ctk.StringVar(value="115200")
        baud_combo = ctk.CTkComboBox(conn_frame, variable=self.baud_var, width=120,
                                     values=["9600", "19200", "38400", "57600", "115200"])
        baud_combo.grid(row=0, column=4, padx=5)

        # Connect button
        self.connect_btn = ctk.CTkButton(conn_frame, text="Connect", width=120,
                                        command=self.toggle_connection,
                                        fg_color=self.colors['success'],
                                        hover_color="#27ae60")
        self.connect_btn.grid(row=0, column=5, padx=20)

        # Status indicator
        self.status_label = ctk.CTkLabel(conn_frame, text="⚫ Disconnected",
                                        font=("Segoe UI", 13, "bold"),
                                        text_color=self.colors['danger'])
        self.status_label.grid(row=0, column=6, padx=10)

        # Init button
        init_btn = ctk.CTkButton(conn_frame, text="Init CC1101", width=120,
                                command=lambda: self.send_command("init"),
                                fg_color=self.colors['warning'],
                                hover_color="#e67e22")
        init_btn.grid(row=0, column=7, padx=10)

    def create_rf_config_tab(self):
        tab = self.tabview.tab("⚙️ RF Config")

        # Create scrollable frame
        scroll = ctk.CTkScrollableFrame(tab, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=10, pady=10)

        # Left and right columns
        left_frame = ctk.CTkFrame(scroll, corner_radius=10)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        right_frame = ctk.CTkFrame(scroll, corner_radius=10)
        right_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)

        scroll.grid_columnconfigure(0, weight=1)
        scroll.grid_columnconfigure(1, weight=1)

        # FREQUENCY SETTINGS
        ctk.CTkLabel(left_frame, text="📡 Frequency Settings",
                    font=("Segoe UI", 16, "bold")).grid(row=0, column=0, columnspan=3, pady=(15, 10), padx=15, sticky="w")

        row = 1
        self.create_setting_row(left_frame, row, "Frequency (MHz):", "433.92",
                              lambda: self.send_command(f"setmhz {self.freq_var.get()}"),
                              "300-348, 387-464, 779-928")
        self.freq_var = self.last_var

        row += 1
        self.create_combo_row(left_frame, row, "Modulation:",
                            ["0 - 2-FSK", "1 - GFSK", "2 - ASK/OOK", "3 - 4-FSK", "4 - MSK"],
                            "0 - 2-FSK",
                            lambda: self.send_command(f"setmodulation {self.mod_var.get().split()[0]}"))
        self.mod_var = self.last_var

        row += 1
        self.create_setting_row(left_frame, row, "Deviation (kHz):", "47.60",
                              lambda: self.send_command(f"setdeviation {self.dev_var.get()}"),
                              "1.58 - 380.85")
        self.dev_var = self.last_var

        row += 1
        self.create_setting_row(left_frame, row, "Channel:", "0",
                              lambda: self.send_command(f"setchannel {self.chan_var.get()}"),
                              "0-255")
        self.chan_var = self.last_var

        row += 1
        self.create_setting_row(left_frame, row, "Ch. Spacing (kHz):", "199.95",
                              lambda: self.send_command(f"setchsp {self.chsp_var.get()}"),
                              "25.39 - 405.45")
        self.chsp_var = self.last_var

        # POWER & DATA RATE
        ctk.CTkLabel(right_frame, text="⚡ Power & Data Rate",
                    font=("Segoe UI", 16, "bold")).grid(row=0, column=0, columnspan=3, pady=(15, 10), padx=15, sticky="w")

        row = 1
        self.create_combo_row(right_frame, row, "TX Power (dBm):",
                            ["-30", "-20", "-15", "-10", "-6", "0", "5", "7", "10", "11", "12"],
                            "12",
                            lambda: self.send_command(f"setpa {self.pa_var.get()}"))
        self.pa_var = self.last_var

        row += 1
        self.create_setting_row(right_frame, row, "RX Bandwidth (kHz):", "203.125",
                              lambda: self.send_command(f"setrxbw {self.rxbw_var.get()}"),
                              "58.03 - 812.50")
        self.rxbw_var = self.last_var

        row += 1
        self.create_setting_row(right_frame, row, "Data Rate (kBaud):", "99.97",
                              lambda: self.send_command(f"setdrate {self.drate_var.get()}"),
                              "0.02 - 1621.83")
        self.drate_var = self.last_var

    def create_packet_config_tab(self):
        tab = self.tabview.tab("📦 Packet")

        scroll = ctk.CTkScrollableFrame(tab, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=10, pady=10)

        # Sync & Address
        sync_frame = ctk.CTkFrame(scroll, corner_radius=10)
        sync_frame.pack(fill="x", padx=5, pady=5)

        ctk.CTkLabel(sync_frame, text="🔗 Sync & Address",
                    font=("Segoe UI", 16, "bold")).grid(row=0, column=0, columnspan=4, pady=(15, 10), padx=15, sticky="w")

        row = 1
        self.create_combo_row(sync_frame, row, "Sync Mode:",
                            ["0 - No preamble/sync", "1 - 16 sync bits", "2 - 16/16 sync bits",
                             "3 - 30/32 sync bits", "4 - No sync + CS", "5 - 15/16 + CS",
                             "6 - 16/16 + CS", "7 - 30/32 + CS"],
                            "2 - 16/16 sync bits",
                            lambda: self.send_command(f"setsyncmode {self.syncmode_var.get().split()[0]}"))
        self.syncmode_var = self.last_var

        row += 1
        ctk.CTkLabel(sync_frame, text="Sync Word:", font=("Segoe UI", 12)).grid(row=row, column=0, sticky="w", padx=15, pady=10)
        self.syncword_low = ctk.StringVar(value="211")
        self.syncword_high = ctk.StringVar(value="145")
        ctk.CTkEntry(sync_frame, textvariable=self.syncword_low, width=80).grid(row=row, column=1, padx=5)
        ctk.CTkEntry(sync_frame, textvariable=self.syncword_high, width=80).grid(row=row, column=2, padx=5)
        ctk.CTkButton(sync_frame, text="Set", width=80,
                     command=lambda: self.send_command(f"setsyncword {self.syncword_low.get()} {self.syncword_high.get()}")
                     ).grid(row=row, column=3, padx=15)

        row += 1
        self.create_combo_row(sync_frame, row, "Address Check:",
                            ["0 - No check", "1 - Address check",
                             "2 - Addr + 0 broadcast", "3 - Addr + 0,255 broadcast"],
                            "0 - No check",
                            lambda: self.send_command(f"setadrchk {self.adrchk_var.get().split()[0]}"))
        self.adrchk_var = self.last_var

        row += 1
        self.create_setting_row(sync_frame, row, "Device Address:", "0",
                              lambda: self.send_command(f"setaddr {self.addr_var.get()}"))
        self.addr_var = self.last_var

        # Packet Format
        pkt_frame = ctk.CTkFrame(scroll, corner_radius=10)
        pkt_frame.pack(fill="x", padx=5, pady=5)

        ctk.CTkLabel(pkt_frame, text="📋 Packet Format",
                    font=("Segoe UI", 16, "bold")).grid(row=0, column=0, columnspan=3, pady=(15, 10), padx=15, sticky="w")

        row = 1
        self.create_combo_row(pkt_frame, row, "Format:",
                            ["0 - Normal", "1 - Sync serial", "2 - Random TX", "3 - Async serial"],
                            "0 - Normal",
                            lambda: self.send_command(f"setpktformat {self.pktfmt_var.get().split()[0]}"))
        self.pktfmt_var = self.last_var

        row += 1
        self.create_combo_row(pkt_frame, row, "Length Mode:",
                            ["0 - Fixed", "1 - Variable", "2 - Infinite"],
                            "1 - Variable",
                            lambda: self.send_command(f"setlengthconfig {self.lencfg_var.get().split()[0]}"))
        self.lencfg_var = self.last_var

        row += 1
        self.create_setting_row(pkt_frame, row, "Packet Length:", "61",
                              lambda: self.send_command(f"setpacketlength {self.pktlen_var.get()}"))
        self.pktlen_var = self.last_var

        row += 1
        self.create_combo_row(pkt_frame, row, "Preamble:",
                            ["0 - 2 bytes", "1 - 3 bytes", "2 - 4 bytes", "3 - 6 bytes",
                             "4 - 8 bytes", "5 - 12 bytes", "6 - 16 bytes", "7 - 24 bytes"],
                            "2 - 4 bytes",
                            lambda: self.send_command(f"setpre {self.pre_var.get().split()[0]}"))
        self.pre_var = self.last_var

        # Options
        opt_frame = ctk.CTkFrame(scroll, corner_radius=10)
        opt_frame.pack(fill="x", padx=5, pady=5)

        ctk.CTkLabel(opt_frame, text="⚙️ Options",
                    font=("Segoe UI", 16, "bold")).grid(row=0, column=0, columnspan=4, pady=(15, 10), padx=15, sticky="w")

        # Checkboxes in grid
        row = 1
        self.crc_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(opt_frame, text="CRC", variable=self.crc_var,
                       command=lambda: self.send_command(f"setcrc {1 if self.crc_var.get() else 0}")
                       ).grid(row=row, column=0, padx=15, pady=5, sticky="w")

        self.crcaf_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(opt_frame, text="CRC AutoFlush", variable=self.crcaf_var,
                       command=lambda: self.send_command(f"setcrcaf {1 if self.crcaf_var.get() else 0}")
                       ).grid(row=row, column=1, padx=15, pady=5, sticky="w")

        self.white_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(opt_frame, text="Data Whitening", variable=self.white_var,
                       command=lambda: self.send_command(f"setwhitedata {1 if self.white_var.get() else 0}")
                       ).grid(row=row, column=2, padx=15, pady=5, sticky="w")

        row += 1
        self.manch_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(opt_frame, text="Manchester", variable=self.manch_var,
                       command=lambda: self.send_command(f"setmanchester {1 if self.manch_var.get() else 0}")
                       ).grid(row=row, column=0, padx=15, pady=5, sticky="w")

        self.fec_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(opt_frame, text="FEC", variable=self.fec_var,
                       command=lambda: self.send_command(f"setfec {1 if self.fec_var.get() else 0}")
                       ).grid(row=row, column=1, padx=15, pady=5, sticky="w")

        self.dcfilt_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(opt_frame, text="DC Filter Off", variable=self.dcfilt_var,
                       command=lambda: self.send_command(f"setdcfilteroff {1 if self.dcfilt_var.get() else 0}")
                       ).grid(row=row, column=2, padx=15, pady=5, sticky="w")

        row += 1
        self.appstat_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(opt_frame, text="Append Status", variable=self.appstat_var,
                       command=lambda: self.send_command(f"setappendstatus {1 if self.appstat_var.get() else 0}")
                       ).grid(row=row, column=0, padx=15, pady=(5, 15), sticky="w")

        ctk.CTkLabel(opt_frame, text="PQT:", font=("Segoe UI", 12)).grid(row=row, column=1, sticky="e", padx=5)
        self.pqt_var = ctk.StringVar(value="0")
        pqt_entry = ctk.CTkEntry(opt_frame, textvariable=self.pqt_var, width=60)
        pqt_entry.grid(row=row, column=2, sticky="w", padx=5)
        ctk.CTkButton(opt_frame, text="Set", width=60,
                     command=lambda: self.send_command(f"setpqt {self.pqt_var.get()}")
                     ).grid(row=row, column=3, padx=(5, 15), pady=(5, 15))

    def create_operations_tab(self):
        tab = self.tabview.tab("🔄 Operations")

        scroll = ctk.CTkScrollableFrame(tab, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=10, pady=10)

        # TX Frame
        tx_frame = ctk.CTkFrame(scroll, corner_radius=10)
        tx_frame.pack(fill="x", padx=5, pady=5)

        ctk.CTkLabel(tx_frame, text="📤 Transmit",
                    font=("Segoe UI", 16, "bold")).grid(row=0, column=0, columnspan=3, pady=(15, 10), padx=15, sticky="w")

        ctk.CTkLabel(tx_frame, text="TX Data (hex):", font=("Segoe UI", 12)).grid(row=1, column=0, sticky="w", padx=15, pady=10)
        self.tx_data = ctk.StringVar()
        ctk.CTkEntry(tx_frame, textvariable=self.tx_data, width=500).grid(row=1, column=1, padx=10)
        ctk.CTkButton(tx_frame, text="Send", width=100, command=self.send_tx,
                     fg_color=self.colors['success'], hover_color="#27ae60").grid(row=1, column=2, padx=15)

        ctk.CTkLabel(tx_frame, text="Max 60 bytes", font=("Segoe UI", 10),
                    text_color="gray").grid(row=2, column=1, sticky="w", padx=10, pady=(0, 15))

        # RX Frame
        rx_frame = ctk.CTkFrame(scroll, corner_radius=10)
        rx_frame.pack(fill="x", padx=5, pady=5)

        ctk.CTkLabel(rx_frame, text="📥 Receive",
                    font=("Segoe UI", 16, "bold")).grid(row=0, column=0, columnspan=4, pady=(15, 10), padx=15, sticky="w")

        self.rx_btn = ctk.CTkButton(rx_frame, text="▶ Start RX Sniffer", width=150,
                                    command=self.toggle_rx,
                                    fg_color=self.colors['info'], hover_color="#2980b9")
        self.rx_btn.grid(row=1, column=0, padx=15, pady=(10, 15))

        ctk.CTkButton(rx_frame, text="📊 Get RSSI", width=120,
                     command=lambda: self.send_command("getrssi")).grid(row=1, column=1, padx=10, pady=(10, 15))

        ctk.CTkButton(rx_frame, text="⏹ Stop (x)", width=100,
                     command=lambda: self.send_command("x"),
                     fg_color=self.colors['danger'], hover_color="#c0392b").grid(row=1, column=2, padx=10, pady=(10, 15))

        # Scan Frame
        scan_frame = ctk.CTkFrame(scroll, corner_radius=10)
        scan_frame.pack(fill="x", padx=5, pady=5)

        ctk.CTkLabel(scan_frame, text="🔍 Frequency Scan",
                    font=("Segoe UI", 16, "bold")).grid(row=0, column=0, columnspan=4, pady=(15, 10), padx=15, sticky="w")

        ctk.CTkLabel(scan_frame, text="Start (MHz):", font=("Segoe UI", 12)).grid(row=1, column=0, sticky="e", padx=15, pady=10)
        self.scan_start = ctk.StringVar(value="433.0")
        ctk.CTkEntry(scan_frame, textvariable=self.scan_start, width=100).grid(row=1, column=1, padx=10)

        ctk.CTkLabel(scan_frame, text="Stop (MHz):", font=("Segoe UI", 12)).grid(row=1, column=2, sticky="e", padx=15)
        self.scan_stop = ctk.StringVar(value="434.0")
        ctk.CTkEntry(scan_frame, textvariable=self.scan_stop, width=100).grid(row=1, column=3, padx=10)

        ctk.CTkButton(scan_frame, text="🔍 Start Scan", width=150,
                     command=self.start_scan,
                     fg_color=self.colors['warning'], hover_color="#e67e22").grid(row=2, column=0, columnspan=4, pady=(10, 15))

        # Chat Frame
        chat_frame = ctk.CTkFrame(scroll, corner_radius=10)
        chat_frame.pack(fill="x", padx=5, pady=5)

        ctk.CTkLabel(chat_frame, text="💬 Chat Mode",
                    font=("Segoe UI", 16, "bold")).grid(row=0, column=0, columnspan=2, pady=(15, 10), padx=15, sticky="w")

        ctk.CTkButton(chat_frame, text="💬 Enable Chat", width=150,
                     command=lambda: self.send_command("chat")).grid(row=1, column=0, padx=15, pady=(10, 10))

        ctk.CTkLabel(chat_frame, text="⚠️ No exit available, disconnect device to quit",
                    font=("Segoe UI", 11), text_color=self.colors['danger']).grid(row=1, column=1, padx=10, pady=(10, 10), sticky="w")

    def create_recording_tab(self):
        tab = self.tabview.tab("💾 Recording")

        scroll = ctk.CTkScrollableFrame(tab, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=10, pady=10)

        # Normal Recording
        norm_frame = ctk.CTkFrame(scroll, corner_radius=10)
        norm_frame.pack(fill="x", padx=5, pady=5)

        ctk.CTkLabel(norm_frame, text="⏺️ Normal Recording",
                    font=("Segoe UI", 16, "bold")).grid(row=0, column=0, columnspan=4, pady=(15, 10), padx=15, sticky="w")

        self.rec_btn = ctk.CTkButton(norm_frame, text="▶ Start Recording", width=150,
                                     command=self.toggle_rec,
                                     fg_color=self.colors['danger'], hover_color="#c0392b")
        self.rec_btn.grid(row=1, column=0, padx=15, pady=10)

        ctk.CTkButton(norm_frame, text="📋 Show Buffer", width=120,
                     command=lambda: self.send_command("show")).grid(row=1, column=1, padx=10)

        ctk.CTkButton(norm_frame, text="🗑️ Flush", width=100,
                     command=lambda: self.send_command("flush")).grid(row=1, column=2, padx=10)

        ctk.CTkLabel(norm_frame, text="Add Frame:", font=("Segoe UI", 12)).grid(row=2, column=0, sticky="w", padx=15, pady=10)
        self.add_frame = ctk.StringVar()
        ctk.CTkEntry(norm_frame, textvariable=self.add_frame, width=350).grid(row=2, column=1, columnspan=2, padx=10)
        ctk.CTkButton(norm_frame, text="Add", width=80,
                     command=lambda: self.send_command(f"add {self.add_frame.get()}")
                     ).grid(row=2, column=3, padx=15)

        ctk.CTkLabel(norm_frame, text="Play Frame #:", font=("Segoe UI", 12)).grid(row=3, column=0, sticky="w", padx=15, pady=(10, 15))
        self.play_n = ctk.StringVar(value="0")
        ctk.CTkEntry(norm_frame, textvariable=self.play_n, width=100).grid(row=3, column=1, sticky="w", padx=10)
        ctk.CTkButton(norm_frame, text="▶ Play", width=100,
                     command=lambda: self.send_command(f"play {self.play_n.get()}"),
                     fg_color=self.colors['success'], hover_color="#27ae60").grid(row=3, column=2, sticky="w", padx=10)
        ctk.CTkLabel(norm_frame, text="(0 = all frames)", font=("Segoe UI", 10),
                    text_color="gray").grid(row=3, column=3, sticky="w", padx=15, pady=(10, 15))

        # RAW Recording
        raw_frame = ctk.CTkFrame(scroll, corner_radius=10)
        raw_frame.pack(fill="x", padx=5, pady=5)

        ctk.CTkLabel(raw_frame, text="📡 RAW Recording",
                    font=("Segoe UI", 16, "bold")).grid(row=0, column=0, columnspan=4, pady=(15, 10), padx=15, sticky="w")

        ctk.CTkLabel(raw_frame, text="Sample Interval (μs):", font=("Segoe UI", 12)).grid(row=1, column=0, sticky="w", padx=15, pady=10)
        self.raw_interval = ctk.StringVar(value="100")
        ctk.CTkEntry(raw_frame, textvariable=self.raw_interval, width=100).grid(row=1, column=1, padx=10)

        ctk.CTkButton(raw_frame, text="RX RAW", width=100,
                     command=lambda: self.send_command(f"rxraw {self.raw_interval.get()}")
                     ).grid(row=1, column=2, padx=10)

        ctk.CTkButton(raw_frame, text="⏺️ Record RAW", width=120,
                     command=lambda: self.send_command(f"recraw {self.raw_interval.get()}")
                     ).grid(row=1, column=3, padx=15)

        ctk.CTkLabel(raw_frame, text="Add RAW:", font=("Segoe UI", 12)).grid(row=2, column=0, sticky="w", padx=15, pady=10)
        self.addraw_data = ctk.StringVar()
        ctk.CTkEntry(raw_frame, textvariable=self.addraw_data, width=350).grid(row=2, column=1, columnspan=2, padx=10)
        ctk.CTkButton(raw_frame, text="Add", width=80,
                     command=lambda: self.send_command(f"addraw {self.addraw_data.get()}")
                     ).grid(row=2, column=3, padx=15)

        btn_row_frame = ctk.CTkFrame(raw_frame, fg_color="transparent")
        btn_row_frame.grid(row=3, column=0, columnspan=4, pady=10)

        ctk.CTkButton(btn_row_frame, text="📋 Show RAW", width=120,
                     command=lambda: self.send_command("showraw")).pack(side="left", padx=5)
        ctk.CTkButton(btn_row_frame, text="🔢 Show Bits", width=120,
                     command=lambda: self.send_command("showbit")).pack(side="left", padx=5)

        ctk.CTkLabel(raw_frame, text="Play Interval (μs):", font=("Segoe UI", 12)).grid(row=4, column=0, sticky="w", padx=15, pady=(10, 15))
        self.playraw_interval = ctk.StringVar(value="100")
        ctk.CTkEntry(raw_frame, textvariable=self.playraw_interval, width=100).grid(row=4, column=1, padx=10, pady=(10, 15))
        ctk.CTkButton(raw_frame, text="▶ Play RAW", width=120,
                     command=lambda: self.send_command(f"playraw {self.playraw_interval.get()}"),
                     fg_color=self.colors['success'], hover_color="#27ae60").grid(row=4, column=2, columnspan=2, padx=10, pady=(10, 15))

        # Memory
        mem_frame = ctk.CTkFrame(scroll, corner_radius=10)
        mem_frame.pack(fill="x", padx=5, pady=5)

        ctk.CTkLabel(mem_frame, text="💿 Non-Volatile Memory",
                    font=("Segoe UI", 16, "bold")).grid(row=0, column=0, columnspan=2, pady=(15, 10), padx=15, sticky="w")

        ctk.CTkButton(mem_frame, text="💾 Save to Memory", width=150,
                     command=lambda: self.send_command("save")).grid(row=1, column=0, padx=15, pady=(10, 15))
        ctk.CTkButton(mem_frame, text="📂 Load from Memory", width=150,
                     command=lambda: self.send_command("load")).grid(row=1, column=1, padx=15, pady=(10, 15))

    def create_advanced_tab(self):
        tab = self.tabview.tab("⚡ Advanced")

        scroll = ctk.CTkScrollableFrame(tab, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=10, pady=10)

        # Jamming
        jam_frame = ctk.CTkFrame(scroll, corner_radius=10, fg_color="#2c1810")
        jam_frame.pack(fill="x", padx=5, pady=5)

        ctk.CTkLabel(jam_frame, text="⚠️ Jamming",
                    font=("Segoe UI", 16, "bold"), text_color="#ff6b6b").grid(row=0, column=0, columnspan=2, pady=(15, 10), padx=15, sticky="w")

        self.jam_btn = ctk.CTkButton(jam_frame, text="⚠️ Start Jamming", width=150,
                                     command=self.toggle_jam,
                                     fg_color=self.colors['danger'], hover_color="#c0392b")
        self.jam_btn.grid(row=1, column=0, padx=15, pady=(10, 10))

        ctk.CTkLabel(jam_frame, text="Continuous jamming on selected band",
                    font=("Segoe UI", 11), text_color="#ff9999").grid(row=1, column=1, padx=10, pady=(10, 10), sticky="w")

        ctk.CTkLabel(jam_frame, text="⚠️ May be illegal in your jurisdiction. Use responsibly.",
                    font=("Segoe UI", 10, "bold"), text_color=self.colors['warning']).grid(row=2, column=0, columnspan=2, padx=15, pady=(0, 15))

        # Brute Force
        brute_frame = ctk.CTkFrame(scroll, corner_radius=10, fg_color="#1a1a2e")
        brute_frame.pack(fill="x", padx=5, pady=5)

        ctk.CTkLabel(brute_frame, text="🔓 Brute Force",
                    font=("Segoe UI", 16, "bold"), text_color="#ffa500").grid(row=0, column=0, columnspan=3, pady=(15, 10), padx=15, sticky="w")

        ctk.CTkLabel(brute_frame, text="Symbol Time (μs):", font=("Segoe UI", 12)).grid(row=1, column=0, sticky="w", padx=15, pady=10)
        self.brute_usec = ctk.StringVar(value="400")
        ctk.CTkEntry(brute_frame, textvariable=self.brute_usec, width=100).grid(row=1, column=1, padx=10)

        ctk.CTkLabel(brute_frame, text="Number of Bits:", font=("Segoe UI", 12)).grid(row=2, column=0, sticky="w", padx=15, pady=10)
        self.brute_bits = ctk.StringVar(value="12")
        ctk.CTkEntry(brute_frame, textvariable=self.brute_bits, width=100).grid(row=2, column=1, padx=10)

        ctk.CTkButton(brute_frame, text="🔓 Start Brute Force", width=150,
                     command=self.start_brute,
                     fg_color=self.colors['warning'], hover_color="#e67e22").grid(row=3, column=0, columnspan=2, pady=10)

        ctk.CTkLabel(brute_frame, text="⚠️ This will transmit many packets. Use only on authorized systems.",
                    font=("Segoe UI", 10, "bold"), text_color=self.colors['warning']).grid(row=4, column=0, columnspan=3, padx=15, pady=(0, 15))

        # Settings
        settings_frame = ctk.CTkFrame(scroll, corner_radius=10)
        settings_frame.pack(fill="x", padx=5, pady=5)

        ctk.CTkLabel(settings_frame, text="⚙️ Settings",
                    font=("Segoe UI", 16, "bold")).grid(row=0, column=0, columnspan=2, pady=(15, 10), padx=15, sticky="w")

        self.echo_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(settings_frame, text="Enable Echo on Serial Terminal", variable=self.echo_var,
                       font=("Segoe UI", 12),
                       command=lambda: self.send_command(f"echo {1 if self.echo_var.get() else 0}")
                       ).grid(row=1, column=0, padx=15, pady=(10, 15), sticky="w")

    def create_terminal(self, parent):
        term_frame = ctk.CTkFrame(parent, corner_radius=10)
        term_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        parent.grid_rowconfigure(1, weight=1)

        # Header
        header = ctk.CTkFrame(term_frame, fg_color=self.colors['dark'], corner_radius=8)
        header.pack(fill="x", padx=5, pady=5)

        ctk.CTkLabel(header, text="💻 Terminal Output",
                    font=("Segoe UI", 14, "bold")).pack(side="left", padx=15, pady=8)

        ctk.CTkButton(header, text="📋 Copy", width=80, height=28,
                     command=self.copy_terminal).pack(side="right", padx=5)
        ctk.CTkButton(header, text="🗑️ Clear", width=80, height=28,
                     command=self.clear_terminal).pack(side="right", padx=5)

        # Terminal text widget
        self.terminal = ctk.CTkTextbox(term_frame, font=("Consolas", 11),
                                      fg_color="#0a0a0a", text_color="#00ff00",
                                      corner_radius=5)
        self.terminal.pack(fill="both", expand=True, padx=5, pady=(0, 5))

    # Helper functions for creating UI elements
    def create_setting_row(self, parent, row, label, default_val, callback, hint=""):
        ctk.CTkLabel(parent, text=label, font=("Segoe UI", 12)).grid(row=row, column=0, sticky="w", padx=15, pady=10)
        var = ctk.StringVar(value=default_val)
        ctk.CTkEntry(parent, textvariable=var, width=120).grid(row=row, column=1, padx=10)
        ctk.CTkButton(parent, text="Set", width=80, command=callback).grid(row=row, column=2, padx=15)
        if hint:
            ctk.CTkLabel(parent, text=hint, font=("Segoe UI", 10), text_color="gray").grid(row=row, column=3, sticky="w", padx=5)
        self.last_var = var
        return var

    def create_combo_row(self, parent, row, label, values, default, callback):
        ctk.CTkLabel(parent, text=label, font=("Segoe UI", 12)).grid(row=row, column=0, sticky="w", padx=15, pady=10)
        var = ctk.StringVar(value=default)
        combo = ctk.CTkComboBox(parent, variable=var, values=values, width=180)
        combo.grid(row=row, column=1, padx=10)
        ctk.CTkButton(parent, text="Set", width=80, command=callback).grid(row=row, column=2, padx=15)
        self.last_var = var
        return var

    # Serial communication methods
    def refresh_ports(self):
        ports = [port.device for port in serial.tools.list_ports.comports()]
        if ports:
            self.port_combo.configure(values=ports)
            if not self.port_var.get() and ports:
                self.port_combo.set(ports[0])
        else:
            self.port_combo.configure(values=["No ports found"])

    def toggle_connection(self):
        if not self.is_connected:
            self.connect()
        else:
            self.disconnect()

    def connect(self):
        try:
            port = self.port_var.get()
            baud = int(self.baud_var.get())

            if not port or port == "No ports found":
                messagebox.showerror("Error", "Please select a valid COM port")
                return

            self.serial_port = serial.Serial(port, baud, timeout=0.1)
            self.is_connected = True

            self.status_label.configure(text="🟢 Connected", text_color=self.colors['success'])
            self.connect_btn.configure(text="Disconnect", fg_color=self.colors['danger'], hover_color="#c0392b")
            self.port_combo.configure(state='disabled')

            # Start reading thread
            self.rx_running = True
            self.rx_thread = threading.Thread(target=self.read_serial, daemon=True)
            self.rx_thread.start()

            self.log_terminal(f"✓ Connected to {port} at {baud} baud\n")

        except Exception as e:
            messagebox.showerror("Connection Error", str(e))
            self.is_connected = False

    def disconnect(self):
        if self.serial_port:
            self.rx_running = False
            time.sleep(0.2)
            self.serial_port.close()
            self.serial_port = None

        self.is_connected = False
        self.status_label.configure(text="⚫ Disconnected", text_color=self.colors['danger'])
        self.connect_btn.configure(text="Connect", fg_color=self.colors['success'], hover_color="#27ae60")
        self.port_combo.configure(state='normal')

        self.log_terminal("✗ Disconnected\n")

    def read_serial(self):
        while self.rx_running and self.serial_port:
            try:
                if self.serial_port.in_waiting:
                    data = self.serial_port.read(self.serial_port.in_waiting)
                    try:
                        text = data.decode('utf-8', errors='replace')
                        self.log_terminal(text)
                    except:
                        self.log_terminal(f"[Binary: {data.hex()}]\n")
            except Exception as e:
                if self.rx_running:
                    self.log_terminal(f"⚠ Read error: {str(e)}\n")
                break
            time.sleep(0.01)

    def send_command(self, command):
        if not self.is_connected:
            messagebox.showwarning("Not Connected", "Please connect to a device first")
            return

        try:
            self.serial_port.write(f"{command}\n".encode('utf-8'))
            self.log_terminal(f"→ {command}\n")
        except Exception as e:
            messagebox.showerror("Send Error", str(e))

    def send_tx(self):
        data = self.tx_data.get().strip()
        if not data:
            messagebox.showwarning("Invalid Input", "Please enter hex data to transmit")
            return
        self.send_command(f"tx {data}")

    def toggle_rx(self):
        if "Start" in self.rx_btn.cget("text"):
            self.send_command("rx")
            self.rx_btn.configure(text="⏹ Stop RX Sniffer", fg_color=self.colors['danger'])
        else:
            self.send_command("x")
            self.rx_btn.configure(text="▶ Start RX Sniffer", fg_color=self.colors['info'])

    def toggle_rec(self):
        if "Start" in self.rec_btn.cget("text"):
            self.send_command("rec")
            self.rec_btn.configure(text="⏹ Stop Recording")
        else:
            self.send_command("x")
            self.rec_btn.configure(text="▶ Start Recording")

    def toggle_jam(self):
        if "Start" in self.jam_btn.cget("text"):
            self.send_command("jam")
            self.jam_btn.configure(text="⏹ Stop Jamming")
        else:
            self.send_command("x")
            self.jam_btn.configure(text="⚠️ Start Jamming")

    def start_scan(self):
        start = self.scan_start.get()
        stop = self.scan_stop.get()
        self.send_command(f"scan {start} {stop}")

    def start_brute(self):
        usec = self.brute_usec.get()
        bits = self.brute_bits.get()
        result = messagebox.askyesno("⚠️ Confirm",
                                     f"Start brute force attack?\n\nThis will transmit many packets.\n\nEnsure you have authorization.",
                                     icon='warning')
        if result:
            self.send_command(f"brute {usec} {bits}")

    def log_terminal(self, text):
        def append():
            self.terminal.insert("end", text)
            self.terminal.see("end")
        self.root.after(0, append)

    def clear_terminal(self):
        self.terminal.delete("1.0", "end")

    def copy_terminal(self):
        text = self.terminal.get("1.0", "end")
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        self.log_terminal("✓ Copied to clipboard\n")

def main():
    root = ctk.CTk()
    root.title("CC1101 RF Controller")

    # Set window icon (if you have one)
    try:
        root.iconbitmap("icon.ico")
    except:
        pass

    app = CC1101GUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
