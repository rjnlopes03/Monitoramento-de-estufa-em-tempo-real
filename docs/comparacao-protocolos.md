# Comparação de Protocolos para o Cenário da Estufa

Cenário: **monitoramento de temperatura e umidade** de muitos sensores de baixo
custo, em rede possivelmente instável, com necessidade de alertas em tempo quase
real, histórico e capacidade de **escalar**.

## Tabela comparativa

| Critério | **MQTT** ✅ | CoAP | AMQP | HTTP | MCP |
|---|---|---|---|---|---|
| Modelo | Pub/Sub (broker) | Cliente/Servidor (REST-like) | Filas/Exchanges (broker) | Requisição/Resposta | Cliente↔Servidor (LLM↔ferramentas) |
| Transporte | TCP | UDP | TCP | TCP | stdio / HTTP+SSE |
| Peso / overhead | Muito leve | Levíssimo | Médio/pesado | Pesado (cabeçalhos) | Médio |
| Tempo real (push) | Sim | Parcial (observe) | Sim | Não (polling) | Sob demanda |
| Confiabilidade | QoS 0/1/2 | Confirmável (CON) | Forte (ack, durável) | Garantida pelo TCP | Depende do transporte |
| Muitos dispositivos | Excelente | Bom | Bom (mais pesado) | Ruim (1:1) | Não é o foco |
| Consumo de energia | Baixo | Muito baixo | Médio | Alto | N/A |
| Ecossistema IoT | Enorme | Bom | Corporativo | Universal | Emergente (IA) |

## Por que MQTT vence neste cenário

- **Pub/Sub desacoplado:** sensores não conhecem os consumidores. Adicionar um
  novo painel ou serviço de alerta não exige mudar os sensores — escalabilidade
  natural.
- **Leve e econômico:** ideal para dispositivos de baixa potência publicando com
  frequência.
- **Push em tempo real:** o broker entrega assim que chega; sem polling.
- **Resiliência:** QoS, sessões persistentes e Last Will lidam bem com quedas de
  rede comuns em IoT.

## Limitações dos demais para ESTE cenário

- **HTTP:** requisição/resposta 1:1 e cabeçalhos pesados. Para receber dados em
  tempo real, o servidor teria que ficar fazendo *polling* — caro e com latência.
  Ótimo para APIs e integrações pontuais, não para telemetria contínua de muitos
  sensores.
- **CoAP:** excelente e ainda mais leve que MQTT (UDP), forte concorrente em
  redes muito restritas. Perde aqui pela distribuição 1-para-N: o modelo
  cliente/servidor não entrega naturalmente o mesmo dado a vários consumidores
  como o broker pub/sub faz; o ecossistema/ferramentas de pub/sub é menor.
- **AMQP:** muito robusto (filas duráveis, roteamento avançado), mas mais
  **pesado** e voltado a mensageria corporativa/transacional. Overhead
  desnecessário para sensores simples de estufa.
- **MCP (Model Context Protocol):** resolve um problema **diferente** — conectar
  modelos de IA a ferramentas/dados externos. Não é um protocolo de telemetria de
  sensores. Seria adequado se o objetivo fosse, por exemplo, um agente de IA
  consultando/atuando sobre a estufa — possível evolução futura, mas não o núcleo
  do problema atual.

## Conclusão

Para telemetria de muitos sensores, leve, em tempo real e escalável, **MQTT** é a
escolha mais equilibrada. CoAP seria a segunda opção em redes ultrarrestritas;
HTTP/AMQP/MCP atendem a outras necessidades (APIs, mensageria corporativa,
integração com IA, respectivamente).
