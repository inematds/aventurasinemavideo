# aventurasinemavideo

[![Memorias de Aventura](guia/assets/banner-es.jpg)](https://inematds.github.io/aventurasinemavideo/guia/es/)

**🇧🇷 [Português](README.md) · 🇺🇸 [English](README.en.md) · 🇪🇸 [Español](README.es.md)**

## Qué es

**aventurasinemavideo** es el proyecto que produce la serie **Memorias de Aventura** ("Memórias de Aventura"). Toma artículos reales del archivo de INEMA Aventura (aventura.inema.club, de 2001 a 2012), con el relato y las fotos que enviaron los propios aventureros, y convierte cada uno en una película narrada de uno a tres minutos. Sirve para quienes vivieron esas historias y para quien ama la aventura: las películas se publican gratis en el canal [Aventuras INEMA](https://www.youtube.com/@aventurasinema) de YouTube. Para verlas, basta abrir el canal; el repositorio guarda las reglas y el motor que arma las películas.

## 📖 Guía de uso

Guía completa (landing + paso a paso): **https://inematds.github.io/aventurasinemavideo/guia/es/**

## Cómo funciona

Cada episodio parte de un artículo real del archivo: el relato se convierte en guion, las fotos del álbum se
restauran y ganan movimiento (profundidad 2.5D, pilas, franjas y mosaicos), y la narración usa la voz de Nei.
El autor de la historia recibe el video por correo electrónico.

- **Reglas de producción** (6 videos por día, criterio de artículo, publicación y aviso): [PLANO.md](PLANO.md) (en portugués)
- **Episodios ya hechos**: [EPISODIOS.md](EPISODIOS.md) (en portugués)
- **Motor de la película**: [motor/](motor/), con el ejemplo completo del episodio 6 (`filme_exemplo_guilherme.py`, `roteiro_exemplo_guilherme.md`)

## Piezas

| Archivo | Qué hace |
|---|---|
| `motor/tts.sh` | narración por bloque (chatterbox, voz `nei`) |
| `motor/pos_voz.py` | corte, ritmo, volumen y transcripción palabra por palabra (Whisper) |
| `motor/linha.py`, `motor/mixar_trilha.sh` | línea de tiempo y banda sonora (voz + música) |
| `motor/remaster_codex.py` | restaura las fotos antiguas (Codex image_gen, por suscripción) |
| `motor/gerar_depth.mjs` | mapa de profundidad para el movimiento 2.5D |
| `motor/render_v3.py`, `motor/render_v4.py` | composición de los cuadros (pila, franja, mosaico, profundidad, rótulos) |
| `publicar_fila.py` | cola de publicación en YouTube (yt-pubx), con reintento al llegar al límite diario |
| `montar_descricoes.py` | descripción completa en YouTube (narración, registro, enlace del artículo) |
| `enviar_email.py` | aviso por correo al autor (Resend) |

La publicación en YouTube usa [yt-pubx](https://github.com/inematds/yt-pubx) (`--canal aventuras`).

## Datos personales

Correos, lista de suscriptores, estado de la cola y textos de los correos quedan fuera de git (`privado/`, `.gitignore`).
