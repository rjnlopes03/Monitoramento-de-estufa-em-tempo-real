"""
Monitor de sensores (SUBSCRIBER) — núcleo "básico e funcional".

Assina TODOS os tópicos da estufa, exibe as leituras em tempo real,
persiste em SQLite e dispara ALERTAS quando temperatura/umidade saem
da faixa segura definida em config.py.

Por causa do modelo publish/subscribe do MQTT, podem existir vários
monitores rodando ao mesmo tempo (este aqui, o dashboard web, etc.),
todos recebendo as mesmas mensagens sem que o publicador saiba.

Uso:
    python src/monitor_subscriber.py
"""
import json
import signal
import sys
from datetime import datetime

import paho.mqtt.client as mqtt

import config
import db

# No Windows o console costuma usar cp1252 e quebra ao imprimir símbolos
# fora do ASCII. Forçamos UTF-8 (com fallback seguro) para evitar crashes.
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except (AttributeError, ValueError):
    pass


def avaliar_alertas(leitura: dict):
    alertas = []
    t = leitura.get("temperatura")
    u = leitura.get("umidade")
    if t is not None and (t < config.TEMP_MIN or t > config.TEMP_MAX):
        alertas.append(f"TEMPERATURA fora da faixa ({t}C | ok: {config.TEMP_MIN}-{config.TEMP_MAX})")
    if u is not None and (u < config.UMID_MIN or u > config.UMID_MAX):
        alertas.append(f"UMIDADE fora da faixa ({u}% | ok: {config.UMID_MIN}-{config.UMID_MAX})")
    return alertas


def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code == 0:
        client.subscribe(config.TOPIC_SUBSCRIBE, qos=config.QOS)
        print(f"[monitor] Conectado. Assinando '{config.TOPIC_SUBSCRIBE}' (QoS {config.QOS}).\n")
    else:
        print(f"[monitor] Falha na conexão: {reason_code}")


def on_message(client, userdata, msg):
    # Ignora mensagens de status (online/offline) — só processa dados.
    if msg.topic.endswith("/dados") is False:
        return
    try:
        leitura = json.loads(msg.payload.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        print(f"[monitor] Payload inválido em {msg.topic}")
        return

    db.salvar_leitura(leitura)

    hora = datetime.now().strftime("%H:%M:%S")
    base = (f"[{hora}] {leitura.get('setor')}/{leitura.get('sensor_id')}  "
            f"T={leitura.get('temperatura')}C  U={leitura.get('umidade')}%")
    alertas = avaliar_alertas(leitura)
    if alertas:
        print(f"{base}  [ALERTA] " + " | ".join(alertas), flush=True)
    else:
        print(f"{base}  [OK]", flush=True)


def main():
    db.init_db()

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="monitor-cli")
    if config.MQTT_USERNAME:
        client.username_pw_set(config.MQTT_USERNAME, config.MQTT_PASSWORD)
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(config.MQTT_HOST, config.MQTT_PORT, config.MQTT_KEEPALIVE)

    def parar(*_):
        print("\n[monitor] Encerrando...")
        client.disconnect()

    signal.signal(signal.SIGINT, parar)
    signal.signal(signal.SIGTERM, parar)

    client.loop_forever()


if __name__ == "__main__":
    sys.exit(main())
