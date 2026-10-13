# FALHAS — aventurasinemavideo

| data | o que quebrou | menor correção | prompt \| infra |
|---|---|---|---|
| 13/10/2026 | teste de modelo (Sonnet) e laço principal (Opus) mexeram no mesmo episódio: o laço "retomou" o em_producao do teste, reprovou em 1 min e renomeou o EPISODIO.json; dois #27 | candidato do teste ganha `teste=<modelo>` e a retomada pula esses; reiniciar aventuras-produz antes do próximo teste | infra |
| 13/10/2026 | #28 com dois agentes na mesma pasta: a retomada do `produz_loop.sh` pegou um `em_producao` que outro laço (teste Haiku) produzia naquele momento | retomar só se nenhum `claude -p` vivo tiver a pasta (gravar PID na reserva e checar com `kill -0`) | infra |
| 13/10/2026 | cópias de foto da `Pilha` iam para a borda (cortadas pelo zoom da câmera) e o meio da tela ficava vazio: a escolha só maximizava a distância entre as cópias | posição limitada para a cópia caber inteira (tamanho girado + margem do zoom) e nota que desconta a distância do centro | infra |
| 12/10/2026 | fila parou 11/10 08:03 (codex 0.116 do /usr/bin morreu no config.toml) e ficou 18 h parada sem ninguém saber; 9 episódios prontos e e-mails de aviso já enviados | PATH com ~/.npm-global/bin no fila_publicar.sh + erro vira pedido de ajuda no bot v3 repetido a cada 30 min, sem sair | infra + prompt |
| 11/10/2026 | #19: voz `nei` gaguejou antes de citação com dois-pontos ("pergunta: Fei, vocês…") e leu "USB" como "os bi" | fala em discurso indireto sem dois-pontos e sigla escrita como se fala ("u-esse-bê"); citação literal só no letreiro | prompt |
| 11/10/2026 | #17: render caiu com "box can't exceed original image size": `Pilha` sem `z` (zoom 1,012) e muitas cópias com `every` curto somam tremida maior que a margem | dar `z=(1.02, 1.08)` ou mais a toda `Pilha` com muitas cópias/tremida | infra |
| 10/10/2026 | #13: última palavra do bloco ("jamanta") sumiu do WAV final: Whisper não a transcreveu no bruto e o `pos_voz` corta na última palavra transcrita | conferir a última palavra de cada bloco na transcrição; faltou = gerar o bloco de novo | infra |
| 10/10/2026 | #13 (evitado): `conta=` com v1 ≥ 100 arredonda a dezenas, 273 vira "270 KM" | número que não termina em 0 vai como texto fixo, sem `conta` | infra |
| 10/10/2026 | #13: mapa regional (~1,5°) com `MS` alto engrossa bordas e letreiros do `mapa_base` e o litoral do paises.geojson fica grosseiro | `mapa_base` próprio no filme.py com terra = uf.json e mar claro (rótulo escuro legível) | infra |
| 10/10/2026 | #12: voz `nei` estropiou nome espanhol ("El Tatio" 3× → Altatiel/Eltatil; "San Antonio de los Cobres" → Luscovitz) | tirar o nome da fala e deixar no letreiro | prompt |
| 10/10/2026 | #7: render travou 20 min sem erro (âncora `Wd` inexistente → SystemExit no worker do Pool) | validar `filme.blocos()` num processo só antes do render | prompt |
| 10/10/2026 | #7: contador `conta=(2500, 4800, …)` mostrou "27.300 METROS" (precedência na fórmula do render_v4) | parênteses na fórmula do motor (corrigido em motor/render_v4.py) | infra |
