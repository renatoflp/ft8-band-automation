import tkinter as tk
from tkinter import ttk
import webbrowser
from config import FREQUENCIAS

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

class AboutWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Sobre")
        self.geometry("450x480")
        self.resizable(False, False)
        self.configure(bg="#ecf0f1")
        self.transient(parent)
        self.grab_set()
        self._construir_ui()

    def _construir_ui(self):
        tk.Label(self, text="Automação de Bandas", font=("Segoe UI", 16, "bold"), 
                 bg="#ecf0f1", fg="#2c3e50").pack(pady=(20, 5))
        tk.Label(self, text="Para WSJT-X / JTDX & FLRIG", font=("Segoe UI", 10), 
                 bg="#ecf0f1", fg="#7f8c8d").pack()
        ttk.Separator(self, orient="horizontal").pack(fill="x", padx=40, pady=15)

        f_autor = tk.Frame(self, bg="#ecf0f1")
        f_autor.pack(pady=5)
        tk.Label(f_autor, text="Desenvolvido por:", font=("Segoe UI", 10), bg="#ecf0f1").pack()
        tk.Label(f_autor, text="MUNIZ, Renato de Souza - PP5EO", font=("Segoe UI", 12, "bold"), bg="#ecf0f1", fg="#2980b9").pack()

        lbl_link = tk.Label(self, text="github.com/renatoflp/ft8-band-automation", 
                            font=("Segoe UI", 10, "underline"), bg="#ecf0f1", fg="blue", cursor="hand2")
        lbl_link.pack(pady=10)
        lbl_link.bind("<Button-1>", lambda e: self._abrir_link("https://github.com/renatoflp/ft8-band-automation"))
        ToolTip(lbl_link, "Clique para ver o código fonte e atualizações")

        f_lic = tk.LabelFrame(self, text="Licença & Aviso Legal", bg="#ecf0f1", padx=10, pady=10)
        f_lic.pack(fill="both", expand=True, padx=20, pady=10)
        txt_lic = ("Este software é Open Source (Licença MIT).\n\n"
                   "Você é livre para usar, copiar e modificar.\n"
                   "O software é fornecido 'COMO ESTÁ', sem garantias.\n"
                   "O autor não se responsabiliza por danos ao equipamento\n"
                   "decorrentes do uso de automação.")
        lbl_lic = tk.Label(f_lic, text=txt_lic, font=("Segoe UI", 9), bg="#ecf0f1", justify="center")
        lbl_lic.pack()

        tk.Button(self, text="Fechar", command=self.destroy, bg="#95a5a6", fg="white", 
                  font=("Segoe UI", 9, "bold"), relief="flat", padx=20).pack(pady=15)

    def _abrir_link(self, url):
        webbrowser.open_new(url)

class GuiBuilder:
    def __init__(self, root, app_controller):
        self.root = root
        self.app = app_controller 
        self.cor_fundo = "#f4f6f7"
        self.modo_compacto = False
        
        self.configurar_estilos()
        self.construir_layout()

    def configurar_estilos(self):
        self.root.configure(bg=self.cor_fundo)
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TLabelframe", background=self.cor_fundo, bordercolor="#b2bec3", borderwidth=1)
        style.configure("TLabelframe.Label", background=self.cor_fundo, foreground="#2c3e50", font=('Segoe UI', 10, 'bold'))
        style.configure("TFrame", background=self.cor_fundo)
        style.configure("TCheckbutton", background=self.cor_fundo, font=('Segoe UI', 10))

    def construir_layout(self):
        self._criar_header()
        
        self.lbl_status_geral = tk.Label(self.root, text="INICIANDO...", font=("Segoe UI", 10), bg="#ecf0f1", fg="#2c3e50", pady=6)
        self.lbl_status_geral.pack(fill="x")
        ToolTip(self.lbl_status_geral, "Status atual da automação")
        
        self.f_main = tk.Frame(self.root, bg=self.cor_fundo)
        self.f_main.pack(fill="both", expand=True, padx=15, pady=15)
        
        self._criar_selecao_bandas(self.f_main)
        self._criar_footer()
        
        self.root.update_idletasks()
        self.root.geometry("") 

    def _criar_header(self):
        f_header = tk.Frame(self.root, bg="#2c3e50", pady=15, padx=15)
        f_header.pack(fill="x")
        
        f_conn = tk.Frame(f_header, bg="#2c3e50")
        f_conn.pack(side="left")
        
        self.lbl_flrig = tk.Label(f_conn, text="FLRIG", font=("Segoe UI", 8, "bold"), bg="#7f8c8d", fg="white", width=10)
        self.lbl_flrig.pack(pady=1)
        self.lbl_jtdx = tk.Label(f_conn, text="WSJT/JTDX", font=("Segoe UI", 8, "bold"), bg="#7f8c8d", fg="white", width=10)
        self.lbl_jtdx.pack(pady=1)
        
        f_btns = tk.Frame(f_header, bg="#2c3e50")
        f_btns.pack(side="right")

        btn_config = {'width': 12, 'height': 1, 'relief': "flat", 'cursor': "hand2", 'font': ("Segoe UI", 9, "bold")}
        
        self.btn_cfg = tk.Button(f_btns, text="⚙ CONFIG", bg="#34495e", fg="white", 
                            command=self.app.abrir_tela_config, **btn_config)
        self.btn_cfg.grid(row=0, column=0, padx=2, pady=2)

        self.btn_about = tk.Button(f_btns, text="ℹ SOBRE", bg="#7f8c8d", fg="white", 
                              command=lambda: AboutWindow(self.root), **btn_config)
        self.btn_about.grid(row=0, column=1, padx=2, pady=2)

        self.btn_next = tk.Button(f_btns, text="⏭ PRÓXIMA", bg="#3498db", fg="white",
                          command=self.app.pular_para_proxima_banda, **btn_config)
        self.btn_next.grid(row=1, column=0, padx=2, pady=2)

        self.btn_pause = tk.Button(f_btns, text="PAUSAR", bg="#c0392b", fg="white", 
                                   command=self.app.toggle_pause, **btn_config)
        self.btn_pause.grid(row=1, column=1, padx=2, pady=2)

        self.btn_mini = tk.Button(f_btns, text="📌", bg="#f39c12", fg="white", 
                                  command=self.toggle_modo_compacto, relief="flat", font=("Segoe UI", 9, "bold"), width=3)
        self.btn_mini.grid(row=0, column=2, rowspan=2, padx=2, pady=2, sticky="ns")
        ToolTip(self.btn_mini, "Modo Compacto (Sempre no Topo)")

        f_info = tk.Frame(f_header, bg="#2c3e50")
        f_info.pack(side="left", fill="both", expand=True)
        
        f_center_inner = tk.Frame(f_info, bg="#2c3e50")
        f_center_inner.pack(expand=True)
        
        tk.Label(f_center_inner, text="PRÓXIMA TROCA EM", font=("Segoe UI", 10, "bold"), bg="#2c3e50", fg="#bdc3c7").pack()
        
        self.lbl_timer = tk.Label(f_center_inner, text="--:--", font=("Consolas", 28, "bold"), bg="#2c3e50", fg="#f1c40f")
        self.lbl_timer.pack()
        self.lbl_banda_grande = tk.Label(f_center_inner, text="---", font=("Segoe UI", 12, "bold"), bg="#2c3e50", fg="white")
        self.lbl_banda_grande.pack()

    def _criar_selecao_bandas(self, parent):
        self.f_bandas_container = tk.Frame(parent, bg=self.cor_fundo)
        self.f_bandas_container.pack(fill="both", expand=True, pady=5)
        
        self.frame_externo = tk.Frame(self.f_bandas_container, bg=self.cor_fundo, relief="solid", borderwidth=1)
        self.frame_externo.pack(fill="x", expand=False) 
        
        self.frame_conteudo_bandas = tk.Frame(self.frame_externo, bg=self.cor_fundo)
        self.frame_conteudo_bandas.pack(pady=15, padx=10, anchor="center")
        
        self._popular_conteudo_bandas(self.frame_conteudo_bandas)

    def _popular_conteudo_bandas(self, container):
        tk.Label(container, text="Banda", font=("Segoe UI", 9, "bold"), bg=self.cor_fundo).grid(row=0, column=0, padx=10, pady=5, sticky="e")
        tk.Label(container, text="☀ Dia", font=("Segoe UI", 9, "bold"), fg="#e67e22", bg=self.cor_fundo).grid(row=1, column=0, padx=10, pady=2, sticky="e")
        tk.Label(container, text="🌙 Noite", font=("Segoe UI", 9, "bold"), fg="#8e44ad", bg=self.cor_fundo).grid(row=2, column=0, padx=10, pady=2, sticky="e")
        
        for i, banda in enumerate(sorted(FREQUENCIAS.keys(), key=lambda x: -FREQUENCIAS[x])):
            col = i + 1
            
            lbl_b = tk.Label(container, text=banda, font=("Segoe UI", 10, "bold"), 
                             bg="#ecf0f1", fg="#2c3e50", width=6, cursor="hand2")
            lbl_b.grid(row=0, column=col, pady=5, padx=2)
            lbl_b.bind("<Double-1>", lambda event, b=banda: self.app.forcar_mudanca_banda(b))
            ToolTip(lbl_b, f"Clique Duplo para mudar para {banda}")
            
            vd = tk.BooleanVar(value=(banda in self.app.dados_config.get("bandas_dia", [])))
            self.app.vars_dia[banda] = vd
            ttk.Checkbutton(container, variable=vd, command=self.app.salvar_automatico).grid(row=1, column=col, padx=2)
            
            vn = tk.BooleanVar(value=(banda in self.app.dados_config.get("bandas_noite", [])))
            self.app.vars_noite[banda] = vn
            ttk.Checkbutton(container, variable=vn, command=self.app.salvar_automatico).grid(row=2, column=col, padx=2)

    def _criar_footer(self):
        self.f_footer = tk.Frame(self.root, bg=self.cor_fundo, pady=10)
        self.f_footer.pack(fill="x", side="bottom")
        tk.Label(self.f_footer, text="Dica: Use o botão '⚙ CONFIG' acima para ajustar Redes e Horários.", 
                 bg=self.cor_fundo, fg="#7f8c8d", font=("Segoe UI", 8)).pack(side="left", padx=10)

    def toggle_modo_compacto(self):
        self.modo_compacto = not self.modo_compacto
        
        if self.modo_compacto:
            self.root.attributes('-topmost', True) 
            self.f_main.pack_forget() 
            self.f_footer.pack_forget() 
            
            self.lbl_timer.config(font=("Consolas", 16, "bold"))
            self.lbl_banda_grande.config(font=("Segoe UI", 9, "bold"))
            self.lbl_status_geral.config(font=("Segoe UI", 8), pady=2)
            
            self.btn_cfg.config(text="⚙", width=3)
            self.btn_about.config(text="ℹ", width=3)
            self.btn_next.config(text="⏭", width=3)
            self.btn_pause.config(text="▶" if not self.app.automacao_ativa else "⏸", width=3)
            
            self.lbl_flrig.config(width=5, text="FLRIG")
            self.lbl_jtdx.config(width=5, text="WSJT")
            
            self.btn_mini.config(text="🗖") 
            self.root.geometry("") 
            
        else:
            self.root.attributes('-topmost', False)
            
            self.f_main.pack(fill="both", expand=True, padx=15, pady=15)
            self.f_footer.pack(fill="x", side="bottom")
            
            self.lbl_timer.config(font=("Consolas", 28, "bold"))
            self.lbl_banda_grande.config(font=("Segoe UI", 12, "bold"))
            self.lbl_status_geral.config(font=("Segoe UI", 10), pady=6)
            
            self.btn_cfg.config(text="⚙ CONFIG", width=12)
            self.btn_about.config(text="ℹ SOBRE", width=12)
            self.btn_next.config(text="⏭ PRÓXIMA", width=12)
            self.btn_pause.config(text="RETOMAR" if not self.app.automacao_ativa else "PAUSAR", width=12)
            
            self.lbl_flrig.config(width=10)
            self.lbl_jtdx.config(width=10)
            
            self.btn_mini.config(text="📌")
            self.root.geometry("")
