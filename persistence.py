import json
import os

ARQUIVO_CONFIG_JSON = "config_jtdx.json"

DEFAULT_CONFIG = {
    "my_callsign": "PP5EO",
    "flrig_url": "http://127.0.0.1:12345",
    "jtdx_udp_ip": "224.0.0.1",
    "jtdx_udp_port": 2237,
    
    # Voltamos para a lista simples
    "frequencias": {
        "10m": 28074000, "12m": 24915000, "15m": 21074000,
        "17m": 18100000, "20m": 14074000, "30m": 10136000,
        "40m": 7074000,  "80m": 3573000
    },

    "intervalo": "10 min",
    "inicio_dia": "07:00",
    "fim_dia": "18:30",
    "delay_pos_tx": "300",
    "audio_mudo": False,
    "bandas_dia": ["10m", "12m", "15m"],
    "bandas_noite": ["40m", "80m"],
    "watchlists": {}
}

class ConfigManager:
    @staticmethod
    def carregar():
        if not os.path.exists(ARQUIVO_CONFIG_JSON):
            ConfigManager.salvar(DEFAULT_CONFIG)
            return DEFAULT_CONFIG.copy()
        try:
            with open(ARQUIVO_CONFIG_JSON, 'r') as f:
                dados = json.load(f)
                padrao = DEFAULT_CONFIG.copy()
                
                for k, v in padrao.items():
                    if k not in dados:
                        dados[k] = v
                
                # Garante que usamos a lista simples de frequências
                # Se o arquivo tiver "10m FT4", isso vai limpar na próxima execução
                if "frequencias" not in dados or "10m FT4" in dados["frequencias"]:
                    dados["frequencias"] = padrao["frequencias"]
                            
                return dados
        except:
            return DEFAULT_CONFIG.copy()

    @staticmethod
    def salvar(dados):
        try:
            with open(ARQUIVO_CONFIG_JSON, 'w') as f:
                json.dump(dados, f, indent=4)
        except Exception as e:
            print(f"Erro ao salvar config: {e}")