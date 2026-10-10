# FALHAS — aventurasinemavideo

| data | o que quebrou | menor correção | prompt \| infra |
|---|---|---|---|
| 10/10/2026 | #12: voz `nei` estropiou nome espanhol ("El Tatio" 3× → Altatiel/Eltatil; "San Antonio de los Cobres" → Luscovitz) | tirar o nome da fala e deixar no letreiro | prompt |
| 10/10/2026 | #7: render travou 20 min sem erro (âncora `Wd` inexistente → SystemExit no worker do Pool) | validar `filme.blocos()` num processo só antes do render | prompt |
| 10/10/2026 | #7: contador `conta=(2500, 4800, …)` mostrou "27.300 METROS" (precedência na fórmula do render_v4) | parênteses na fórmula do motor (corrigido em motor/render_v4.py) | infra |
