import tkinter as tk
from tkinter import ttk

class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tipwindow = None
        self.id = None
        self.widget.bind("<Enter>", self.show_tip)
        self.widget.bind("<Leave>", self.hide_tip)

    def show_tip(self, event=None):
        self.unschedule()
        self.id = self.widget.after(500, self.show_window)

    def hide_tip(self, event=None):
        self.unschedule()
        if self.tipwindow:
            self.tipwindow.destroy()
            self.tipwindow = None

    def unschedule(self):
        id = self.id
        self.id = None
        if id:
            self.widget.after_cancel(id)

    def show_window(self):
        if self.tipwindow or not self.text: return
        try:
            x = self.widget.winfo_rootx() + 20
            y = self.widget.winfo_rooty() + self.widget.winfo_height() + 5
            self.tipwindow = tw = tk.Toplevel(self.widget)
            tw.wm_overrideredirect(1)
            tw.wm_geometry("+%d+%d" % (x, y))
            label = tk.Label(tw, text=self.text, justify='left',
                           background="#ffffe0", relief='solid', borderwidth=1,
                           font=("tahoma", "8", "normal"))
            label.pack(ipadx=1)
        except: pass

class SettingsWindow(tk.Toplevel):
    def __init__(self, parent, app_controller):
        super().__init__(parent)
        self.app = app_controller
        self.title("Configurações do Sistema")
        self.geometry("500x380") # Aumentei um pouco a altura
        
        self.cor_fundo = "#f4f6f7" 
        self.configure(bg=self.cor_fundo)
        
        style = ttk.Style(self)
        style.configure("TCheckbutton", background=self.cor_fundo)
        
        self.transient(parent)
        self.grab_set()
        
        self._construir_ui()
        
    def _construir_ui(self):
        main_frame = tk.Frame(self, bg=self.cor_fundo, padx=15, pady=15)
        main_frame.pack(fill="both", expand=True)

        # === SEÇÃO DE REDE ===
        lf_rede = tk.LabelFrame(main_frame, text="Configuração de Escuta (RX)", 
                                bg=self.cor_fundo, fg="#2c3e50", font=('Segoe UI', 10, 'bold'), padx=10, pady=10)
        lf_rede.pack(fill="x", pady=(0, 15))

        f_ip = tk.Frame(lf_rede, bg=self.cor_fundo)
        f_ip.pack(fill="x", pady=5)
        
        lbl_ip = tk.Label(f_ip, text="Multicast/Local IP:", font=("Segoe UI", 9), bg=self.cor_fundo)
        lbl_ip.pack(side="left")
        entry_ip = ttk.Entry(f_ip, textvariable=self.app.var_udp_ip, width=15)
        entry_ip.pack(side="left", padx=(5, 15))
        ToolTip(entry_ip, "IP onde o WSJT-X/JTDX manda dados.\nMulticast: 224.0.0.1\nLocal: 127.0.0.1")
        
        lbl_port = tk.Label(f_ip, text="Porta:", font=("Segoe UI", 9), bg=self.cor_fundo)
        lbl_port.pack(side="left")
        entry_port = ttk.Entry(f_ip, textvariable=self.app.var_udp_port, width=6)
        entry_port.pack(side="left", padx=5)
        ToolTip(entry_port, "Porta UDP (Padrão: 2237).")

        # === SEÇÃO DE AUTOMACAO ===
        lf_auto = tk.LabelFrame(main_frame, text="Parâmetros de Troca de Banda", 
                                bg=self.cor_fundo, fg="#2c3e50", font=('Segoe UI', 10, 'bold'), padx=10, pady=10)
        lf_auto.pack(fill="x", pady=15)

        f_grid = tk.Frame(lf_auto, bg=self.cor_fundo)
        f_grid.pack(fill="x")

        # Linha 1: Intervalo
        lbl_interv = tk.Label(f_grid, text="Intervalo de Troca:", font=("Segoe UI", 9), bg=self.cor_fundo)
        lbl_interv.grid(row=0, column=0, sticky="w", pady=5)
        
        cb_intervalo = ttk.Combobox(f_grid, textvariable=self.app.var_intervalo, values=("1 min", "2 min", "5 min", "10 min", "15 min"), width=10)
        cb_intervalo.grid(row=0, column=1, sticky="w", padx=10)
        cb_intervalo.bind("<<ComboboxSelected>>", self.app.salvar_automatico)
        ToolTip(cb_intervalo, "Tempo monitorando cada banda antes de trocar.")

        # Linha 2: Horários
        lbl_ini = tk.Label(f_grid, text="Início Dia (HH:MM):", font=("Segoe UI", 9), bg=self.cor_fundo)
        lbl_ini.grid(row=1, column=0, sticky="w", pady=5)
        entry_ini = ttk.Entry(f_grid, textvariable=self.app.var_inicio_dia, width=8)
        entry_ini.grid(row=1, column=1, sticky="w", padx=10)

        lbl_fim = tk.Label(f_grid, text="Fim Dia (HH:MM):", font=("Segoe UI", 9), bg=self.cor_fundo)
        lbl_fim.grid(row=2, column=0, sticky="w", pady=5)
        entry_fim = ttk.Entry(f_grid, textvariable=self.app.var_fim_dia, width=8)
        entry_fim.grid(row=2, column=1, sticky="w", padx=10)
        
        # --- TRAZIDO DE VOLTA: Linha 3: Delay Pós-TX ---
        lbl_delay = tk.Label(f_grid, text="Delay Pós-TX (seg):", font=("Segoe UI", 9), bg=self.cor_fundo)
        lbl_delay.grid(row=3, column=0, sticky="w", pady=5)
        entry_delay = ttk.Entry(f_grid, textvariable=self.app.var_delay_tx, width=8)
        entry_delay.grid(row=3, column=1, sticky="w", padx=10)
        ToolTip(entry_delay, "Se você transmitir (PTT), a troca de bandas\nfica pausada por este tempo (ex: 300s).")

        # Bind genérico
        self.bind_class("TEntry", "<FocusOut>", self.app.salvar_automatico)

        # Botão Fechar
        btn_fechar = tk.Button(main_frame, text="Fechar e Salvar", command=self.destroy, 
                               bg="#27ae60", fg="white", font=("Segoe UI", 10, "bold"), relief="flat", pady=5, cursor="hand2")
        btn_fechar.pack(fill="x", side="bottom")