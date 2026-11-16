# IA do produtor Memórias de Aventura

Motor, modelo e esforço ficam em **auto/ia.yaml**, com opções comentadas com `#`.
Cada chamada relê o arquivo; uma produção que já começou termina com a configuração anterior.

Ativo: **assinatura Codex / gpt-6.1-sol / medium** nas etapas `producao` e `classificacao`.
`producao` é o agente que segue PRODUZIR.md; `classificacao` lê as fotos e devolve JSON.
A remasterização de imagens continua sempre no Codex assinatura (`motor/remaster_codex.py`).
Voz local, render, validação do vídeo, fila, horários, canal e e-mails seguem o fluxo existente.

Ver e alterar sem mexer em código:

```bash
ia-crons ver aventura
ia-crons configurar aventura producao --tipo assinatura --motor codex --modelo gpt-6.1-sol --esforco high
ia-crons configurar aventura classificacao --tipo assinatura --motor claude --modelo claude-opus-5-5 --esforco medium
ia-crons validar aventura
```

São exemplos; a configuração entregue permanece Codex/medium em ambas as etapas.
Também funciona sem o atalho do WiFi: `python3 auto/ia_motor.py ver` e `configurar ...`.
O configurador preserva os comentários. Modelo e esforço não são herdados de MODELO, ESFORCO ou seletores globais antigos.
O login do CLI é o da assinatura. Não copie credenciais para este projeto.

As alternativas API Anthropic, OpenAI e OpenRouter estão documentadas no YAML e **desativadas**.
O agente completo exige assinatura com ferramentas; trocar apenas o tipo para API não cria um agente e é recusado.
A etapa de classificação admite os adaptadores de visão, mas qualquer API depende de autorização explícita
para este projeto e esta finalidade, além de modelo compatível com visão. Nenhuma API de modelo foi usada na adaptação.

O serviço `aventuras-produz.service` continua supervisionando o laço, com 48 GB de memória e 4 horas por episódio.
Falhas de execução, cota, login ou timeout mantêm a matéria em `em_producao`, avisam o v3 e retomam após 30 minutos.
Um episódio executado mas reprovado no portão continua sendo tratado como erro de produção.
O produtor não sobe B2, publica nem envia e-mail; isso continua com `aventuras-fila.service`.
Mensagens de episódio pronto continuam no inemaytbot. Não reinicie o produtor durante um episódio.

Diagnóstico local: `privado/produz.log`, `privado/tarefas/<slug>.log` e `ia-execucoes.jsonl` (fora do git).
A telemetria informa o motor, modelo, esforço, duração e estado; não inventa custo em dólares para assinatura.

Validação realizada: cinco testes de contrato, incluindo falha do motor sem perder matéria/fila e reprovação editorial;
`bash -n produz_loop.sh`; ensaio real do Codex escrevendo e relendo um marcador em pasta isolada,
sem produzir episódio nem publicar no ensaio; classificação visual real distinguiu quadrado vermelho e círculo azul corretamente. Evidências no WiFi/output de crons de 15/11/2026.

```bash
python3 -m unittest discover -s auto/tests -v
bash -n produz_loop.sh
```
