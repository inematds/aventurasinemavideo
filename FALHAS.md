# FALHAS — aventurasinemavideo

| data | o que quebrou | menor correção | prompt \| infra |
|---|---|---|---|
| 10/10/2026 | #7: render travou 20 min sem erro (âncora `Wd` inexistente → SystemExit no worker do Pool) | validar `filme.blocos()` num processo só antes do render | prompt |
| 10/10/2026 | #7: contador `conta=(2500, 4800, …)` mostrou "27.300 METROS" (precedência na fórmula do render_v4) | usar v0 = 0 (ou corrigir `round((v0 + (v1-v0)*e)/10)*10`) | infra |
