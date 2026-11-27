# Produzir UM episódio (instrução para o agente que faz o vídeo)

Entrada: `idmat`, `album`, `slug` (ex.: `gilmar-chile-2008`), número do episódio `N`.
Saída: `~/projetos/output/memorias-aventura-<slug>/<slug>_memorias_v1.mp4` conferido, mais `roteiro.md` e `EPISODIO.json`.
Não publica no YouTube, não sobe no B2 e não manda e-mail. Quem faz isso é o orquestrador (`publicar_episodio.py`).

## Passos

1. **Pasta**: `mkdir ~/projetos/output/memorias-aventura-<slug>` e copie o motor de `~/projetos/aventurasinemavideo/motor/`
   (render_v3.py, render_v4.py, tts.sh, pos_voz.py, linha.py, mixar_trilha.sh, remaster_codex.py, preparar_rm.py,
   gerar_depth.mjs, enviar_bot.py). Use como referência o episódio pronto `~/projetos/output/memorias-aventura-guilherme/`
   (filme.py, roteiro.md, linha.json) e `~/projetos/output/memorias-aventura-ana/`. Leia o filme.py de um deles antes de escrever o seu.
2. **Texto**: `~/projetos/aventurasinemavideo/privado/textos/<idmat>.txt`. Se a matéria tiver "Parte 2…", junte as partes.
3. **Fotos**: `~/projetos/inemabk/rclone/rclone copy b2:inemaaventura/albuns/<album>/al1/ fotos-all/` (apague `Album.txt`).
   **Fotos principais = as que aparecem na própria matéria** (`<img>` em https://f005.backblazeb2.com/file/inemaaventura/mat/idmatXXXXXX.htm, versão grande em `al1/`): use TODAS. Outras fotos do álbum ou de álbuns vizinhos do mesmo evento entram só como enfeite (fundo, mosaico, faixa). Regra do Nei, 10/10/2026.
   Classifique as fotos pela etapa `classificacao` de `auto/ia.yaml` (categorias da história + nota 1–3 + "ruim") → `classificacao.json`.
   Use o executor do projeto (caminho absoluto): `python3 ~/projetos/aventurasinemavideo/auto/ia_motor.py executar classificacao --pasta "$PWD" --imagem /caminho/foto.jpg --saida classificacao.json`, recebendo o pedido pela entrada padrão; repita `--imagem` para lotes pequenos e consolide o JSON. Informe os nomes dos arquivos no pedido. Não fixe modelo nem use um subagente Haiku por fora da configuração. A remasterização continua Codex assinatura.
4. **roteiro.md**: de 9 a 15 blocos (B01 = apresenta a aventura e promete o que vem, ver abaixo; último bloco = "…continua guardada no acervo do INEMA Aventura").
   **Com relato, a narração conta a HISTÓRIA do texto e as fotos complementam (regra do Nei, 27/11/2026).** A voz não
   descreve a foto ("a vista compensou o esforço" sobre a foto da vista): conta o que aconteceu, o que a pessoa sentiu,
   o antes e o depois. Fato sem foto própria também é narrado, e na tela entram fotos reais da mesma matéria (galeria,
   faixa, fundo desfocado) sem afirmar que mostram aquele instante. Nunca tela só com texto em fundo escuro; o gancho
   B01 sempre com foto. Só a matéria SEM relato (só fotos) narra o que as fotos mostram.
   Não invente nome de lugar nem de pessoa nem fato fora do relato.
   **B01 apresenta a aventura (Nei, 27/11/2026: "todo início tem que falar da aventura").** A primeira frase diz QUAL é
   a aventura (o nome da prova/viagem/evento como está na matéria), quem, quando e onde, já com a promessa do que vem.
   Ex.: "Em abril de dois mil e quatro, Nanda Brenner encarou dez horas da Corrida Canela Aventura, e a prova guardava
   um penhasco, um rapel e uma chegada decidida em cinco segundos." Nunca começar no meio da ação sem dizer a aventura.
   Letreiro do B01 = nome da aventura + ano.
   **Meio:** decisões, sustos, sensações e frases da própria pessoa ("ela contou que…"), não inventário de trechos.
   Virada, desfecho e fecho fixo. Duração pelo relato: longo até 3 min; curto ~1,5 min, sem encher.
   **Palavra do assunto na tela (Nei, 27/11/2026: "uma palavra sobre o que é, não precisa legenda").** Cada momento
   ganha um letreiro de 2 a 4 palavras dizendo DO QUE se fala ("NATAÇÃO NO LAGO", "SERROTE NA PRAÇA", "RAPEL NA
   CASCATA", "PNEU FURADO"), entrando quando a voz chega nele (`Wd`). Não é legenda nem cópia da frase. Dado (PC 7,
   903 m, 10h15) só como linha pequena de apoio.
   **A foto acompanha a fala (Nei, 27/11/2026: "buscar as fotos apropriadas para a fala").** Escolha as fotos de cada
   bloco pela `classificacao.json` (categoria + descrição) do assunto falado, trocando de foto quando a fala muda de
   assunto. Sem foto daquele momento: galeria do evento passando (Faixa/Mosaico), nunca tela vazia.
   **Formato obrigatório do roteiro.md:** logo abaixo de cada linha `Bxx — <fala>`, uma linha
   `  TELA: <assunto em 2–4 palavras>[ / <outro assunto quando a fala muda>] · FOTOS: <categoria(s) da classificacao.json, separadas por vírgula> | galeria`.
   O `filme.py` usa exatamente essas categorias. O portão (`verifica_ep.py`) reprova bloco sem TELA/FOTOS, categoria
   inexistente e B01 sem o nome da aventura.
   Na fala, anos e números vão por extenso ("dois mil e oito", "dez mil quilômetros"). Frases curtas.
5. **Voz**: `tts.sh` (chatterbox, voz `nei5`, 0.6/0.6; Nei escolheu em 27/11/2026), depois `pos_voz.py`. Confira a transcrição do Whisper bloco a bloco.
   Se uma palavra saiu errada ou gaguejada, reescreva a frase e gere de novo só aquele bloco. O Whisper devolve número em dígito: use `Wd(b,'12')`.
6. `linha.py` → `mixar_trilha.sh` → `remaster_codex.py` (~12 fotos mais fortes, Codex pela assinatura) → `preparar_rm.py`
   (prefixo do slug) → `gerar_depth.mjs` → escreva o `filme.py` (beats Pilha/Faixa/Mosaico/Prof, letreiros sincronizados por `Wd`) e renderize.
   Rode TTS e render com teto de memória: `systemd-run --user --scope -p MemoryMax=24G …`.
7. **Conferir**: extraia 1 quadro por bloco (ffmpeg) e olhe cada um (letreiro legível, foto certa, nada cortado). Confira a duração (1–3 min) e o áudio.
8. **EPISODIO.json** na pasta (o orquestrador lê isto):
   `{"n": N, "slug", "idmat", "album", "titulo_curto": "<Nome — assunto (ano)>", "assunto": "<título da matéria>", "ano": "<ano da publicação>",
   "video": "<caminho absoluto do mp4>", "duracao_s", "registro": ["<linha: datas e roteiro da viagem>", "<linha: quem escreveu, quando foi publicado>", "<linha: fotos de quem>"],
   "notificar": [<idf das pessoas a avisar, recebido na tarefa>]}`.
9. Mande ao **inemaytbot** (nunca ao bot v3; regra do Nei, 11/10/2026): `python3 enviar_bot.py <mp4> "Memórias de Aventura #N — <título>"`.

## Regras

- Comandos que matam processo (`pkill`) sempre numa chamada separada; nunca `pkill -f` com o padrão na mesma linha.
- Nada de API paga. Codex e Claude só pela assinatura.
- Se travar em algo por mais de 3 tentativas, pare e relate o que aconteceu, sem inventar resultado.
