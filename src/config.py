"""
Configuração central do projeto.

Todos os parâmetros podem ser sobrescritos por variáveis de ambiente,
o que facilita escalar a solução (trocar de broker, mudar tópicos,
ajustar limites de alerta) sem alterar o código.
"""
import os

# --- Broker MQTT ---

MQTT_HOST = os.getenv("MQTT_HOST", "broker.hivemq.com")
"""Endereço do broker. Por padrão, um broker público de testes para que o
projeto rode imediatamente; para produção/local, suba o Mosquitto via
docker-compose e use ``MQTT_HOST=localhost``."""

MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
"""Porta do broker MQTT (1883 = padrão sem TLS)."""

MQTT_USERNAME = os.getenv("MQTT_USERNAME", "")
"""Usuário para autenticação no broker (opcional)."""

MQTT_PASSWORD = os.getenv("MQTT_PASSWORD", "")
"""Senha para autenticação no broker (opcional)."""

MQTT_KEEPALIVE = int(os.getenv("MQTT_KEEPALIVE", "60"))
"""Intervalo de keep-alive, em segundos, entre cliente e broker."""

# --- Topologia de tópicos ---

TOPIC_PREFIX = os.getenv("TOPIC_PREFIX", "estufa-redes-silvio")
"""Prefixo da hierarquia ``<prefixo>/<setor>/<sensor_id>/<grandeza>``
(ex.: ``estufa/setor-a/sensor-01/temperatura``). Um prefixo único evita
colisão com outras pessoas no broker público."""

TOPIC_SUBSCRIBE = f"{TOPIC_PREFIX}/#"
"""Curinga usado pelos assinantes para receber tudo de todos os sensores."""

# --- Qualidade de Serviço (QoS) ---

QOS = int(os.getenv("MQTT_QOS", "1"))
"""Nível de QoS: 0 = no máximo uma vez | 1 = ao menos uma vez |
2 = exatamente uma vez. Padrão 1: bom equilíbrio entre confiabilidade e
overhead."""

# --- Limites para geração de alertas (cenário: estufa) ---

TEMP_MIN = float(os.getenv("TEMP_MIN", "15.0"))
"""Temperatura mínima segura, em °C; abaixo disso gera alerta."""

TEMP_MAX = float(os.getenv("TEMP_MAX", "32.0"))
"""Temperatura máxima segura, em °C; acima disso gera alerta."""

UMID_MIN = float(os.getenv("UMID_MIN", "40.0"))
"""Umidade mínima segura, em %; abaixo disso gera alerta."""

UMID_MAX = float(os.getenv("UMID_MAX", "80.0"))
"""Umidade máxima segura, em %; acima disso gera alerta."""

# --- Persistência ---

DB_PATH = os.getenv("DB_PATH", "data/leituras.db")
"""Caminho do arquivo SQLite onde as leituras são armazenadas."""

# --- Dashboard web ---

WEB_HOST = os.getenv("WEB_HOST", "0.0.0.0")
"""Endereço de bind do servidor web (0.0.0.0 = todas as interfaces)."""

WEB_PORT = int(os.getenv("WEB_PORT", "8000"))
"""Porta HTTP do dashboard web."""
