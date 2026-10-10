# aventurasinemavideo

Transforma os relatos e as fotos do acervo **INEMA Aventura** (aventura.inema.club, 2001–2012) em
filmes narrados da série **Memórias de Aventura**. Os filmes são publicados no canal
[Aventuras INEMA](https://www.youtube.com/@aventurasinema).

Cada episódio parte de uma matéria real do acervo: o relato vira roteiro, as fotos do álbum são
restauradas e ganham movimento (profundidade 2.5D, pilhas, faixas e mosaicos), e a narração usa a
voz do Nei. O autor da história recebe o vídeo por e-mail.

- **Regras de produção** (6 vídeos por dia, critério de matéria, publicação e aviso): [PLANO.md](PLANO.md)
- **Episódios já feitos**: [EPISODIOS.md](EPISODIOS.md)
- **Motor do filme**: [motor/](motor/), com o exemplo completo do episódio 6 (`filme_exemplo_guilherme.py`, `roteiro_exemplo_guilherme.md`)

## Peças

| Arquivo | O que faz |
|---|---|
| `motor/tts.sh` | narração por bloco (chatterbox, voz `nei`) |
| `motor/pos_voz.py` | corte, ritmo, volume e transcrição palavra a palavra (Whisper) |
| `motor/linha.py`, `motor/mixar_trilha.sh` | linha do tempo e trilha (voz + música) |
| `motor/remaster_codex.py` | restaura as fotos antigas (Codex image_gen, pela assinatura) |
| `motor/gerar_depth.mjs` | mapa de profundidade para o movimento 2.5D |
| `motor/render_v3.py`, `motor/render_v4.py` | composição dos quadros (pilha, faixa, mosaico, profundidade, letreiros) |
| `publicar_fila.py` | fila de publicação no YouTube (yt-pubx), com nova tentativa no limite diário |
| `montar_descricoes.py` | descrição completa no YouTube (narração, registro, link da matéria) |
| `enviar_email.py` | aviso por e-mail ao autor (Resend) |

Publicação no YouTube pelo [yt-pubx](https://github.com/inematds/yt-pubx) (`--canal aventuras`).
Para autorizar um canal novo, veja o [passo a passo sem termos técnicos](https://github.com/inematds/yt-pubx/blob/main/docs/autorizar-canal.md).

## Dados pessoais

E-mails, lista de assinantes, estado da fila e textos dos e-mails ficam fora do git (`privado/`, `.gitignore`).
