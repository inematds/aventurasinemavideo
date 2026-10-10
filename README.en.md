# aventurasinemavideo

[![Adventure Memories](guia/assets/banner-en.jpg)](https://inematds.github.io/aventurasinemavideo/guia/en/)

**🇧🇷 [Português](README.md) · 🇺🇸 [English](README.en.md) · 🇪🇸 [Español](README.es.md)**

## What it is

**aventurasinemavideo** is the project behind the **Adventure Memories** series ("Memórias de Aventura"). It takes real articles from the INEMA Aventura archive (aventura.inema.club, 2001 to 2012), with the stories and photos the adventurers themselves sent in, and turns each one into a narrated film of one to three minutes. It is for the people who lived those stories and for anyone who loves adventure: the films are free on the [Aventuras INEMA](https://www.youtube.com/@aventurasinema) YouTube channel. To watch, just open the channel; this repository holds the rules and the engine that builds the films.

## 📖 User guide

Full guide (landing + step by step): **https://inematds.github.io/aventurasinemavideo/guia/en/**

## How it works

Each episode starts from a real article in the archive: the story becomes a script, the album photos are
restored and set in motion (2.5D depth, stacks, strips and mosaics), and the narration uses Nei's voice.
The author of the story receives the video by e-mail.

- **Production rules** (6 videos a day, article criteria, publishing and notice): [PLANO.md](PLANO.md) (in Portuguese)
- **Episodes already made**: [EPISODIOS.md](EPISODIOS.md) (in Portuguese)
- **Film engine**: [motor/](motor/), with the full example of episode 6 (`filme_exemplo_guilherme.py`, `roteiro_exemplo_guilherme.md`)

## Pieces

| File | What it does |
|---|---|
| `motor/tts.sh` | narration per block (chatterbox, `nei` voice) |
| `motor/pos_voz.py` | trimming, pacing, volume and word-by-word transcription (Whisper) |
| `motor/linha.py`, `motor/mixar_trilha.sh` | timeline and soundtrack (voice + music) |
| `motor/remaster_codex.py` | restores the old photos (Codex image_gen, via subscription) |
| `motor/gerar_depth.mjs` | depth map for the 2.5D motion |
| `motor/render_v3.py`, `motor/render_v4.py` | frame composition (stack, strip, mosaic, depth, titles) |
| `publicar_fila.py` | YouTube publishing queue (yt-pubx), retrying when the daily limit is hit |
| `montar_descricoes.py` | full YouTube description (narration, record, article link) |
| `enviar_email.py` | e-mail notice to the author (Resend) |

Publishing to YouTube uses [yt-pubx](https://github.com/inematds/yt-pubx) (`--canal aventuras`).

## Personal data

E-mails, subscriber list, queue state and e-mail texts stay out of git (`privado/`, `.gitignore`).
