import socket
import threading
import time
import re
import struct
import datetime
from config import JTDX_UDP_IP, JTDX_UDP_PORT, MY_CALLSIGN 

class JTDXMonitor(threading.Thread):
    def __init__(self, callback_alerta, ip_multicast, porta):
        super().__init__()
        self.callback_alerta = callback_alerta
        self.stop_event = threading.Event()
        self.watchlist_patterns = [] 
        
        # --- CORREÇÃO AQUI ---
        self.last_packet_time = 0 # Inicializa a variável para evitar o erro no main.py
        
        self.ip_multicast = ip_multicast
        self.porta = porta
        
        self.sock = None
        self.running = False
        self.current_freq = 0 
        
        self.cache_alertas = {} 
        
        self._iniciar_socket()

    def _get_local_ips(self):
        ips = set()
        ips.add("127.0.0.1")
        try:
            hostname = socket.gethostname()
            infos = socket.getaddrinfo(hostname, None, socket.AF_INET)
            for info in infos:
                ip = info[4][0]
                ips.add(ip)
        except: pass
        return list(ips)

    def _iniciar_socket(self):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.sock.bind(('0.0.0.0', self.porta))
            
            ips_locais = self._get_local_ips()
            print(f"[MONITOR] Entrando no grupo {self.ip_multicast}:{self.porta}")
            
            group = socket.inet_aton(self.ip_multicast)
            for ip in ips_locais:
                try:
                    local = socket.inet_aton(ip)
                    mreq = struct.pack('4s4s', group, local)
                    self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
                except: pass
            
            self.running = True
        except Exception as e:
            print(f"[MONITOR] Erro fatal: {e}")
            self.running = False

    def stop(self):
        self.stop_event.set()
        self.running = False
        if self.sock:
            try: self.sock.close() 
            except: pass

    def update_watchlist(self, raw_string):
        if not raw_string:
            self.watchlist_patterns = []
            return
        
        lista_texto = raw_string.replace(";", ",").split(',')
        novos_padroes = []
        for item in lista_texto:
            item = item.strip().upper()
            if not item: continue
            try:
                regex_safe = re.escape(item)
                regex_final = "^" + regex_safe.replace(r"\*", ".*") + "$" 
                padrao = re.compile(regex_final)
                novos_padroes.append(padrao)
            except: pass
        self.watchlist_patterns = novos_padroes

    def run(self):
        if not self.sock: return
        while not self.stop_event.is_set() and self.running:
            try:
                self.sock.settimeout(1.0)
                data, addr = self.sock.recvfrom(65535)
                self.last_packet_time = time.time() # Atualiza o tempo do último pacote recebido
                self.parse_packet(data)
            except socket.timeout: continue
            except OSError: break 
            except Exception as e: 
                time.sleep(1)
        
        if self.sock:
            try: self.sock.close()
            except: pass

    def parse_packet(self, data):
        if len(data) < 12: return
        try:
            msg_type = struct.unpack('>I', data[8:12])[0]
        except: return

        if msg_type == 1:
            self.handle_status_packet(data)
        elif msg_type == 2:
            self.handle_decode_packet(data)

    def handle_status_packet(self, data):
        try:
            offset = 12 
            id_len = struct.unpack('>I', data[offset:offset+4])[0]
            offset += 4 + id_len 
            freq = struct.unpack('>Q', data[offset:offset+8])[0]
            if freq > 0: self.current_freq = freq
        except: pass

    def handle_decode_packet(self, data):
        try:
            offset = 12
            len_id = struct.unpack('>I', data[offset:offset+4])[0]
            offset += 4 + len_id + 1 
            
            ms_midnight = struct.unpack('>I', data[offset:offset+4])[0]
            offset += 4
            snr = struct.unpack('>i', data[offset:offset+4])[0]
            offset += 4
            delta_time = struct.unpack('>d', data[offset:offset+8])[0]
            offset += 8
            delta_freq = struct.unpack('>I', data[offset:offset+4])[0]
            offset += 4
            
            len_mode = struct.unpack('>I', data[offset:offset+4])[0]
            offset += 4 + len_mode
            
            len_msg = struct.unpack('>I', data[offset:offset+4])[0]
            msg_bytes = data[offset+4 : offset+4+len_msg]
            raw_text = msg_bytes.decode('utf-8', errors='ignore')
            
            dados_tecnicos = {
                "ms_midnight": ms_midnight,
                "snr": snr,
                "dt": delta_time,
                "df": delta_freq,
                "msg_original": raw_text
            }
            
            if len(raw_text) > 4:
                self.analisar_texto(raw_text, dados_tecnicos)
                
        except Exception as e:
            pass

    def analisar_texto(self, raw_text, dados_tecnicos):
        msg_limpa = self.extrair_msg_bonita(raw_text).upper()
        partes = msg_limpa.split()
        if len(partes) < 2: return

        remetente = ""
        if partes[0] == "CQ":
            modificadores = ["DX", "TEST", "POTA", "SOTA", "QRP", "LP", "AG", "UP", "NA", "SA", "EU", "AS", "OC", "AF"]
            if len(partes) > 2 and (partes[1] in modificadores or partes[1].isdigit()):
                remetente = partes[2]
            else:
                remetente = partes[1]
        else:
            remetente = partes[1]

        if remetente == MY_CALLSIGN: return
        if len(remetente) < 3: return 

        if not self.watchlist_patterns: return

        encontrado = False
        for pattern in self.watchlist_patterns:
            if pattern.match(remetente):
                encontrado = True
                break
        
        if encontrado:
            agora = time.time()
            ultimo = self.cache_alertas.get(remetente, 0)
            
            if (agora - ultimo) > 15: 
                self.cache_alertas[remetente] = agora
                
                seconds = (dados_tecnicos["ms_midnight"] // 1000) % 86400
                m, s = divmod(seconds, 60)
                h, m = divmod(m, 60)
                horario_legivel = f"{h:02d}:{m:02d}:{s:02d}"
                
                modo = "FT8"
                if "FT4" in raw_text: modo = "FT4"
                
                self.callback_alerta(remetente, modo, msg_limpa, horario_legivel, dados_tecnicos)
                print(f"ALERTA: {remetente} (DF:{dados_tecnicos['df']}Hz)")

    def extrair_msg_bonita(self, raw_text):
        text = raw_text.replace("\x00", " ").strip()
        if "~" in text: text = text.split("~")[-1]
        elif "%" in text: text = text.split("%")[-1]
        text = re.sub(r' [+-]\d+ ', ' ', text)
        text = re.sub(r'\s+\?\s+[aA]\d+', '', text)
        text = re.sub(r'\s+[aA]\d+\s*$', '', text)
        text = re.sub(r'\s+\?$', '', text)
        match = re.search(r'[A-Z0-9/]{2,}', text) 
        if match:
            start = match.start()
            text = text[start:]
        return text.strip()