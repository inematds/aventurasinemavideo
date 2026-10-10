# Produzir UM episódio (instrução para o agente que faz o vídeo)

Entrada: `idmat`, `album`, `slug` (ex.: `gilmar-chile-2008`), número do episódio `N`.
Saída: `~/projetos/output/memorias-aventura-<slug>/<slug>_memorias_v1.mp4` conferido, mais `roteiro.md` e `EPISODIO.json`.
Não publica no YouTube, não sobe no B2 e não manda e-mail. Quem faz isso é o orquestrador (`publicar_episodio.py`).

## Passos

1. **Pasta**: `mkdir ~/projetos/output/memorias-aventura-<slug>` e copie o motor de `~/projetos/aventurasinemavideo/motor/`
   (render_v3.py, render_v4.py, tts.sh, pos_voz.py, linha.py, mixar_trilha.sh, remaster_codex.py, preparar_rm.py,
   gerar_depth.mjs, enviar_bot_v3.py). Use como referência o episódio pronto `~/projetos/output/memorias-aventura-guilherme/`
   (filme.py, roteiro.md, linha.json) e `~/projetos/output/memorias-aventura-ana/`. Leia o filme.py de um deles antes de escrever o seu.
2. **Texto**: `~/projetos/aventurasinemavideo/privado/textos/<idmat>.txt`. Se a matéria tiver "Parte 2…", junte as partes.
3. **Fotos**: `~/projetos/inemabk/rclone/rclone copy b2:inemaaventura/albuns/<album>/al1/ fotos-all/` (apague `Album.txt`).
   **Fotos principais = as que aparecem na própria matéria** (`<img>` em https://f005.backblazeb2.com/file/inemaaventura/mat/idmatXXXXXX.htm, versão grande em `al1/`): use TODAS. Outras fotos do álbum ou de álbuns vizinhos do mesmo evento entram só como enfeite (fundo, mosaico, faixa). Regra do Nei, 10/10/2026.
   Classifique as fotos com um subagente `model: haiku` (categorias da história + nota 1–3 + "ruim") → `classificacao.json`.
4. **roteiro.md**: de 9 a 15 blocos (B01 = gancho com o ganho/emoção da história; último bloco = "…continua guardada no acervo do INEMA Aventura").
   Use só fatos do relato e o que as fotos mostram. Não invente nome de lugar nem de pessoa.
   Na fala, anos e números vão por extenso ("dois mil e oito", "dez mil quilômetros"). Frases curtas.
5. **Voz**: `tts.sh` (chatterbox, voz `nei`, 0.6/0.6), depois `pos_voz.py`. Confira a transcrição do Whisper bloco a bloco.
   Se uma palavra saiu errada ou gaguejada, reescreva a frase e gere de novo só aquele bloco. O Whisper devolve número em dígito: use `Wd(b,'12')`.
6. `linha.py` → `mixar_trilha.sh` → `remaster_codex.py` (~12 fotos mais fortes, Codex pela assinatura) → `preparar_rm.py`
   (prefixo do slug) → `gerar_depth.mjs` → escreva o `filme.py` (beats Pilha/Faixa/Mosaico/Prof, letreiros sincronizados por `Wd`) e renderize.
   Rode TTS e render com teto de memória: `systemd-run --user --scope -p MemoryMax=24G …`.
7. **Conferir**: extraia 1 quadro por bloco (ffmpeg) e olhe cada um (letreiro legível, foto certa, nada cortado). Confira a duração (1–3 min) e o áudio.
8. **EPISODIO.json** na pasta (o orquestrador lê isto):
   `{"n": N, "slug", "idmat", "album", "titulo_curto": "<Nome — assunto (ano)>", "assunto": "<título da matéria>", "ano": "<ano da publicação>",
   "video": "<caminho absoluto do mp4>", "duracao_s", "registro": ["<linha: datas e roteiro da viagem>", "<linha: quem escreveu, quando foi publicado>", "<linha: fotos de quem>"],
   "notificar": [<idf das pessoas a avisar, recebido na tarefa>]}`.
9. Mande ao bot: `python3 enviar_bot_v3.py <mp4> "Memórias de Aventura #N — <título>"`.

## Regras

- Comandos que matam processo (`pkill`) sempre numa chamada separada; nunca `pkill -f` com o padrão na mesma linha.
- Nada de API paga. Codex e Claude só pela assinatura.
- Se travar em algo por mais de 3 tentativas, pare e relate o que aconteceu, sem inventar resultado.
