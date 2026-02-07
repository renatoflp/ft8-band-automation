# -----------------------------------------------------------------------------
# Projeto: Automação de Bandas JTDX/WSJT-X
# Autor: MUNIZ, Renato de Souza - PP5EO
# Licença: MIT License
# Repositório Oficial: https://github.com/renatoflp/ft8-band-automation
#
# Copyright (c) 2026 MUNIZ, Renato de Souza - PP5EO
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# -----------------------------------------------------------------------------

import tkinter as tk
import datetime
import time
import winsound

from config import FREQUENCIAS, JTDX_UDP_PORT
from monitor import JTDXMonitor
from comms import FLRIGClient
from persistence import ConfigManager
from interface import GuiBuilder
from settings_ui import SettingsWindow

class AppJTDX:
    def __init__(self, root):
        self.root = root
        self.root.title("PP5EO | Monitor & Auto Band Switch")
        self.root.geometry("780x700")
        self.root.protocol("WM_DELETE_WINDOW", self.fechar_app)
        
        self.dados_config = ConfigManager.carregar()
        
        self.vars_dia = {}
        self.vars_noite = {}
        self.vars_watchlist = {}
        
        self.var_intervalo = tk.StringVar(value=self.dados_config.get("intervalo", "10 min"))
        self.var_inicio_dia = tk.StringVar(value=self.dados_config.get("inicio_dia", "07:00"))
        self.var_fim_dia = tk.StringVar(value=self.dados_config.get("fim_dia", "18:30"))
        self.var_mudo = tk.BooleanVar(value=self.dados_config.get("audio_mudo", False))
        self.var_delay_tx = tk.StringVar(value=str(self.dados_config.get("delay_pos_tx", "300")))
        
        self.var_udp_ip = tk.StringVar(value=self.dados_config.get("jtdx_udp_ip", "224.0.0.1"))
        self.var_udp_port = tk.StringVar(value=str(self.dados_config.get("jtdx_udp_port", 2237)))
        
        self.last_network_config = {
            "ip": self.var_udp_ip.get(),
            "port": self.var_udp_port.get()
        }

        self.automacao_ativa = True
        self.last_band_change = time.time() - 9999 
        self.last_tx_time = 0
        self.current_band_index = -1
        self.banda_atual_nome = "---"
        self.ultimo_ciclo_sync = 0 
        self.ultimo_alerta_time = 0
        self.tag_cor_atual = 'ciclo_claro'
        
        self.flrig = FLRIGClient()
        
        print(f"[SISTEMA] Iniciando Monitor em {self.var_udp_ip.get()}:{self.var_udp_port.get()}...")
        self.monitor = JTDXMonitor(self.receber_alerta_dx, self.var_udp_ip.get(), int(self.var_udp_port.get()))
        self.monitor.start()

        self.gui = GuiBuilder(root, self)
        
        self.root.after(2000, self.sincronizar_radio_inicio)
        self.root.after(3000, self.loop_automacao)

    def abrir_tela_config(self):
        SettingsWindow(self.root, self)

    def forcar_mudanca_banda(self, nome_banda):
        print(f"Comando Manual: Mudando para {nome_banda}")
        freq = FREQUENCIAS.get(nome_banda)
        if freq:
            if self.flrig.set_frequency(freq):
                self.banda_atual_nome = nome_banda
                self.last_band_change = time.time() 
                self.gui.lbl_status_geral.config(text="MONITORANDO (RX)", bg="#bdc3c7", fg="#2c3e50")
                lista_ativa, _ = self.get_lista_bandas_ativa()
                if nome_banda in lista_ativa:
                    self.current_band_index = lista_ativa.index(nome_banda)
                self.gui.lbl_banda_grande.config(text=nome_banda)
                self.atualizar_watch_realtime(nome_banda)

    def sincronizar_radio_inicio(self):
        freq_atual = self.monitor.current_freq
        if freq_atual <= 0: freq_atual = self.flrig.get_frequency()
        if freq_atual <= 0: return
        banda_detectada = None
        for nome_banda, freq_ft8 in FREQUENCIAS.items():
            if abs(freq_atual - freq_ft8) < 5000:
                banda_detectada = nome_banda
                break
        if banda_detectada:
            lista_ativa, _ = self.get_lista_bandas_ativa()
            if banda_detectada in lista_ativa:
                try:
                    self.current_band_index = lista_ativa.index(banda_detectada)
                    self.banda_atual_nome = banda_detectada
                    self.last_band_change = time.time()
                    self.gui.lbl_banda_grande.config(text=banda_detectada)
                    self.atualizar_watch_realtime(banda_detectada)
                    print(f"Sincronia Inicial: {banda_detectada}")
                except: pass

    def receber_alerta_dx(self, remetente, modo, mensagem, horario, dados_tecnicos):
        self.root.after(0, lambda: self._processar_alerta_gui(remetente, modo, mensagem, horario))

    def _processar_alerta_gui(self, remetente, modo, mensagem, horario):
        if not self.var_mudo.get():
            try: winsound.Beep(2000, 100)
            except: pass
        tv = self.gui.tree_alertas
        agora = time.time()
        if (agora - self.ultimo_alerta_time) > 2.5:
            if self.tag_cor_atual == 'ciclo_claro': self.tag_cor_atual = 'ciclo_escuro'
            else: self.tag_cor_atual = 'ciclo_claro'
        self.ultimo_alerta_time = agora
        tv.insert("", 0, values=(horario, self.banda_atual_nome, modo, mensagem), tags=(self.tag_cor_atual,))
        filhos = tv.get_children()
        if len(filhos) > 100: tv.delete(filhos[-1])

    def loop_automacao(self):
        agora = time.time()
        ptt = self.flrig.get_ptt()
        flrig_ok = (ptt is not None)
        
        if flrig_ok:
            self.gui.lbl_flrig.config(bg="#27ae60", text="✔ FLRIG ON")
        else:
            self.gui.lbl_flrig.config(bg="#c0392b", text="✖ FLRIG OFF")

        if (agora - self.monitor.last_packet_time) < 15:
            self.gui.lbl_jtdx.config(bg="#27ae60", text="✔ WSJT DATA")
        else:
            self.gui.lbl_jtdx.config(bg="#f39c12", text="⚠ WSJT WAIT")

        if flrig_ok and ptt == 1:
            self.gui.lbl_status_geral.config(text="TRANSMITINDO (TX)", bg="#c0392b", fg="white")
            self.last_tx_time = agora
            self.last_band_change = agora 
        else:
            delay_configurado = self.get_delay_segundos()
            tempo_desde_tx = agora - self.last_tx_time
            
            if tempo_desde_tx < delay_configurado:
                segundos_restantes = int(delay_configurado - tempo_desde_tx)
                self.gui.lbl_status_geral.config(text=f"DELAY PÓS-TX ({segundos_restantes}s)", bg="#2980b9", fg="white")
                self.gui.lbl_timer.config(text="DELAY", fg="#f39c12")
                self.last_band_change = agora 
            else:
                self.gui.lbl_status_geral.config(text="MONITORANDO (RX)", bg="#bdc3c7", fg="#2c3e50")
                
                if self.automacao_ativa and flrig_ok:
                    self.verificar_mudanca_manual()
                    tempo_passado = agora - self.last_band_change
                    intervalo = self.get_segundos()
                    restante = int(intervalo - tempo_passado)

                    if restante > 0:
                        self.gui.lbl_timer.config(text=f"{restante//60:02d}:{restante%60:02d}", fg="#f1c40f")
                        if ptt != 1:
                            self.gui.lbl_banda_grande.config(text=f"{self.banda_atual_nome}")
                    else:
                        self.gui.lbl_timer.config(text="SYNC...", fg="#f1c40f")
                        segundo_atual = datetime.datetime.now().second
                        if segundo_atual % 15 == 0:
                            if abs(agora - self.ultimo_ciclo_sync) > 5: 
                                self.trocar_banda()
                                self.ultimo_ciclo_sync = agora
                else:
                    self.gui.lbl_timer.config(text="PAUSADO", fg="#7f8c8d")

        self.root.after(1000, self.loop_automacao)

    def verificar_mudanca_manual(self):
        freq_real = self.monitor.current_freq
        if freq_real <= 0: return
        banda_real = None
        for nome_banda, freq_ft8 in FREQUENCIAS.items():
            if abs(freq_real - freq_ft8) < 5000:
                banda_real = nome_banda
                break
        if banda_real and banda_real != self.banda_atual_nome:
            print(f"Detectada mudança manual para {banda_real}")
            self.banda_atual_nome = banda_real
            self.last_band_change = time.time()
            lista_ativa, _ = self.get_lista_bandas_ativa()
            if banda_real in lista_ativa:
                self.current_band_index = lista_ativa.index(banda_real)
            self.atualizar_watch_realtime(banda_real)
            self.gui.lbl_banda_grande.config(text=banda_real)

    def get_lista_bandas_ativa(self):
        agora = datetime.datetime.now()
        min_atual = agora.hour * 60 + agora.minute
        try:
            min_inicio = int(self.var_inicio_dia.get().split(':')[0])*60 + int(self.var_inicio_dia.get().split(':')[1])
            min_fim = int(self.var_fim_dia.get().split(':')[0])*60 + int(self.var_fim_dia.get().split(':')[1])
        except:
            min_inicio, min_fim = 420, 1110 
        eh_dia = (min_inicio <= min_atual < min_fim)
        lista_ativa = []
        fonte = self.vars_dia if eh_dia else self.vars_noite
        for banda, var in fonte.items():
            if var.get(): lista_ativa.append(banda)
        return lista_ativa, eh_dia

    def trocar_banda(self):
        lista_ativa, _ = self.get_lista_bandas_ativa()
        if lista_ativa:
            self.last_band_change = time.time()
            self.current_band_index = (self.current_band_index + 1) % len(lista_ativa)
            nova_banda = lista_ativa[self.current_band_index]
            freq = FREQUENCIAS[nova_banda]
            print(f"Automacao: Trocando para {nova_banda} ({freq})")
            
            if self.flrig.set_frequency(freq):
                self.banda_atual_nome = nova_banda
                txt_watch = self.vars_watchlist[nova_banda].get().upper()
                self.monitor.update_watchlist(txt_watch)

    def salvar_automatico(self, event=None):
        dados = ConfigManager.carregar()
        
        ip_novo = self.var_udp_ip.get()
        port_nova = int(self.var_udp_port.get() or 2237)
        
        dados.update({
            "jtdx_udp_ip": ip_novo,
            "jtdx_udp_port": port_nova,
            "intervalo": self.var_intervalo.get(),
            "inicio_dia": self.var_inicio_dia.get(),
            "fim_dia": self.var_fim_dia.get(),
            "delay_pos_tx": self.var_delay_tx.get(),
            "audio_mudo": self.var_mudo.get(),
            "bandas_dia": [b for b, v in self.vars_dia.items() if v.get()],
            "bandas_noite": [b for b, v in self.vars_noite.items() if v.get()],
            "watchlists": {b: v.get().upper() for b, v in self.vars_watchlist.items()}
        })
        ConfigManager.salvar(dados)
        
        if ip_novo != self.last_network_config["ip"] or str(port_nova) != str(self.last_network_config["port"]):
            print("[REDE] Configuração alterada. Reiniciando monitor...")
            try:
                self.monitor.stop()
                self.monitor.join(timeout=1.0)
            except: pass
            self.monitor = JTDXMonitor(self.receber_alerta_dx, ip_novo, port_nova)
            self.monitor.start()
            self.last_network_config["ip"] = ip_novo
            self.last_network_config["port"] = port_nova

        if self.banda_atual_nome in self.vars_watchlist:
            self.monitor.update_watchlist(self.vars_watchlist[self.banda_atual_nome].get())

    def atualizar_watch_realtime(self, banda):
        if self.banda_atual_nome == banda:
            self.monitor.update_watchlist(self.vars_watchlist[banda].get().upper())

    def toggle_pause(self):
        self.automacao_ativa = not self.automacao_ativa
        txt = "RETOMAR" if not self.automacao_ativa else "PAUSAR"
        self.gui.btn_pause.config(text=txt)

    def get_segundos(self):
        try: return int(self.var_intervalo.get().split()[0]) * 60
        except: return 600

    def get_delay_segundos(self):
        try: return int(self.var_delay_tx.get())
        except: return 300

    def fechar_app(self):
        if self.monitor: self.monitor.stop()
        self.salvar_automatico()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = AppJTDX(root)
    root.mainloop()