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
        
        # --- NOME ATUALIZADO AQUI ---
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
        
        self.bandas_visiveis = False 
        self.btn_expandir = None
        self.frame_conteudo_bandas = None
        
        self.configurar_estilos()
        self.construir_layout()

    def configurar_estilos(self):
        self.root.configure(bg=self.cor_fundo)
        style = ttk.Style()
        style.theme_use('clam')
        
        style.configure("Treeview", font=('Segoe UI', 10), rowheight=28, background="#ffffff", fieldbackground="#ffffff", borderwidth=0)
        style.configure("Treeview.Heading", font=('Segoe UI', 9, 'bold'), background="#dfe6e9", foreground="#2d3436")
        style.map("Treeview", background=[('selected', '#0078d7')])
        
        style.configure("TLabelframe", background=self.cor_fundo, bordercolor="#b2bec3", borderwidth=1)
        style.configure("TLabelframe.Label", background=self.cor_fundo, foreground="#2c3e50", font=('Segoe UI', 10, 'bold'))
        style.configure("TFrame", background=self.cor_fundo)
        style.configure("TCheckbutton", background=self.cor_fundo, font=('Segoe UI', 10))

    def construir_layout(self):
        self._criar_header()
        
        self.lbl_status_geral = tk.Label(self.root, text="INICIANDO...", font=("Segoe UI", 10), bg="#ecf0f1", fg="#2c3e50", pady=6)
        self.lbl_status_geral.pack(fill="x")
        ToolTip(self.lbl_status_geral, "Status atual da automação")
        
        f_main = tk.Frame(self.root, bg=self.cor_fundo)
        f_main.pack(fill="both", expand=True, padx=15, pady=15)
        
        self._criar_tabela(f_main)
        self._criar_selecao_bandas(f_main)
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
        
        btn_cfg = tk.Button(f_btns, text="⚙ CONFIG", bg="#34495e", fg="white", 
                            command=self.app.abrir_tela_config, **btn_config)
        btn_cfg.grid(row=0, column=0, padx=2, pady=2)

        btn_about = tk.Button(f_btns, text="ℹ SOBRE", bg="#7f8c8d", fg="white", 
                              command=lambda: AboutWindow(self.root), **btn_config)
        btn_about.grid(row=0, column=1, padx=2, pady=2)

        self.btn_mudo = tk.Button(f_btns, text="🔊 SOM ON", bg="#27ae60", fg="white",
                                  command=self._toggle_mudo, **btn_config)
        self.btn_mudo.grid(row=1, column=0, padx=2, pady=2)
        
        self.btn_pause = tk.Button(f_btns, text="PAUSAR", bg="#c0392b", fg="white", 
                                   command=self.app.toggle_pause, **btn_config)
        self.btn_pause.grid(row=1, column=1, padx=2, pady=2)

        f_info = tk.Frame(f_header, bg="#2c3e50")
        f_info.pack(side="left", fill="both", expand=True)
        
        f_center_inner = tk.Frame(f_info, bg="#2c3e50")
        f_center_inner.pack(expand=True)
        
        tk.Label(f_center_inner, text="PRÓXIMA TROCA EM", font=("Segoe UI", 10, "bold"), bg="#2c3e50", fg="#bdc3c7").pack()
        
        self.lbl_timer = tk.Label(f_center_inner, text="--:--", font=("Consolas", 28, "bold"), bg="#2c3e50", fg="#f1c40f")
        self.lbl_timer.pack()
        self.lbl_banda_grande = tk.Label(f_center_inner, text="---", font=("Segoe UI", 12, "bold"), bg="#2c3e50", fg="white")
        self.lbl_banda_grande.pack()

    def _toggle_mudo(self):
        estado_atual = self.app.var_mudo.get()
        novo_estado = not estado_atual
        self.app.var_mudo.set(novo_estado)
        self.app.salvar_automatico()
        if novo_estado:
            self.btn_mudo.config(text="🔇 MUDO", bg="#e74c3c")
        else:
            self.btn_mudo.config(text="🔊 SOM ON", bg="#27ae60")

    def _criar_tabela(self, parent):
        f_lista = tk.LabelFrame(parent, text="Monitoramento de Alertas", 
                                bg=self.cor_fundo, fg="#2c3e50", font=('Segoe UI', 10, 'bold'), padx=10, pady=10)
        f_lista.pack(fill="both", expand=True, pady=(0, 10))
        
        colunas = ("Hora", "Banda", "Modo", "Mensagem")
        self.tree_alertas = ttk.Treeview(f_lista, columns=colunas, show="headings", height=8)
        self.tree_alertas.heading("Hora", text="Horário (UTC)")
        self.tree_alertas.column("Hora", width=80, anchor="center")
        self.tree_alertas.heading("Banda", text="Banda")
        self.tree_alertas.column("Banda", width=80, anchor="center")
        self.tree_alertas.heading("Modo", text="Modo")
        self.tree_alertas.column("Modo", width=60, anchor="center")
        self.tree_alertas.heading("Mensagem", text="Mensagem Original")
        self.tree_alertas.column("Mensagem", width=330, anchor="w")
        
        self.tree_alertas.tag_configure('ciclo_claro', background='white')
        self.tree_alertas.tag_configure('ciclo_escuro', background='#eaf2f8')
        
        scrolly = ttk.Scrollbar(f_lista, orient="vertical", command=self.tree_alertas.yview)
        self.tree_alertas.configure(yscroll=scrolly.set)
        self.tree_alertas.pack(side="left", fill="both", expand=True)
        scrolly.pack(side="right", fill="y")

    def _criar_selecao_bandas(self, parent):
        self.f_bandas_container = tk.Frame(parent, bg=self.cor_fundo)
        self.f_bandas_container.pack(fill="both", expand=True, pady=5)
        
        f_toggle = tk.Frame(self.f_bandas_container, bg="#bdc3c7", relief="raised", borderwidth=1)
        f_toggle.pack(fill="x")
        
        self.btn_expandir = tk.Button(f_toggle, text="▶  Configuração de Bandas e Watchlist (Clique para Expandir)", 
                                      command=self._toggle_painel_bandas,
                                      bg="#ecf0f1", fg="#2c3e50", relief="flat", anchor="w", padx=10,
                                      font=("Segoe UI", 9, "bold"), cursor="hand2")
        self.btn_expandir.pack(fill="x")
        
        self.frame_externo = tk.Frame(self.f_bandas_container, bg=self.cor_fundo, relief="solid", borderwidth=1)
        
        self.canvas = tk.Canvas(self.frame_externo, bg=self.cor_fundo, highlightthickness=0, height=250)
        self.scrollbar = ttk.Scrollbar(self.frame_externo, orient="vertical", command=self.canvas.yview)
        self.frame_conteudo_bandas = tk.Frame(self.canvas, bg=self.cor_fundo)

        self.frame_conteudo_bandas.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.window_id = self.canvas.create_window((0, 0), window=self.frame_conteudo_bandas, anchor="nw")
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfig(self.window_id, width=e.width))
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        self._popular_conteudo_bandas(self.frame_conteudo_bandas)

    def _popular_conteudo_bandas(self, container):
        tk.Label(container, text="Banda", font=("Segoe UI", 9, "bold"), bg=self.cor_fundo).grid(row=0, column=0, padx=5, pady=5)
        tk.Label(container, text="☀ Dia", font=("Segoe UI", 9, "bold"), fg="#e67e22", bg=self.cor_fundo).grid(row=0, column=1, padx=5)
        tk.Label(container, text="🌙 Noite", font=("Segoe UI", 9, "bold"), fg="#8e44ad", bg=self.cor_fundo).grid(row=0, column=2, padx=5)
        tk.Label(container, text="Indicativos de Interesse", font=("Segoe UI", 9, "bold"), bg=self.cor_fundo).grid(row=0, column=3, sticky="w", padx=5)
        
        container.columnconfigure(3, weight=1)
        
        for i, banda in enumerate(sorted(FREQUENCIAS.keys(), key=lambda x: -FREQUENCIAS[x])):
            row = i + 1
            
            lbl_b = tk.Label(container, text=banda, font=("Segoe UI", 10, "bold"), 
                             bg="#ecf0f1", fg="#2c3e50", width=6, cursor="hand2")
            lbl_b.grid(row=row, column=0, pady=2, padx=2)
            lbl_b.bind("<Double-1>", lambda event, b=banda: self.app.forcar_mudanca_banda(b))
            ToolTip(lbl_b, f"Clique Duplo para mudar para {banda}")
            
            vd = tk.BooleanVar(value=(banda in self.app.dados_config.get("bandas_dia", [])))
            self.app.vars_dia[banda] = vd
            ttk.Checkbutton(container, variable=vd, command=self.app.salvar_automatico).grid(row=row, column=1)
            
            vn = tk.BooleanVar(value=(banda in self.app.dados_config.get("bandas_noite", [])))
            self.app.vars_noite[banda] = vn
            ttk.Checkbutton(container, variable=vn, command=self.app.salvar_automatico).grid(row=row, column=2)
            
            texto_salvo = self.app.dados_config.get("watchlists", {}).get(banda, "")
            vw = tk.StringVar(value=texto_salvo)
            vw.trace_add("write", lambda *args, v=vw: self._forcar_maiusculo(v))
            self.app.vars_watchlist[banda] = vw
            e = ttk.Entry(container, textvariable=vw, font=("Consolas", 10))
            e.grid(row=row, column=3, padx=5, sticky="ew")
            e.bind("<FocusOut>", lambda event, v=vw: self._validar_watchlist_ao_sair(event, v))
            e.bind("<KeyRelease>", lambda event, b=banda: self.app.atualizar_watch_realtime(b))
            
            for widget in [lbl_b, e]:
                widget.bind("<MouseWheel>", self._on_mousewheel)
        
        container.bind("<MouseWheel>", self._on_mousewheel)

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def _toggle_painel_bandas(self):
        self.bandas_visiveis = not self.bandas_visiveis
        
        if self.bandas_visiveis:
            self.btn_expandir.config(text="▼  Configuração de Bandas e Watchlist (Clique para Recolher)")
            self.frame_externo.pack(fill="both", expand=True)
            atual_h = self.root.winfo_height()
            self.root.geometry(f"780x{atual_h + 250}")
        else:
            self.btn_expandir.config(text="▶  Configuração de Bandas e Watchlist (Clique para Expandir)")
            self.frame_externo.pack_forget()
            self.root.geometry("") 
            self.root.update_idletasks()

    def _forcar_maiusculo(self, var_tk):
        atual = var_tk.get()
        if atual != atual.upper():
            var_tk.set(atual.upper())

    def _validar_watchlist_ao_sair(self, event, var_tk):
        texto = var_tk.get()
        if not texto:
            self.app.salvar_automatico(event)
            return
        texto = texto.replace(";", ",").replace(" ", ",")
        itens = [x.strip() for x in texto.split(",") if x.strip()]
        itens_unicos_ordenados = sorted(list(set(itens)))
        novo_texto = ", ".join(itens_unicos_ordenados)
        if novo_texto != var_tk.get():
            var_tk.set(novo_texto)
        self.app.salvar_automatico(event)

    def _criar_footer(self):
        f_footer = tk.Frame(self.root, bg=self.cor_fundo, pady=10)
        f_footer.pack(fill="x", side="bottom")
        tk.Label(f_footer, text="Dica: Use o botão '⚙ CONFIG' acima para ajustar Redes e Horários.", 
                 bg=self.cor_fundo, fg="#7f8c8d", font=("Segoe UI", 8)).pack(side="left", padx=10)