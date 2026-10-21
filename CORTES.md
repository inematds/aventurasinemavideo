# Motor de cortes (shorts) — `cortes.py`

Faz 3 shorts verticais (9:16) de ~15 s de cada episódio publicado no canal Aventuras e põe na fila de imports do **yt-pub-lives26** (canal Aventuras INEMA), que publica **2 por dia, às 11:30 e às 17:30**. Pedido do Nei, 21/10/2026.

**Não usa IA nem gasta token.** Só ffmpeg + Python:
- **Trechos:** um em cada terço do vídeo (pula os primeiros 8% e os últimos 12%), começando e terminando numa pausa da narração (`silencedetect` no `narracao.wav`). Duração entre 12 e 18 s. O sorteio usa o slug como semente, então refazer dá os mesmos trechos.
- **Visual:** vídeo 16:9 no meio, fundo desfocado, "MEMÓRIAS DE AVENTURA #N" + título em cima, "▶ VÍDEO COMPLETO NO CANAL" e @aventurasinema embaixo. Os textos são um PNG feito no PIL (o `drawtext` do ffmpeg 6.1.1 corta o fim de linhas com acento).
- **Texto do YouTube:** título `<título do episódio> (N/3) #shorts`; descrição com o link do vídeo completo (youtu.be), o registro da aventura, o link da matéria e o acervo. Sem capa (short não leva thumb).

## Onde entra no fluxo

`fila_publicar.sh` chama `cortes.py --importar` logo depois de cada episódio publicado com sucesso. Ele processa todo episódio do canal Aventuras no histórico do yt-pubx que ainda não tem corte, então também pega atrasados. Se falhar, só registra um AVISO no log e a fila de episódios continua.

## Uso independente

```bash
python3 cortes.py --so <slug>          # só gera os 3 cortes de um episódio (teste, não publica)
python3 cortes.py                      # gera para todos os publicados ainda sem corte
python3 cortes.py --importar           # gera o que faltar e coloca na fila do lives26
```

- Saída: `/mnt/hd8t/memorias-aventura-cortes/<slug>/` (3 MP4 + `cortes.json` com trechos, títulos, descrições e se já foi importado).
- Refazer um episódio: apagar a pasta dele em `/mnt/hd8t/memorias-aventura-cortes/` e rodar de novo.
- Entrega para o lives26: monta em `~/projetos/yt-pub-lives26/.imports-montando/` e move a pasta inteira para `imports/` no fim, para o `import_worker` (leitura de hora em hora) nunca pegar pasta pela metade.

## Configuração no lives26 (`data/lives.db`, tabela `config`)

`import_auto=true`, `import_pub_horarios=11:30,17:30`, `import_pub_max_por_vez=1`, `import_privacy=public`, `import_gerar_descricao=false` (sem IA), `thumb_mode=none`. Mudar o ritmo = mudar `import_pub_horarios` (o scheduler relê a config a cada volta, sem reiniciar).

**Cota do YouTube:** se estourar, baixar a cota de **episódios** por dia, não a de shorts (Nei, 21/10/2026).
