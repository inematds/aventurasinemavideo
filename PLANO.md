# aventurasinemavideo — plano e regras

Transforma em vídeo narrado as matérias do acervo INEMA Aventura (aventura.inema.club) que têm relato e imagens.
A série chama-se **Memórias de Aventura**. Ela é publicada no canal **Aventuras INEMA**
(https://www.youtube.com/@aventurasinema, yt-pubx `--canal aventuras`, conta aventurasinema@gmail.com).

## A regra do Nei (10/10/2026, palavras dele)

> "cada dia vc faz 6 videos e publica, sempre 2 materias dos q tem assinatura e mais 4 de outros, pode variando.
> crie um doc dos q vc ja fez dentro do projeto gerencia isso. mas quem nao tem assinatura apenas faca 1, e notifica ele,
> passa o link do canal aqui tambem. a ideia é todas materias q tiver relatos e imagens a gente fazer videos."

O que isso significa na operação:

| Item | Regra |
|---|---|
| Vídeos por dia | 4, às 8, 12, 16 e 20 h (regra de 22/10/2026: o canal já tem 2 shorts por dia e os avulsos; antes 8 por dia, 6 às 20 h). A fila (`fila_publicar.sh` + `espera_slot.py`) publica um por horário e para no 4º do dia |
| De assinantes pagos | 2 por dia. Conta **matérias**, não pessoas: um assinante pode ter vários vídeos, um por matéria com relato e fotos |
| De não assinantes | 4 por dia, variando os assuntos (moto, trilha, escalada, jipe, cavalgada, viagem…). **No máximo 1 vídeo por pessoa** |
| Publicação | sempre no canal Aventuras INEMA, sem capa enquanto o canal não for verificado |
| Aviso | sai assim que o episódio entra na fila, mesmo antes do YouTube (download + canal; 11/10/2026). E-mail a **todas** as pessoas ligadas à matéria (autor, participantes, fotógrafos; assinante ou não; menos o próprio Nei), com o link do vídeo, do download (B2) e do canal (regra de 10/10/2026) |
| Letreiros | o título que antes ficava no meio vai para o **topo** da tela, para não cobrir a foto (pedido de 10/10/2026). Exceção: sobre as fotos em linha (beat `Faixa`, tipo filme) e no bloco final (fecho) o letreiro continua no centro, automático |
| Meta | toda matéria do acervo com relato e imagens vira vídeo |
| Sem assinante disponível | completar o dia com não assinantes e anotar em EPISODIOS.md |

Autorizações registradas:
- **Resend (e-mail)**: assinantes desde 09/10/2026; **não assinantes desde 10/10/2026** ("notifica ele"). Remetente `Nei · INEMA Aventura <acesso@inema.club>`, reply_to `contato@inema.club`. Chave `RESEND_API_KEY` em `~/projetos/inemaonline/worker/.dev.vars`, lida em runtime, nunca impressa.
- **YouTube Data API do canal aventuras**: publicar, editar e apagar (10/10/2026). Token em `~/.config/yt-pubx/tokens/aventuras.json`.
- Antes de 10/10 a série saía no lives10. Os 6 primeiros foram republicados no Aventuras INEMA e **apagados do lives10** com ok do Nei.

## O que é "matéria com relato e imagens" (critério de corte)

- Texto próprio da aventura com **≥ 250 palavras** depois de tirar o texto padrão do INEMA ("Chamamos então, COLABORADORES…", "Confira as fotos enviadas por…", contatos da equipe). Resultado, classificação e agenda de prova não contam.
- Álbum com **≥ 12 fotos grandes** em `b2:inemaaventura/albuns/<id>/al1/`. As de 533x400 ficam em `al1/`; a raiz do álbum só tem miniaturas de 150 px.
- Matéria que só tem fotos (sem relato) vale só para assinante, e a narração conta apenas o que as fotos mostram (modelo: #6 Guilherme).

## Decisões sobre pessoas

Ficam em `privado/DECISOES.md` (fora do git: dizem quem é assinante).

## Pipeline de um episódio (motor do Telmo v4)

Pasta `~/projetos/output/memorias-aventura-<slug>/`, copiada de um episódio pronto (ex.: Ana ou Guilherme):

1. **Levantamento**: matéria (texto) + álbum `al1/` (fotos). Um subagente Haiku classifica as fotos (categorias + nota) em `classificacao.json`.
2. **roteiro.md**: 9–15 blocos, a partir do relato, sem inventar nada além do texto e das fotos. Anos e números por extenso na fala.
3. **Narração**: `tts.sh` (chatterbox, voz `nei`, 0.6/0.6) → `pos_voz.py` (corte, atempo 1,06, loudnorm, Whisper) → conferir a transcrição. Palavra errada = reescrever a frase.
4. `linha.py` → `mixar_trilha.sh` → `remaster_codex.py` (Codex image_gen pela assinatura, 4 em paralelo, ~12 fotos) → `preparar_rm.py` → `gerar_depth.mjs` → `filme.py`.
5. **Conferir**: frames de cada bloco e duração. Depois enviar ao **inemaytbot** (`enviar_bot.py`). Toda mensagem da série (vídeo pronto, aviso de publicação) vai para o inemaytbot, nunca para o bot v3 (regra do Nei, 11/10/2026).
6. **B2**: `memorias/<slug>/<arquivo>.mp4` (link público `https://f005.backblazeb2.com/file/inemaaventura/memorias/<slug>/<arquivo>.mp4`).
7. **YouTube**: `yt-pubx publicar <mp4> --canal aventuras --dry-run` → conferir texto → `--plano <pasta>/plano.json --sem-thumb`. Depois aplicar a descrição completa (`montar_descricoes.py <ep>` + `yt-pubx atualizar`).
8. **E-mail**: `enviar_email.py <ep>` (texto em `email_<ep>.txt`, com link do YouTube, do B2 e do canal).
9. **Registrar** em `EPISODIOS.md` e `candidatos.json`.

## Descrição no YouTube (padrão de 10/10/2026)

Abertura, narração completa ("A HISTÓRIA"), "SOBRE O REGISTRO", link da matéria nos dois formatos e os outros episódios. Sem link dos álbuns. O link da matéria vai assim:

```
Matéria original com as fotos (para assinantes): aventura.inema.club/mat/idmatXXXXXX.htm

https://aventura.inema.club/mat/idmatXXXXXX.htm
```

Gerador: `montar_descricoes.py` (acrescentar o episódio novo em `EPS`/`REGISTRO`).

## Limites conhecidos (medir antes de prometer)

- **Medido em 10/10/2026:** o canal aceitou 10 uploads em ~24 h (6 republicados + #7 a #10) e recusou o 11º com `uploadLimitExceeded`. Episódio pronto entra em `privado/fila_publicar.txt`; o `fila_publicar.sh` (unit `aventuras-fila`) tenta a cada 3 h e commita o registro.

- **Canal não verificado** (youtube.com/verify pendente): sem capa, links externos sem clique e teto diário de upload baixo. Em 10/10 subiram 6 sem barrar, mas isso é observação, não garantia.
- **Cota da YouTube Data API**: 10.000 unidades/dia por padrão. Um upload custa cerca de 1.600, então 6 uploads quase esgotam o dia. Edições e repetições também gastam. `quotaExceeded` = tentar no dia seguinte (fila). Aumento de cota é pedido pelo Nei no console do projeto aventuras-511207.
- **Codex image_gen**: ~12 remasters × 6 vídeos = 72 imagens por dia. Medir no 1º dia.
- **D1 (banco do aventura.inema.club)**: precisa de acesso para achar matérias, autores e e-mails. Desde 09/10 o wrangler dá erro 7403. Destravar com um token de API da Cloudflare com permissão D1 (ver README).
- **E-mails antigos (2002–2008)**: muitos voltam. Guardar o id do Resend e o retorno em `candidatos.json` e nunca reenviar para endereço que voltou.
- Memória: rodar TTS e render com teto (`systemd-run --user --scope -p MemoryMax=`), um episódio por vez.
