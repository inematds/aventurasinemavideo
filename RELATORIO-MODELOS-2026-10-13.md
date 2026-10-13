# Opus × Sonnet × Haiku produzindo episódios — 13/10/2026

Série **Memórias de Aventura** (canal Aventuras INEMA): relato de um leitor + fotos do acervo INEMA viram um documentário curto de 2 a 3,5 min, sem ninguém no meio. Um laço (`produz_loop.sh`) escolhe a matéria, chama `claude -p` (assinatura) com o `PRODUZIR.md` e só põe na fila o que passa no portão (`verifica_ep.py`: duração, áudio, 1920×1080, roteiro).

O agente faz tudo sozinho: lê o relato, separa e classifica as fotos, remasteriza (Codex), escreve o roteiro, narra (voz `nei`, local), monta o filme (motor Python) e confere quadros.

**Decisão:** o produtor fica no **Opus 5.5 com esforço medium**.

## O que foi medido

8 episódios de teste, cada um numa matéria diferente. O custo é o equivalente em API que o próprio Claude Code calcula (`total_cost_usd` do `--output-format json`). Pela assinatura não sai dinheiro, mas é esse o peso no limite do plano.

| Modelo | Esforço | Episódio | Produção | Vídeo | Custo | Por min de vídeo | Qualidade |
|---|---|---|---|---|---|---|---|
| Opus 5.5 | medium | #37 Ronésio, Enduro dos Pampas (produtor normal) | 30 min | 3:27 | US$ 3,83 | US$ 1,11 | boa |
| Opus 5.5 | medium | #31 Faccin, corrida de aventura | 38 min | 3:14 | US$ 3,37 | US$ 1,04 | boa: letreiros contam a história |
| Opus 5.5 | low | #35 Mário Engels, Refeno | 43 min | 3:08 | US$ 2,36 | US$ 0,75 | média: um quadro escuro vazio, erro no letreiro ("VALIDO A PENA") |
| Sonnet 5.5 | medium | #32 Gramado | 37 min | 2:46 | US$ 3,80 | US$ 1,37 | média: virou propaganda de turismo, fotos repetidas |
| Sonnet 5.5 | low | #36 Expedição Ushuaia | 53 min | 3:23 | US$ 2,17 | US$ 0,64 | boa |
| Sonnet 5.5 | low (sem duração mínima) | #29 Naoki, Comitê 2003 | 20 min | 1:54 | US$ 1,18 | US$ 0,62 | boa, mas curta |
| Haiku 5.5 | low (sem duração mínima) | #28 Luiz, Paulo Afonso | 19 min | 1:48 | US$ 0,49 | US$ 0,27 | fraca |

Antes dos testes, o produtor normal (Opus medium) fez #21 a #26 em 21 a 52 min cada, com vídeos de 3:00 a 3:18 e 5,5 a 13 milhões de tokens lidos por episódio.

## O que aprendemos

1. **O trabalho em tokens é parecido entre Opus e Sonnet.** Por segundo de vídeo, os dois leem cerca de 30 mil tokens (quase tudo cache). A diferença de custo vem do preço do token, não de um modelo trabalhar menos.
2. **O Haiku custa pouco porque o token é barato, não porque trabalha menos.** Leu o dobro de tokens por segundo de vídeo (erra e refaz) e entregou o pior filme: foto repetida, recorte borrado, letreiro ilegível sobre mosaico e legenda que contradiz a foto ("pista molhada" num dia de sol).
3. **O esforço não era igual.** O `settings.json` dá esforço medium só ao Opus (`modelSettings`); Sonnet e Haiku caíam no padrão geral, low. Comparação justa exige `--effort` explícito, e o produtor agora passa sempre `--model` e `--effort`.
4. **O conselheiro (advisor) pesa.** No Sonnet medium, US$ 1,54 dos US$ 3,80 foram consultas ao Fable 5.1, o `advisorModel` do settings. O Opus não chamou o conselheiro.
5. **Sem regra de duração, o Sonnet faz vídeos curtos** (1:54). Com "mínimo 2:30", chegou a 2:46 e 3:23.
6. **Uma amostra por combinação é pouco.** O Sonnet low foi bem no Ushuaia (US$ 0,64/min), mas o Opus medium foi o único que saiu bom nas duas vezes medidas e também em #21 a #26. Ele é a referência de qualidade; o Sonnet low fica como candidato para um teste maior se o limite da assinatura apertar.
7. **A matéria pesa tanto quanto o modelo.** Texto de turismo (Gramado) ou agenda de evento rende filme fraco em qualquer modelo; o agente já descarta sozinho texto enciclopédico e agenda sem relato.

## Consertos que saíram dos testes

- **Fotos coladas na borda.** As cópias em polaroid iam para os cantos (o zoom lento da câmera cortava a ponta) e o meio da tela ficava vazio. Agora cada cópia cabe inteira, contando o zoom, e o centro tem prioridade (`motor/render_v3.py`, classe `Pilha`).
- **Corrida entre processos.** O laço principal "retomou" o episódio do teste e deu o mesmo número a dois episódios. Candidato de teste agora leva `teste=<modelo>` e a escolha passa por trava (`flock`).
- **Custo de cada episódio no `produz.log`** (`pronto em 30 min, US$ 3,83 → fila`).
- **Modo teste no produtor:** `MODELO=… ESFORCO=… EXTRA="regra" UMA=1 NA_FILA=0 ./produz_loop.sh` faz um episódio fora da fila.

## Quanto custa a série

Com Opus medium, cerca de **US$ 3,50 equivalentes por episódio** (US$ 1,05 a 1,10 por minuto de vídeo). Em 8 episódios por dia, uns US$ 28 equivalentes por dia, todos dentro da assinatura, que também é usada no trabalho do dia a dia. Narração, render e trilha rodam no servidor e não usam LLM.
