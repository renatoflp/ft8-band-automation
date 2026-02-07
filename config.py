from persistence import ConfigManager

# Carrega a configuração do JSON
_conf = ConfigManager.carregar()

# Distribui as variáveis para o sistema
MY_CALLSIGN = _conf.get("my_callsign", "PP5EO")
FLRIG_URL = _conf.get("flrig_url", "http://127.0.0.1:12345")
JTDX_UDP_IP = _conf.get("jtdx_udp_ip", "224.0.0.1")
JTDX_UDP_PORT = int(_conf.get("jtdx_udp_port", 2237))

# As frequências agora vêm do JSON carregado
FREQUENCIAS = _conf.get("frequencias", {
    "10m": 28074000, "12m": 24915000, "15m": 21074000,
    "17m": 18100000, "20m": 14074000, "30m": 10136000,
    "40m": 7074000,  "80m": 3573000
})