# CLAUDE.md — aventurasinemavideo

Projeto que produz e publica a série **Memórias de Aventura** (acervo INEMA Aventura → vídeo narrado → canal
Aventuras INEMA). Antes de qualquer episódio, ler `PLANO.md` (regras do Nei, pipeline, limites) e `EPISODIOS.md`.

- Conta GitHub: **inematds** (autor `inematds <inematds@gmail.com>`).
- Episódios (fotos, voz, render) ficam em `~/projetos/output/memorias-aventura-<slug>/`; aqui só a gestão e o motor.
  `~/projetos/output/memorias-aventura-fila` é um link para esta pasta (caminhos antigos dos planos).
- Publicar = `yt-pubx --canal aventuras` (nunca lives*). E-mail = Resend (autorizado para assinantes e não assinantes).
- Nunca commitar `privado/`, `subs.json`, `estado.json`, `fila.json`, `email_*.txt` (exceto o modelo).
- Ao terminar um episódio: atualizar `EPISODIOS.md`, `privado/candidatos.json`, `montar_descricoes.py` e commitar.

## Self-learning

When I correct you, or you catch yourself making a mistake: before continuing, add the lesson as a one-line rule under ## Lessons, so it never happens again.

## Lessons

- Voz `nei` lê ano em algarismo errado: na fala, ano e número sempre por extenso; conferir pelo Whisper (que devolve dígitos: `Wd(b,'12')`, não 'doze'). (10/10/2026)
- Fotos do acervo: as grandes (533x400) estão em `albuns/<id>/al1/`; a raiz do álbum só tem miniaturas de 150 px; apagar o `Album.txt` de `al1/`. (10/10/2026)
- Whisper parte milhar em dois tokens ("4", ".800"): âncora é `Wd(b,'4')`, não '4800'. Antes de renderizar, rodar `python3 -c "import filme;filme.blocos()"`: âncora errada dá SystemExit dentro do Pool e o render trava sem erro (#7, 10/10/2026).
- `conta=(v0, v1, …)` do render_v4 contava errado com v0 > 0 ("27.300 METROS"); fórmula corrigida no motor em 10/10. (10/10/2026)
- Canal novo do YouTube não verificado: sem capa, sem link externo clicável e teto diário baixo; publicar com `--sem-thumb`. (10/10/2026)
