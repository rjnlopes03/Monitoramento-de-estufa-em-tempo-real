# 🌱 Monitoramento de Estufa em Tempo Real com MQTT

> Desafio Prático – Aplicação de Protocolos para IoT e Comunicação Distribuída
> Disciplina de **Redes de Computadores** · Prof. **Silvio**

Prova de conceito de um sistema de **monitoramento de sensores de uma estufa**
(temperatura e umidade) usando o protocolo **MQTT**. Sensores publicam leituras,
e múltiplos consumidores (um monitor de terminal e um dashboard web) recebem os
dados simultaneamente, com **alertas automáticos** e **persistência** em banco.

O projeto começa **simples, porém funcional**, e foi desenhado para **escalar**
ao longo do semestre (mais sensores, broker dedicado, banco de séries temporais,
TLS/autenticação, etc.).

---

## 📌 Cenário escolhido

Uma estufa possui sensores distribuídos por setores, medindo **temperatura** e
**umidade** das plantas.

### ❗ O problema

Hoje o acompanhamento das condições da estufa é **manual e pontual**: alguém
precisa verificar os sensores de tempos em tempos. Isso gera consequências:

- variações fora da faixa ideal (calor excessivo, umidade baixa) **só são
  percebidas tarde**, podendo **danificar ou perder a plantação**;
- **não há histórico** para entender padrões e tomar decisões;
- conforme a estufa cresce, **acompanhar dezenas de sensores manualmente fica
  inviável**.

### 💡 O que estamos resolvendo

Um sistema que **coleta automaticamente** as leituras de todos os sensores em
tempo real, **avisa na hora** (alerta) quando algum valor sai da faixa segura e
**guarda o histórico** para análise — funcionando mesmo com **dispositivos de
baixo custo/energia** e **rede instável**, e pronto para **escalar** para muitos
sensores.

Para isso, a central precisa:

- receber leituras de **muitos sensores** ao mesmo tempo;
- **alertar** quando algum valor sair da faixa segura;
- **armazenar** o histórico para análise;
- funcionar com **dispositivos de baixo custo/energia** e rede instável.

---

## ✅ Por que MQTT? (justificativa técnica)

| Requisito do cenário | Como o MQTT atende |
|---|---|
| Muitos dispositivos | Modelo **publish/subscribe** desacopla produtores de consumidores |
| Baixo consumo de banda/energia | Protocolo **leve** sobre TCP, cabeçalho mínimo |
| Rede instável | **QoS 0/1/2**, sessões persistentes e **Last Will** (aviso de queda) |
| Escalabilidade | Broker central distribui mensagens para N assinantes |
| Tempo quase real | Entrega **push** (sem polling), baixa latência |

Comparação completa com **HTTP, CoAP, AMQP e MCP** em
[`docs/comparacao-protocolos.md`](docs/comparacao-protocolos.md).

---

## 🏗️ Arquitetura

```
                          (publish)                      (subscribe)
   ┌──────────────┐                  ┌──────────────┐                ┌─────────────────────┐
   │  Sensores    │ ───────────────▶ │   Broker     │ ─────────────▶ │ monitor_subscriber  │  (terminal + alertas)
   │ (publisher)  │   estufa/.../    │    MQTT      │   estufa/#     ├─────────────────────┤
   │  N sensores  │      dados       │ (Mosquitto/  │                │ dashboard.py (web)  │  (cards em tempo real)
   └──────────────┘                  │   HiveMQ)    │                └─────────┬───────────┘
                                     └──────────────┘                          │
                                                                               ▼
                                                                        SQLite (histórico)
```

**Topologia de tópicos:** `estufa-redes-silvio/<setor>/<sensor_id>/dados`
Ex.: `estufa-redes-silvio/setor-a/sensor-01/dados`

O curinga `#` permite que qualquer assinante receba tudo de todos os sensores —
é isso que permite rodar o monitor de terminal e o dashboard **ao mesmo tempo**,
consumindo as mesmas mensagens, sem o publicador saber que eles existem.

---

## 📂 Estrutura do projeto

```
.
├── src/
│   ├── config.py              # configuração central (broker, tópicos, limites)
│   ├── sensor_publisher.py    # PUBLISHER — simula N sensores
│   ├── monitor_subscriber.py  # SUBSCRIBER — terminal + alertas + persistência
│   ├── dashboard.py           # SUBSCRIBER web (Flask) + API REST
│   ├── db.py                  # camada de persistência (SQLite)
│   └── templates/index.html   # painel web
├── docker-compose.yml         # broker Mosquitto local (opcional)
├── mosquitto/config/mosquitto.conf
├── docs/comparacao-protocolos.md
├── requirements.txt
└── README.md
```

---

## 🚀 Como executar

### Pré-requisitos
- Python 3.10+
- (Opcional) Docker, caso queira rodar o broker localmente

### 1) Instalar dependências
```bash
pip install -r requirements.txt
```

### 2) Escolher o broker

**Opção A — sem instalar nada (broker público):** já é o padrão
(`broker.hivemq.com`). Pule para o passo 3.

**Opção B — broker local com Docker (recomendado para produção):**
```bash
docker compose up -d
# Windows PowerShell:
$env:MQTT_HOST = "localhost"
# Linux/macOS:
export MQTT_HOST=localhost
```

### 3) Rodar o sistema (use 3 terminais)

**Terminal 1 — Monitor (terminal + alertas):**
```bash
python src/monitor_subscriber.py
```

**Terminal 2 — Dashboard web:**
```bash
python src/dashboard.py
# abra http://localhost:8000
```

**Terminal 3 — Sensores (publisher):**
```bash
python src/sensor_publisher.py --sensores 5 --setor setor-a --intervalo 2
```

Dá para subir **vários publishers** em paralelo (outros setores) para ver a
solução escalando:
```bash
python src/sensor_publisher.py --setor setor-b --sensores 4
```

---

## 🔔 Alertas

O monitor compara cada leitura com a faixa segura (configurável):

| Variável | Padrão | Significado |
|---|---|---|
| `TEMP_MIN` / `TEMP_MAX` | 15 / 32 °C | faixa de temperatura |
| `UMID_MIN` / `UMID_MAX` | 40 / 80 % | faixa de umidade |

Exemplo (forçar alertas de temperatura):
```bash
# Windows PowerShell
$env:TEMP_MAX = "30"; python src/monitor_subscriber.py
```

---

## ⚙️ Configuração (variáveis de ambiente)

Todos os parâmetros têm padrão em [`src/config.py`](src/config.py) e podem ser
sobrescritos por variável de ambiente:

| Variável | Padrão | Descrição |
|---|---|---|
| `MQTT_HOST` | `broker.hivemq.com` | endereço do broker |
| `MQTT_PORT` | `1883` | porta do broker |
| `TOPIC_PREFIX` | `estufa-redes-silvio` | prefixo dos tópicos |
| `MQTT_QOS` | `1` | qualidade de serviço (0/1/2) |
| `DB_PATH` | `data/leituras.db` | arquivo SQLite |
| `WEB_PORT` | `8000` | porta do dashboard |

> Dica: no broker **público**, troque `TOPIC_PREFIX` por algo único (ex.: seu
> nome) para não misturar suas mensagens com as de outras pessoas.

---

## 🧪 Recursos de MQTT demonstrados

- **Publish/Subscribe** com hierarquia de tópicos e curinga `#`
- **QoS 1** (entrega ao menos uma vez)
- **Retained messages** (status online/offline)
- **Last Will and Testament** (aviso automático de queda do sensor)
- **Múltiplos assinantes** consumindo o mesmo fluxo

---

## 🔭 Roadmap (evolução ao longo do semestre)

- [x] **Semana 1:** publisher + subscriber + broker + alertas + dashboard (este entregável)
- [ ] **Semana 2:** broker dedicado com **autenticação** e **TLS** (porta 8883)
- [ ] **Semana 3:** banco de **séries temporais** (InfluxDB) + gráficos históricos
- [ ] **Semana 4:** sensores físicos (ESP32) e/ou contêineres; deploy em nuvem

---

## 📊 Resultados obtidos

- Comunicação ponta a ponta validada contra broker público: sensores publicam,
  monitor e dashboard recebem **simultaneamente**.
- Alertas disparados corretamente quando valores saem da faixa.
- Histórico persistido em SQLite e exposto via API REST (`/api/estado`,
  `/api/historico`) consumida pelo painel web.

---

## 👤 Autor

Projeto desenvolvido para a disciplina de Redes de Computadores — desafio
proposto pelo Prof. Silvio.
