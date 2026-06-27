"""
Dashboard web (SUBSCRIBER + visualização).

Sobe um servidor Flask que, em uma thread de fundo, assina os mesmos
tópicos MQTT e mantém o estado atualizado em SQLite. A página web faz
polling em /api/estado e /api/historico para mostrar cards por sensor
e alertas em tempo (quase) real.

É a prova de que o modelo pub/sub escala: este dashboard e o
monitor_subscriber.py consomem as MESMAS mensagens simultaneamente.

Uso:
    python src/dashboard.py
    # abra http://localhost:8000
"""
import json
import threading

import paho.mqtt.client as mqtt
from flask import Flask, jsonify, render_template

import config
import db
from monitor_subscriber import avaliar_alertas

app = Flask(__name__)


# ---------------------------------------------------------------------------
# Cliente MQTT em thread de fundo
# ---------------------------------------------------------------------------
def on_connect(client, userdata, flags, reason_code, properties):
    client.subscribe(config.TOPIC_SUBSCRIBE, qos=config.QOS)
    print(f"[dashboard] MQTT conectado. Assinando '{config.TOPIC_SUBSCRIBE}'.")


def on_message(client, userdata, msg):
    if not msg.topic.endswith("/dados"):
        return
    try:
        leitura = json.loads(msg.payload.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return
    db.salvar_leitura(leitura)


def iniciar_mqtt():
    db.init_db()
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="dashboard-web")
    if config.MQTT_USERNAME:
        client.username_pw_set(config.MQTT_USERNAME, config.MQTT_PASSWORD)
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(config.MQTT_HOST, config.MQTT_PORT, config.MQTT_KEEPALIVE)
    client.loop_forever()


# ---------------------------------------------------------------------------
# Rotas HTTP
# ---------------------------------------------------------------------------
@app.route("/")
def index():
    return render_template(
        "index.html",
        broker=f"{config.MQTT_HOST}:{config.MQTT_PORT}",
        prefixo=config.TOPIC_PREFIX,
    )


@app.route("/api/estado")
def api_estado():
    estado = db.estado_atual()
    for s in estado:
        s["alertas"] = avaliar_alertas(s)
    return jsonify(
        {
            "sensores": estado,
            "limites": {
                "temp_min": config.TEMP_MIN,
                "temp_max": config.TEMP_MAX,
                "umid_min": config.UMID_MIN,
                "umid_max": config.UMID_MAX,
            },
        }
    )


@app.route("/api/historico")
def api_historico():
    return jsonify(db.ultimas_leituras(limite=60))


if __name__ == "__main__":
    threading.Thread(target=iniciar_mqtt, daemon=True).start()
    print(f"[dashboard] Acesse http://localhost:{config.WEB_PORT}")
    # use_reloader=False evita abrir duas conexões MQTT
    app.run(host=config.WEB_HOST, port=config.WEB_PORT, debug=False, use_reloader=False)
