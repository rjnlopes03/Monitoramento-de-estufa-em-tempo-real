"""
Configuração central do projeto.

Todos os parâmetros podem ser sobrescritos por variáveis de ambiente,
o que facilita escalar a solução (trocar de broker, mudar tópicos,
ajustar limites de alerta) sem alterar o código.
"""
import os

# ---------------------------------------------------------------------------
# Broker MQTT
# ---------------------------------------------------------------------------
# Por padrão usamos um broker público de testes para que o projeto rode
# imediatamente, sem precisar instalar nada. Para produção/local, suba o
# Mosquitto via docker-compose e use MQTT_HOST=localhost.
MQTT_HOST = os.getenv("MQTT_HOST", "broker.hivemq.com")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
MQTT_USERNAME = os.getenv("MQTT_USERNAME", "")  # opcional
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD", "")  # opcional
MQTT_KEEPALIVE = int(os.getenv("MQTT_KEEPALIVE", "60"))

# ---------------------------------------------------------------------------
# Topologia de tópicos
# ---------------------------------------------------------------------------
# Hierarquia: <prefixo>/<setor>/<sensor_id>/<grandeza>
# Ex.: estufa/setor-a/sensor-01/temperatura
# Um prefixo único evita colisão com outras pessoas no broker público.
TOPIC_PREFIX = os.getenv("TOPIC_PREFIX", "estufa-redes-silvio")

# Curinga usado pelos assinantes para receber tudo de todos os sensores.
TOPIC_SUBSCRIBE = f"{TOPIC_PREFIX}/#"

# ---------------------------------------------------------------------------
# Qualidade de Serviço (QoS)
# ---------------------------------------------------------------------------
# 0 = no máximo uma vez | 1 = ao menos uma vez | 2 = exatamente uma vez
# Usamos 1 por padrão: bom equilíbrio entre confiabilidade e overhead.
QOS = int(os.getenv("MQTT_QOS", "1"))

# ---------------------------------------------------------------------------
# Limites para geração de alertas (cenário: estufa)
# ---------------------------------------------------------------------------
TEMP_MIN = float(os.getenv("TEMP_MIN", "15.0"))
TEMP_MAX = float(os.getenv("TEMP_MAX", "32.0"))
UMID_MIN = float(os.getenv("UMID_MIN", "40.0"))
UMID_MAX = float(os.getenv("UMID_MAX", "80.0"))

# ---------------------------------------------------------------------------
# Persistência
# ---------------------------------------------------------------------------
DB_PATH = os.getenv("DB_PATH", "data/leituras.db")

# ---------------------------------------------------------------------------
# Dashboard web
# ---------------------------------------------------------------------------
WEB_HOST = os.getenv("WEB_HOST", "0.0.0.0")
WEB_PORT = int(os.getenv("WEB_PORT", "8000"))
