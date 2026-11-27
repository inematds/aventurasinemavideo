# CONTINUAR — refação das narrações (27/11/2026)

Estado: produtor refazendo 10 episódios (Nanda #245 + 9 da fila) com as regras novas e voz nei5; cada um volta à
`privado/fila_publicar.txt` pronto. A fila está TRAVADA por `privado/SEGURAR_FILA` (nada publica).
Nanda nova (v2) e antiga foram ao v3 (msg 1205/1206) para o Nei comparar.

Ordens do Nei: "refaz o nanda e todos da fila refaz"; "a regra mostre so o q as fotos dizem nao, se tem texto use a historia".

Falta, nesta ordem (só com OK do Nei):
1. Nei aprova a Nanda nova. Se reprovar: `systemctl --user stop aventuras-produz` e ajustar o PRODUZIR.md.
2. Nei refaz o login do yt-pubx do Aventuras (`yt-pubx auth aventuras`), senão a descrição completa falha.
3. Nanda: tirar a pasta dela da fila antes de soltar (o publicar_episodio acharia o episódio já registrado);
   publicar a v2 como novo vídeo, apagar o antigo FuRc_8T1PPQ (OK específico do Nei) e trocar o link em
   `privado/episodios.json` e `EPISODIOS.md`.
4. Conferir cada refeito no log (`privado/produz.log`); reprovado no portão vira `erro_producao` e precisa ser refeito à mão.
5. Soltar a fila: `rm privado/SEGURAR_FILA` (o serviço aventuras-fila já está ativo ou o produtor o liga).
Backups: `privado/bak-20261127-refazer/` (candidatos, fila, estado_pub, episodios). Versões antigas: `versao-antiga-20261127/` em cada pasta.
