# FALHAS — aventurasinemavideo

| data | o que quebrou | menor correção | prompt \| infra |
|---|---|---|---|
| 10/10/2026 | #13: última palavra do bloco ("jamanta") sumiu do WAV final: Whisper não a transcreveu no bruto e o `pos_voz` corta na última palavra transcrita | conferir a última palavra de cada bloco na transcrição; faltou = gerar o bloco de novo | infra |
| 10/10/2026 | #13 (evitado): `conta=` com v1 ≥ 100 arredonda a dezenas, 273 vira "270 KM" | número que não termina em 0 vai como texto fixo, sem `conta` | infra |
| 10/10/2026 | #13: mapa regional (~1,5°) com `MS` alto engrossa bordas e letreiros do `mapa_base` e o litoral do paises.geojson fica grosseiro | `mapa_base` próprio no filme.py com terra = uf.json e mar claro (rótulo escuro legível) | infra |
| 10/10/2026 | #12: voz `nei` estropiou nome espanhol ("El Tatio" 3× → Altatiel/Eltatil; "San Antonio de los Cobres" → Luscovitz) | tirar o nome da fala e deixar no letreiro | prompt |
| 10/10/2026 | #7: render travou 20 min sem erro (âncora `Wd` inexistente → SystemExit no worker do Pool) | validar `filme.blocos()` num processo só antes do render | prompt |
| 10/10/2026 | #7: contador `conta=(2500, 4800, …)` mostrou "27.300 METROS" (precedência na fórmula do render_v4) | parênteses na fórmula do motor (corrigido em motor/render_v4.py) | infra |
