# CLAUDE.md — aventurasinemavideo

Projeto que produz e publica a série **Memórias de Aventura** (acervo INEMA Aventura → vídeo narrado → canal
Aventuras INEMA). Antes de qualquer episódio, ler `PLANO.md` (regras do Nei, pipeline, limites) e `EPISODIOS.md`.

- Conta GitHub: **inematds** (autor `inematds <inematds@gmail.com>`).
- Episódios (fotos, voz, render) ficam em `~/projetos/output/memorias-aventura-<slug>/`; aqui só a gestão e o motor.
  `~/projetos/output/memorias-aventura-fila` é um link para esta pasta (caminhos antigos dos planos).
- Publicar = `yt-pubx --canal aventuras` (nunca lives*). E-mail = Resend (autorizado para assinantes e não assinantes).
- Nunca commitar `privado/`, `subs.json`, `estado.json`, `fila.json`, `email_*.txt` (exceto o modelo).
- Ao terminar um episódio: atualizar `EPISODIOS.md`, `privado/candidatos.json`, `montar_descricoes.py` e commitar.

- **Runtime contínuo (12/10/2026, pedido do Nei: "um runtime rodando sem parar"):** `aventuras-produz.service`
  (`produz_loop.sh`: `escolhe.py` reserva a matéria → `claude -p` segue o PRODUZIR.md → `verifica_ep.py` → fila) e
  `aventuras-fila.service` (`fila_publicar.sh` + `espera_slot.py`: 8 por dia, 6 às 20 h). Os dois são units de arquivo
  em `~/.config/systemd/user`, `Restart=always`, ligados no boot. Produz só enquanto a fila tiver < 16; episódio novo
  mora em `/mnt/hd8t/memorias-aventura/` com link em `output/`. Log: `privado/produz.log`, `privado/tarefas/<slug>.log`.

## Self-learning

When I correct you, or you catch yourself making a mistake: before continuing, add the lesson as a one-line rule under ## Lessons, so it never happens again.

## Lessons
- Erro em qualquer etapa automática (fila, render, publicação) NUNCA para calado: pede ajuda no **bot v3** (`~/projetos/wifi/scripts/avisa-v3.sh`) de forma clara (episódio, erro, o que falta) e insiste até destravar; conteúdo da série continua no inemaytbot. Em 11/10 a fila ficou 18 h parada só com uma linha no log. (12/10/2026)
- Mensagens da série (vídeo pronto, aviso de publicação) vão para o **inemaytbot** (`motor/enviar_bot.py`, token TELEGRAM_NOTIFY_BOT_TOKEN em yt-pub-livesx-master/config/.env), NUNCA para o bot v3. Regra do Nei em 11/10/2026: os episódios 15 a 20 tinham ido ao v3. (11/10/2026)

- Voz `nei` lê ano em algarismo errado: na fala, ano e número sempre por extenso; conferir pelo Whisper (que devolve dígitos: `Wd(b,'12')`, não 'doze'). (10/10/2026)
- Fotos do acervo: as grandes (533x400) estão em `albuns/<id>/al1/`; a raiz do álbum só tem miniaturas de 150 px; apagar o `Album.txt` de `al1/`. (10/10/2026)
- Whisper parte milhar em dois tokens ("4", ".800"): âncora é `Wd(b,'4')`, não '4800'. Antes de renderizar, rodar `python3 -c "import filme;filme.blocos()"`: âncora errada dá SystemExit dentro do Pool e o render trava sem erro (#7, 10/10/2026).
- `conta=(v0, v1, …)` do render_v4 contava errado com v0 > 0 ("27.300 METROS"); fórmula corrigida no motor em 10/10. (10/10/2026)
- Âncora `Wd` tem que ser a palavra como o Whisper escreveu, não a do roteiro: "camioneta" virou "caminhoneta", "CTG" virou "setegui"/"etag"; conferir em palavras.json antes de escolher a âncora (#8, 10/10/2026).
- Letreiro de centro cobria a foto: desde 10/10 o padrão (`pos=c`) fica no topo; e-mail vai a TODAS as pessoas da matéria (menos o Nei). (10/10/2026)
- Voz `nei` erra nomes: "Eliandra", "Ilha das Couves", "Blue" (blu-e), "El Tatio", "San Antonio de los Cobres": deixar só no letreiro. (10/10/2026)
- Canal novo do YouTube não verificado: sem capa, sem link externo clicável e teto diário baixo; publicar com `--sem-thumb`. (10/10/2026)
- Remaster Codex inventa: trocou "BOULDER" por "BOLICHE" num adesivo e virou agarras sujas de magnésio em pelúcia (duas vezes). Olhar TODO remaster em folha antes do render; texto/objeto mudado = refazer uma vez, senão usar o original como cópia em papel (#10, 10/10/2026).
- O álbum dado pode ser só UM capítulo do evento: ler `Album.txt` (IdEv) e os álbuns vizinhos antes de classificar. No #9 o 0039336 era "11Ushuaia" (zero Antártida); as fotos da viagem estavam em 0039337–0039350. Fotos extras entram em fotos-all com prefixo que ordena DEPOIS (`zz_`), senão os índices mudam. (#9, 10/10/2026)
- As <img> da página B2 da matéria podem incluir a faixa "edições anteriores" (fotos de outras matérias/anos): no #16 (84780) as 7 fotos eram do 4º ao 9º Moto Lagoa; o letreiro sobre cada uma diz a edição e a narração não atribui a foto ao ano da matéria. (11/10/2026)
