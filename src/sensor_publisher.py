"""
Publicador de sensores (PUBLISHER).

Simula um ou mais sensores de estufa que publicam leituras de
temperatura e umidade em um broker MQTT, em intervalos regulares.

Demonstra o padrão publish/subscribe: o sensor NÃO conhece quem vai
consumir os dados — apenas publica em um tópico. Isso é o que torna a
solução escalável: podemos adicionar dezenas de sensores e múltiplos
consumidores sem que um precise saber do outro.

Uso:
    python src/sensor_publisher.py                 # 3 sensores, setor-a
    python src/sensor_publisher.py --sensores 10   # 10 sensores
    python src/sensor_publisher.py --intervalo 2   # publica a cada 2s
    python src/sensor_publisher.py --setor setor-b
"""
import argparse
import json
import random
import signal
import sys
import time
from datetime import datetime, timezone

import paho.mqtt.client as mqtt

import config


def parse_args():
    p = argparse.ArgumentParser(description="Simulador de sensores de estufa via MQTT")
    p.add_argument("--sensores", type=int, default=3, help="quantidade de sensores simulados")
    p.add_argument("--setor", default="setor-a", help="nome do setor (ex.: setor-a)")
    p.add_argument("--intervalo", type=float, default=3.0, help="segundos entre publicações")
    return p.parse_args()


def criar_cliente(client_id: str) -> mqtt.Client:
    """Cria e conecta um cliente MQTT (API de callback v2 do paho 2.x)."""
    client = mqtt.Client(
        mqtt.CallbackAPIVersion.VERSION2,
        client_id=client_id,
        clean_session=True,
    )
    if config.MQTT_USERNAME:
        client.username_pw_set(config.MQTT_USERNAME, config.MQTT_PASSWORD)

    # Last Will: se o publicador cair sem avisar, o broker publica este
    # aviso automaticamente — recurso nativo do MQTT, útil para IoT.
    client.will_set(
        f"{config.TOPIC_PREFIX}/status/{client_id}",
        payload=json.dumps({"online": False}),
        qos=config.QOS,
        retain=True,
    )

    client.connect(config.MQTT_HOST, config.MQTT_PORT, config.MQTT_KEEPALIVE)
    # Marca o publicador como online (mensagem retida).
    client.publish(
        f"{config.TOPIC_PREFIX}/status/{client_id}",
        json.dumps({"online": True}),
        qos=config.QOS,
        retain=True,
    )
    return client


def gerar_leitura(sensor_id: str, setor: str) -> dict:
    """Gera uma leitura plausível, com pequena variação aleatória."""
    return {
        "sensor_id": sensor_id,
        "setor": setor,
        "temperatura": round(random.uniform(12.0, 36.0), 2),
        "umidade": round(random.uniform(35.0, 85.0), 2),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


def main():
    args = parse_args()
    client = criar_cliente(client_id=f"publisher-{args.setor}-{random.randint(1000, 9999)}")
    client.loop_start()  # rede em thread separada

    rodando = {"ok": True}

    def parar(*_):
        rodando["ok"] = False

    signal.signal(signal.SIGINT, parar)
    signal.signal(signal.SIGTERM, parar)

    print(f"[publisher] Conectado a {config.MQTT_HOST}:{config.MQTT_PORT}")
    print(f"[publisher] Publicando {args.sensores} sensor(es) no setor '{args.setor}' "
          f"a cada {args.intervalo}s (QoS {config.QOS}). Ctrl+C para sair.\n")

    try:
        while rodando["ok"]:
            for i in range(1, args.sensores + 1):
                sensor_id = f"sensor-{i:02d}"
                leitura = gerar_leitura(sensor_id, args.setor)
                topico = f"{config.TOPIC_PREFIX}/{args.setor}/{sensor_id}/dados"
                client.publish(topico, json.dumps(leitura), qos=config.QOS)
                print(f"  -> {topico}  T={leitura['temperatura']}C  U={leitura['umidade']}%", flush=True)
            print("-" * 60, flush=True)
            time.sleep(args.intervalo)
    finally:
        client.loop_stop()
        client.disconnect()
        print("\n[publisher] Encerrado.")


if __name__ == "__main__":
    sys.exit(main())
