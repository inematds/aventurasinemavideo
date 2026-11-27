| 26/11/2026 | mesma matéria virou 5 episódios no canal (Alexandre, Trilha Inca, Nanda; Pedro 2x) desde 19/11: publicar_episodio.py gravava a cópia do candidatos.json lida horas antes (espera do x3) e devolvia a "pendente" a matéria recém-produzida | gravar sob a trava do produtor relendo e mudando só o idmat; escolhe.py pula idmat que já tem episódio; publicador recusa matéria já publicada (saída 65, sai da fila) | infra |
| 25/11/2026 | #258 foto com placa de Morro do Ferro surgiu na abertura do trecho de Bonfim | manter a placa no B05 e trocar apenas a foto do B04; recompor e conferir o quadro do MP4 | prompt |
| 25/11/2026 | #258 narração imprecisa em Paraopeba e São Tiago, pausa mudou sentido e B07 repetiu frase | refazer B03/B05/B06/B07 e limpar som isolado de B04 entre 5,285 e 5,870 s; large-v3 confirmou os 11 blocos | prompt e infra |
| 25/11/2026 | #256 a voz trocou “barco” e “Caio”, ligou datas à frase seguinte e deixou ruído entre frases | reescrever B01/B04/B07/B09 e silenciar só o interior de quatro pausas; large-v3 confirmou as frases e a posição das datas | prompt e infra |
| 24/11/2026 | #254 restauração retexturizou areia das dunas e detalhes sob a marca | manter originais em papel e depth do original 011, sem trocar os registros documentais | prompt |
| 24/11/2026 | #252 voz trocou “passou pelo litoral” por “passou pênalti” e nomes ficaram imprecisos | reescrever só cinco blocos; large-v3 confirmou litoral, lugares e fecho | prompt |
| 24/11/2026 | #252 restauração 038 trouxe barras pretas laterais | conservar original, com profundidade do original | prompt |
| 2026-11-23 | #245 TTS trocou palavras no B04/B08 e gerou ruído em pausas do B05/B07 | reescrever dois blocos e silenciar só interiores das duas pausas, mantendo tempos; retranscrição integral e diagnóstico limpos | infra |
| 2026-11-23 | #245 remaster ampliou bordas e detalhes incertos em 399/400/413 | usar originais e depth do original 400 | prompt |
| 2026-11-23 | #246: som isolado não transcrito na pausa do B11 | silenciar 7,78–8,30 s com fades, preservar duração e retranscrever | infra |
| 2026-11-23 | #246: prévia quebrou com largura float em Pilha.big | arredondar largura proporcional antes de criar o cartão | infra |
| 2026-11-23 | #246: TTS colou adjunto do B09 e capturou fecho com concordância incorreta | frases independentes e regenerar apenas B09/B12 | prompt |
| 22/11/2026 | #242 TTS alterou Oliva/caiaque/embarcação, omitiu frase do B11 e trouxe ruído no B03 | reescrever e regenerar somente B02/B03/B04/B10/B11; transcrição e energia das pausas conferidas | infra |
| 22/11/2026 | #242 restaurações ampliaram bordas e reconstruíram água, vegetação, rostos e inscrições | manter fotos originais em papel e profundidade calculada no original 000 | prompt |
| 2026-11-22 | #244 envio ao inemaytbot preso em conexão IPv6 | Resolver somente IPv4 na cópia do episódio; vídeo e roteiro confirmados pelo bot | infra |
| 2026-11-22 | #244 prévia mostrou vestígio de marca e evento B11 negativo | Corte inferior de 64 px; antecipar evento e validar duração positiva | prompt |
| 2026-11-22 | #244 TTS com ruído entre frases no B08 e frase ambígua de vizinhança no B11 | Reescrever e gerar somente B08/B11; conferir transcrição e pausas | prompt |
| 21/11/2026 | #240 voz errou nomes/camping e fez ruído em pausas | reescrever cinco blocos e limpar só interior de duas pausas; retranscrição íntegra | infra |
| 21/11/2026 | #240 folha de prévias parou por import math ausente | importar math e remontar só a folha dos quadros já salvos | prompt |
| 21/11/2026 | #240 doze restaurações reconstruíram detalhes sem evidência | preservar originais e usar depth do original 017 | prompt |
| 21/11/2026 | #240 remaster recusou modelos porque systemd usou Codex 0.116 de /usr/bin | caminho absoluto ~/.npm-global/bin/codex na cópia do episódio | infra |
| 2026-11-20 | #239 montagem final sob scope terminou com SIGTERM (143), deixando MP4 sem moov | reutilizar segmentos íntegros e executar só montagem em unit transitória independente, MemoryMax=24G/RuntimeMaxSec=900; saída de 46,07 MB concluída | infra |
| 2026-11-20 | #239 remaster 151/153 redesenhou cristais e vegetação; pessoas pequenas das principais ficaram incertas | usar as seis principais como originais em papel; aproveitar apenas 130/140 restauradas como fundos desfocados | infra |
| 2026-11-20 | #239 voz imprecisa em Aparados, pausa ruidosa no B02 e frase colada no B05; novas pausas no B04/B08 | nome do evento no letreiro; regenerar só B02/B04/B05; limpar 6,40–7,72 s do B04 e 7,98–8,68 s do B08 com fades; nove blocos retranscritos sem ruído detectado | infra |
| 2026-11-20 | #239 classificação cobriu 665 índices mas trocou um dígito no timestamp do arquivo 267 | consolidar nome canônico por índice visível usando indice.json; validar cobertura e unicidade | infra |
| 2026-11-20 | #234 prévia nomeou Tres Piedras sobre foto de ruínas não identificadas | usar Faixa ilustrativa e letreiro O plano mudou para o acampamento sem foto própria | prompt |
| 2026-11-20 | #234 nova voz B06 manteve ruído de −29,5 dB na pausa após pedra | silenciar só 6,90–8,35 s com fades de 30 ms, duração preservada e nova transcrição íntegra (pausa −79 dB) | infra |
| 2026-11-20 | #234 voz perdeu o r de passaportes e tornou Alan impreciso; ruído na pausa do B07 | regenerar B06/B09/B10 com documento original e o filho; silenciar 6,58–7,78 s no B07 com fades, transcrição conferida | infra |
| 2026-11-20 | #234 remaster 005 redesenhou vegetação e enquadramento; 004 estendeu terreno incerto | reprovar essas versões e manter originais em papel na galeria | infra |
| 2026-11-19 | #231 voz B02 juntou a formatura à frase seguinte e B06 teve som isolado entre frases | sujeito explícito no B02 e reescrita concisa do B06; regenerar só esses blocos e retranscrever | infra |
| 2026-11-19 | #231 remaster 003 alterou detalhes do rosto da escaladora | reprovar a restauração e conservar original em papel | infra |
| 2026-11-19 | #229 MP4 truncou em 82 s porque trilha.wav foi sobrescrita durante a montagem com shortest | aguardar mix concluído, remontar segmentos íntegros e comparar duração do MP4 com linha.json | prompt |
| 2026-11-19 | #229 B09 manteve ruído de −32 dB na pausa amizade/havia | silenciar só 12,55–13,00 s com fades de 25 ms e duração preservada; transcrição confirmou frase íntegra | infra |
| 2026-11-19 | #229 prévia deixou cópias em papel pequenas porque thumbnail não amplia | redimensionar pela razão mínima da caixa, preservando a proporção | prompt |
| 2026-11-19 | #229 B09 repetiu do caminho; remasters com pessoas pequenas ficaram incertos | iniciar B09 com Alexandre fez cursos e regenerar só ele; originais em papel para restaurações reprovadas | infra |
| 2026-11-19 | #229 voz B08: montanhismo saiu montainhismo | trocar apenas a frase por As montanhas eram sua grande paixão; regenerar B08 | infra |
| 2026-11-18 | #227 B04 regenerado manteve ruído na pausa entre palavras corretas | Silenciar somente 7,07–8,40 s entre fins/inícios confirmados, com fades e duração preservada | infra |
| 2026-11-18 | Auditoria #225 mediu ruído entre palavras em B07/B10, apesar de transcrição correta | silenciar somente pausas comprovadas, com fades de 25 ms e duração preservada; retranscrição manteve todo o texto | infra |
| 2026-11-18 | #227 corte do balbucio B04 removeu início de “Depois” (Whisper passou a “pois”) | Regenerar só B04 com sujeito explícito e conferir novamente | infra |
| 2026-11-18 | #227 balbucio não transcrito no B04/B08 | Corte só dos intervalos confirmados por word_timestamps, fades de 25 ms e nova transcrição | infra |
| 2026-11-18 | #227 classificação por lotes interrompida (SIGTERM 143) antes da consolidação | Retomar só lotes ausentes em scope systemd e validar cobertura dos 253 nomes | infra |
| 2026-11-18 | Prévia #225 chamou fundo() como factory e deu TypeError | usar diretamente a imagem retornada por fundo(...).copy() | prompt |
| 2026-11-18 | Pós #225 interrompida por SIGTERM sem palavras.json; retomada systemd perdeu perfil Codex do remaster | checkpoint por bloco na cópia local da pós e CODEX_HOME explícito nas units de retomada | infra |
# FALHAS — aventurasinemavideo
| 2026-11-17 | #223 envio ao inemaytbot caiu com SSLEOFError | repetir uma vez o mesmo envio; sendVideo True confirmado | infra |
| 2026-11-17 | #223 TTS deformou Djalma e Roberval, omitiu frase e confundiu Fórmula Uno | Reescrever somente cinco blocos; nomes completos e categoria nos letreiros; conferir o Whisper | prompt |
| 2026-11-17 | #223 prévia iniciada enquanto B12 ainda tinha transcrição anterior | Aguardar pos_voz terminar e só então refazer linha, mix e prévia | prompt |
| 2026-11-17 | #223 remaster 023 reconstruiu trabalhadores junto aos trucks | Rejeitar a restauração e preservar originais; usar só vista geral distante | prompt |
| 2026-11-17 | MP4 #222 atingiu 50,27 MB e excedeu o teto de 50 MB do bot | copiar o vídeo sem reencodar e reduzir só AAC para 112 kbps; final 49,49 MB e validador aprovado | infra |
| 2026-11-17 | Voz #222 registrou Alfredo Wagner como Alfred Wagner no B10 | deixar o nome no letreiro e regenerar só B10 com “A chuva persistiu por um longo trecho”; Whisper confirmou | prompt |
| 2026-11-17 | Remasters #222 reconstruíram inscrições pequenas e detalhes incertos em fotos de pessoas/motos | conservar todas as nove principais como originais em papel; restaurações de paisagem só no fundo | prompt |
| 2026-11-17 | Prévia #221 rejeitou âncora novecentos porque Whisper registrou 900 | usar Wd com 900 e validar todos os beats antes do render | prompt |
| 2026-11-17 | Voz #221 trocou conectivos e topônimos em B04/B09/B11, repetiu “na viagem” no fecho e deixou pausas longas | reescrever só três blocos; cortar repetição/pausas preservando tomadas e conferir novamente pelo Whisper | prompt |
| 2026-11-17 | Remaster #221 reconstruiu placas nas motos 002/003 e detalhes incertos de pessoas 004/006 | manter essas fotos originais em papel e aprovar paisagens separadamente | prompt |
| 2026-11-17 | Auditoria #219 encontrou ruído em pausas sem palavras, sobretudo B10 | silenciar só intervalos fora das palavras, com fades de 25 ms e duração preservada; retranscrever | infra |
| 2026-11-17 | Prévia #219 acumulou gráficos de blocos diferentes no fundo | copiar imagem retornada por fundo() antes de desenhar; cache nunca é alterado | infra |
| 2026-11-17 | Voz #219 abriu com “em carro” e trocou “na seguinte” por “no seguinte” | reescrever apenas B01/B04 e regenerar; Whisper confirmou as duas | prompt |
| 2026-11-17 | Depth #219 não salvou porque v1/depth ainda não existia | criar diretório antes de gerar_depth.mjs | prompt |
| 2026-11-17 | Remaster #219 reconstruiu inscrições/obstáculos em fotos de jipes | usar originais em papel; aprovar só panoramas fiéis 034/039 | prompt |
| 2026-11-16 | Voz #218 repetiu sílaba após Cusco e deformou Punta Sal | reescrever só B05/B08, nomes nos letreiros; simplificar B09 | prompt |
| 2026-11-16 | Voz #218 deixou murmúrio de 1 s na pausa do B03 | cortar 10.65–12.55 s entre palavras e atualizar tempos; checa sem buraco | infra |
| 2026-11-16 | Wd refeições no B07 #218 pegou a primeira ocorrência e deu duração negativa | indicar segunda ocorrência; prévia validou os 30 beats | prompt |
| 2026-11-16 | ffmpeg recusou duração .025 no afade do corte #218 | escrever 0.025 | prompt |
| 2026-11-16 | Detecção amarela de marca #218 confundiu vegetação e cortou fotos demais | limitar corte à faixa inferior medida: 64 px em 600 px | prompt |

| 2026-11-16 | Prévia #217 detectou principal 276 ausente por índice 270 digitado | Corrigir índice e validar cobertura antes do render | prompt |
| 2026-11-16 | Pré-teste #217 encontrou âncora Enquanto removida do roteiro | Trocar pela nova palavra Muitos antes do render | prompt |
| 2026-11-16 | Auditoria #217 abriu B09 durante substituição pela pós-produção | Aguardar a pós e pular WAV ausente antes da leitura | prompt |
| 2026-11-16 | Remaster #217 foto 406 acrescentou faixa clara ao céu | Preservar original como cópia em papel | infra |
| 2026-11-16 | TTS #217 B09 juntou “Enquanto muita gente dormia” à chegada a Ottawa | Reescrever com sujeitos explícitos e regenerar só B09 | prompt |

| 2026-11-16 | Carimbos verticais #214 nas fotos 012/016 sobravam após corte inferior e lateral de 18 px | Medir a marca (x22–34) e cortar 40 px à esquerda a partir do original; refazer só B02/B08/B12 | prompt |
| 2026-11-16 | Compressão #214 em uma passada perdeu detalhes das paisagens e criou blocos no fundo | Duas passadas a 1750k e reduzir grão local de 7 para 1,2; conferir quadros do MP4 | infra |
| 2026-11-16 | Voz #214 trocou “passada a ferro”, concordância das motos e Monte Quemado | Reescrever B03/B04/B09 com frases simples; conferir novamente pelo Whisper | infra |
| 2026-11-16 | Indexação #214 iniciou antes do download da página terminar | Aguardar a sessão de download concluir antes de abrir mat.htm | prompt |

| 2026-11-15 | Voz #211 repetiu “A chuva”, trocou Fenasoja por Fenasóia e acolhimento por aconimento na revisão | Reescrever B01/B07 e reaproveitar a tomada original correta do B12; conferir pelo Whisper | infra |

| 2026-11-15 | Classificação #211 salva no repo por saída relativa | Mover JSONs para o episódio e usar --saida absoluto | prompt |

| data | o que quebrou | menor correção | prompt \| infra |
|---|---|---|---|
| 2026-11-25 | #255: a checagem de pausas marcou fala válida com fim de fatia negativo | checar a duração do intervalo antes de fatiar e recalcular com os tempos já salvos | infra |
| 2026-11-25 | #255: Chatterbox juntou “a mostra” e a data de 1933 à frase anterior; Caxias saiu impreciso | reescrever B03/B06 com termos diretos e data no fim da oração dos municípios | prompt |
| 23/11/2026 | #250: pré-teste recusou âncora trinta no B02 | Usar token 30 do Whisper antes de renderizar | prompt |
| 23/11/2026 | #250: som não transcrito nas pausas de B04/B08 | Frases mais diretas e regeneração só dos dois blocos; nova transcrição completa e pausas limpas | infra |
| 18/11/2026 | #228 tentativa de abrir foto por nome digitado falhou | obter o caminho pelo indice.json em vez de reconstruir timestamp | prompt |
| 18/11/2026 | #228 remaster 299 deixou barra preta no rodapé; pausa B03 tinha ruído a −34 dB | conservar foto original e silenciar só interior da pausa sem mudar duração | infra |
| 18/11/2026 | #228 voz juntou “Claci ficou” em “classificou” e falhou em “genro” no B09 | reescrever só a frase como “A viagem dela continuou em Milão, na companhia da família” e regenerar B09 | infra |
| 18/11/2026 | #228 filme.py com parêntese final ausente no fecho | fechar dict e validar com py_compile antes de importar | prompt |
| 2026-11-18 | #226: voz disse acredita no lugar de credita no fecho | trocar por As fotos são de Ayumi e regenerar só B11; Whisper confirmou | prompt |
| 2026-11-18 | #226: remaster 000 alterou caracteres pequenos do casco; pessoas de 003/006 ficaram reconstruídas | manter os registros originais em papel; reservar remaster a fundos seguros | prompt |
| 2026-11-17 | #220 TTS pronunciou “curva indecida” e depois trocou preposição na abertura | reescrever para “curva da estrada” e omitir a frase inicial secundária do WAV/roteiro | prompt |
| 2026-11-17 | #220 pós encerrada por SIGTERM antes de salvar índices finais | recuperar JSON das transcrições e persistir índices a cada bloco | infra |
| 2026-11-17 | #220 remaster do pôr do sol adicionou rocha e deixou detalhes incertos em bicicletas/fachada | conservar 001/002/011 originais em papel; não repetir geração | prompt |
| 2026-11-16 | Voz #216 colou “esposas” e “Dali em diante” às frases anteriores | Reescrever B03/B04 com sujeitos explícitos e regenerar só esses blocos | prompt |
| 2026-11-16 | #213 remaster 013 reconstruiu figuras entre redes e 017/020 inscrições do barco | Usar originais em papel; só 012 como plano cheio | prompt |
| 2026-11-16 | #213 TTS disse “corrida” em vez de “acolhida” | Trocar a primeira frase do B10 por “Os amigos receberam Foffão em Manaus” e regenerar só o bloco | prompt |
| 2026-11-16 | #213 TTS deformou “Depois vieram Estreito” e “Castanhal” | Reescrever só B06 com frases curtas e lugar difícil apenas no letreiro | prompt |
| 2026-11-15 | #212 pausas com ruído fora das palavras nos B05/B09/B10 | cortar só os intervalos e retranscrever os três blocos; frases preservadas | infra |
| 2026-11-15 | #212 ffmpeg rejeitou d=.025 no corte das pausas | usar d=0.025 e marcar corte concluído só após sucesso | prompt |
| 2026-11-15 | #212 prévia parou na âncora “Nei”, transcrita “Ney” | usar a palavra única “deixou” no B04 antes do render | prompt |
| 2026-11-15 | #212 fecho pronunciou “acevo” no lugar de “acervo” | reescrever só B12 e regenerar; Whisper confirmou “acervo” na nova tomada | infra |
| 2026-11-15 | #212 TTS omitiu a última frase do B05 | remover do roteiro a frase secundária ausente; manter a tomada correta conferida no Whisper | infra |
| 15/11/2026 | #210: prévia da montagem achou depth ausente da foto 013 acrescentada após gerar os mapas | gerar só o depth 013 e conferir todas as instâncias Prof antes do render | prompt |
| 15/11/2026 | #210: B01 e B05 tinham ~1,5 s de murmúrio entre frases não transcrito pelo Whisper | cortar somente os dois intervalos ruidosos, preservando as palavras e ajustando seus tempos | prompt |
| 15/11/2026 | #210: pré-render não achou âncora Luis porque Whisper escreveu Luiz | usar a palavra única aproveitava e validar blocos() antes do render | prompt |
| 15/11/2026 | #210: voz trocou excursões por discussões e Diego de Alvear por Alviar | trocar para guias de turismo e deixar o lugar somente no letreiro; regenerar só B06/B08 | prompt |
| 15/11/2026 | #210: correção no roteiro durante tts.sh não entrou no B11, pois blocos.tsv já estava carregado | regenerar só B11 após finalizar o lote com o roteiro definitivo | prompt |
| 15/11/2026 | #209: classificador devolveu índices 1–30 apesar da folha 000–029 | normalizar índice pelo nome do arquivo em indice.json e exigir cobertura exata | prompt |
| 15/11/2026 | #209: B08 tinha pausa de 2,94 s com som fora das palavras depois de serra | cortar só 4,12–6,72 s, deslocar tempos posteriores e renderizar apenas B08 | prompt |
| 15/11/2026 | #209: voz errou rafting/pomar e omitiu a última frase do B08 | reformular as palavras e regenerar apenas os blocos afetados, conferindo a frase final | prompt |
| 15/11/2026 | #209: remaster terminou com SIGTERM 143 depois de salvar a última imagem no work_029 | recuperar o PNG já gerado antes de repetir o lote | infra |
| 15/11/2026 | #209: URL da matéria sem zero inicial retornou 404 | usar idmat031816.htm e idmat031814.htm | prompt |
| 15/11/2026 | produtor descartava sucessivas matérias como erro_producao ao esgotar a cota semanal do Claude | motor configurável em YAML, Codex assinatura ativo e falha de execução preserva em_producao para retomar | infra |
| 12/11/2026 | #192: 1º `tts_lote.py` morreu com "CUDA error: out of memory" ao carregar o chatterbox (GPU cheia de outro job) | laço que testa `torch.zeros(1).cuda()` a cada 60 s antes de rodar (liberou em 2 min); falta esse laço dentro do tts_lote.py | infra |
| 10/11/2026 | #181: `tts_lote.py` com 4 blocos refeitos saiu no meio (código ≠ 0, sem WAV, última linha do log = aviso de repetição de token do chatterbox) | rodar o mesmo comando de novo (saiu na 2ª); falta retry dentro do tts_lote.py | infra |
| 08/11/2026 | #171: worker do `tts_lote.py` travou depois da 1ª de 29 frases (3% de CPU, 12 min) rodando sob `systemd-run --scope -p MemoryMax=24G` com outro job de 29 GB na GPU | matar e rodar o `tts_lote.py` SEM o scope, só com `timeout 2400` (29 frases em ~6 min) | infra |
| 08/11/2026 | #170: `pos_voz.py` caiu 3× com "CUDA error: out of memory" no `whisper.load_model` (GPU com só ~30 GB em uso; o load direto falha, um tensor criado antes não) | `torch.zeros(1, device="cuda")` antes do `import whisper` (no motor/pos_voz.py) | infra |
| 08/11/2026 | #168: `enviar_bot.py` (vídeo de 44 MB) caiu com "The write operation timed out" no 1º envio ao inemaytbot | repetir o envio uma vez (2ª saiu `sendVideo True`); falta retry dentro do enviar_bot.py | infra |
| 04/11/2026 | #147: worker do `tts_lote.py` (3 blocos refeitos) travou 12 min a 3,5% de CPU com a GPU dividida (2ª vez, como #59) | matar o worker, relançar só os blocos com `timeout 1500`; falta teto de tempo dentro do tts_lote.py | infra |
| 04/11/2026 | #147: 1º render com letreiro de lugar sobre a carta errada (NAVIRAÍ e PUERTO IGUAZÚ sobre a colagem de baixo da pilha), "NATAL EM CUIABÁ" (o Natal foi na casa dos pais) e "PIRACICABA" sobre a foto de Naviraí | foto com a placa por último na `Pilha`, letreiro só com o que a carta de cima prova; revisão pegou antes do envio final | prompt |
| 30/10/2026 | #131: `rclone copy` do álbum 0095497 (667 fotos) parou 2 vezes pelo teto de 10 min do Bash e o B2 devolveu 503 too_busy/500 em 4 arquivos (663 de 667) | rodar o download em `run_in_background` com `timeout` longo e `--transfers 16`; seguir sem as 4 (nenhuma da página) | infra |
| 27/10/2026 | #116: 12 cartões (`Pilha`) do 1º render com a foto errada: `indice.json` em ordem do nº e `v3.A` em ordem alfabética (o Prof, pelo F(i), saiu certo) | `A = v3.A = json.load(open('indice.json'))` no filme.py; a folha de quadros pegou antes do envio | prompt |
| 27/10/2026 | #114: 1º render caiu com FileNotFoundError v1/depth/c114_040.png (lista de fotos do gerar_depth feita à mão, faltou uma) | gerar a lista pelo `grep -oE "pf\([0-9]+" filme.py`; falta o filme.py checar os depth antes do Pool | prompt |
| 26/10/2026 | #108: enviar_bot.py deu HTTP 400 "too Many Requests: retry after 8" duas vezes no sendVideo ao inemaytbot | 3ª tentativa, com espera de 40–120 s, passou; falta retry com espera no enviar_bot.py (mesma proteção do #98) | infra |
| 24/10/2026 | #104: 1º render com rótulos do mapa no mar e o Rio sob o letreiro: motor/render_v4.py não tem ROTULO_LADO (só cópias de episódio têm) | copiar o trecho do render_v4 de um episódio (#97) para a cópia local; falta portar para o motor | infra |
| 22/10/2026 | #98: enviar_bot.py deu "The write operation timed out" no envio do mp4 de 44 MB ao inemaytbot | 2ª tentativa passou (sendVideo True); falta um retry automático no enviar_bot.py | infra |
| 21/10/2026 | cortes.py: drawtext do ffmpeg 6.1.1 cortava o fim de linhas com acento ("#74"→"#7", "CANAL"→"CA") | textos desenhados num PNG pelo PIL e sobrepostos com overlay | infra |
| 2026-11-10 | #184: TTS chatterbox e Whisper com `CUDA error: out of memory` até em `torch.zeros` (GPU disputada por outros serviços, ~15 min) | laço no TTS esperando a GPU (teste a cada 60 s) + Whisper do pos_voz com queda para CPU | infra |
| 20/10/2026 | fila do canal parou 25 h (19/10 18:00 → 20/10 19:00): publicar_episodio.narracao() exigia "## Narração" e os 16 roteiros novos da fila vêm só com B01…; IndexError + AJUDA no v3 a cada 30 min | narracao() usa o texto todo quando falta o título (testado nos 67 roteiros) | prompt |
| 18/10/2026 | #79: worker do tts_lote.py parou 9 min na 7ª de 29 frases (GPU com outro processo de 29 GB) | copiar voz/lote/seg_*.wav, matar o worker, remontar B01–B03 e relançar só B04–B14 (lição #59); falta um teto de tempo por frase no worker | infra |
| 17/10/2026 | fila parou 12 h (24 falhas): token próprio do yt-pubx aventuras venceu (app OAuth em modo Teste = 7 dias) | yt-pubx aventuras passou a ler a credencial do lives26 (credenciais_cmd lives-cred.py lives26), renovada pelo painel; falta publicar o app OAuth | infra |
| 16/10/2026 | #72: a `Faixa` do B02 mostrou a tira de patrocinador "NOSSO POSTO" e o mapa da viagem de 2009 (fotos do álbum fora do assunto) | montar as listas da `Faixa` sem as fotos marcadas `ruim` na `classificacao.json` e conferir a folha do bloco | prompt |
| 15/10/2026 | #64: regeneração de 5 blocos de voz saiu idêntica à antiga — o `pos_voz.py` usa `voz/bruto/<B>.wav` se existe e sobrescreveu a voz nova | apagar `voz/bruto/<B>.wav` dos blocos refeitos antes do `pos_voz.py` | prompt |
| 15/10/2026 | #60: corte fixo de 56 px serrou ao meio o carimbo de data das fotos 799x600; letreiros de mapa davam a distância do dia inteiro a um só trecho ("São Borja → Corrientes 1.017 km") | medir marca e carimbo no canto de cada álbum antes do corte (aqui 72 px); letreiro de distância diz de onde a onde o número vale | prompt |
| 15/10/2026 | #59: worker do chatterbox (`tts_lote.py`) travou na 17ª de 30 frases, 30 min sem progresso com a GPU dividida | salvar `voz/lote/seg_*.wav`, matar o worker, remontar os blocos prontos e relançar só os que faltam | infra |
| 15/10/2026 | #57: com a GPU dividida o chatterbox levou até 5,5 min só para carregar; 11 de 13 blocos estouraram os 600 s do `tts_direct` (2 h perdidas) | `tts_lote.py` no episódio: carrega o modelo uma vez para todos os blocos que faltam, sem teto de 600 s | infra |
| 14/10/2026 | #50: chatterbox não disse a última frase de B11 e de B08 e o `pos_voz` cortou no fim do Whisper, sem erro (o bloco ficou mais curto) | refazer o bloco com a frase reescrita; proteção: comparar o fim da transcrição com a última frase do roteiro | infra |
| 14/10/2026 | #50: `tts.sh` em `run_in_background` foi morto no teto padrão de 10 min (B01 esperou a GPU dividida) | relançar com `timeout` de 2 h (o script só refaz o que falta) | prompt |
| 13/10/2026 | #47 TTS B06 estourou os 600 s do chatterbox (GPU dividida com 2 outros TTS) | rerodar `tts.sh` (idempotente); proteção: fila única de GPU ou teto maior | infra |
| 13/10/2026 | #42 B09: `Wd(b, 'Foi')` casou com o 1º "foi" (do curry), o beat da ponte ficou depois do seguinte e a Tower Bridge sumiu, sem erro | `Wd(b, 'Foi', 1)`; proteção: conferir em `blocos()` que os tempos dos beats crescem | prompt |
| 13/10/2026 | #33: `remaster_codex.py` lançado com `nohup … &` morreu junto com a chamada do Bash (3 de 9 fotos) e o laço `pgrep -f remaster_codex.py` ficou preso casando consigo mesmo | relançar as 6 que faltavam com `run_in_background`; esperar pelo arquivo de log, não por `pgrep -f` | prompt |
| 13/10/2026 | #33: a marca inema.com.br do álbum 0020393 fica mais alta (linhas 350–380) e o corte de 46 px a deixava à vista | medir os pixels amarelos por álbum, cortar 56 px e fazer `v3.foto` ler de fotos-clean | infra |
| 13/10/2026 | #31 (194 s, 65 MB a 2500k): `enviar_bot.py` recusou o envio por passar de 50 MB (limite do Telegram) | cópia leve só para o bot (`-b:v 1600k`, 42 MB); proteção: o `enviar_bot.py` recodificar sozinho quando o arquivo passar de 50 MB | infra |
| 13/10/2026 | teste de modelo (Sonnet) e laço principal (Opus) mexeram no mesmo episódio: o laço "retomou" o em_producao do teste, reprovou em 1 min e renomeou o EPISODIO.json; dois #27 | candidato do teste ganha `teste=<modelo>` e a retomada pula esses; reiniciar aventuras-produz antes do próximo teste | infra |
| 13/10/2026 | #28 com dois agentes na mesma pasta: a retomada do `produz_loop.sh` pegou um `em_producao` que outro laço (teste Haiku) produzia naquele momento | retomar só se nenhum `claude -p` vivo tiver a pasta (gravar PID na reserva e checar com `kill -0`) | infra |
| 13/10/2026 | cópias de foto da `Pilha` iam para a borda (cortadas pelo zoom da câmera) e o meio da tela ficava vazio: a escolha só maximizava a distância entre as cópias | posição limitada para a cópia caber inteira (tamanho girado + margem do zoom) e nota que desconta a distância do centro | infra |
| 12/10/2026 | fila parou 11/10 08:03 (codex 0.116 do /usr/bin morreu no config.toml) e ficou 18 h parada sem ninguém saber; 9 episódios prontos e e-mails de aviso já enviados | PATH com ~/.npm-global/bin no fila_publicar.sh + erro vira pedido de ajuda no bot v3 repetido a cada 30 min, sem sair | infra + prompt |
| 11/10/2026 | #19: voz `nei` gaguejou antes de citação com dois-pontos ("pergunta: Fei, vocês…") e leu "USB" como "os bi" | fala em discurso indireto sem dois-pontos e sigla escrita como se fala ("u-esse-bê"); citação literal só no letreiro | prompt |
| 11/10/2026 | #17: render caiu com "box can't exceed original image size": `Pilha` sem `z` (zoom 1,012) e muitas cópias com `every` curto somam tremida maior que a margem | dar `z=(1.02, 1.08)` ou mais a toda `Pilha` com muitas cópias/tremida | infra |
| 10/10/2026 | #13: última palavra do bloco ("jamanta") sumiu do WAV final: Whisper não a transcreveu no bruto e o `pos_voz` corta na última palavra transcrita | conferir a última palavra de cada bloco na transcrição; faltou = gerar o bloco de novo | infra |
| 10/10/2026 | #13 (evitado): `conta=` com v1 ≥ 100 arredonda a dezenas, 273 vira "270 KM" | número que não termina em 0 vai como texto fixo, sem `conta` | infra |
| 10/10/2026 | #13: mapa regional (~1,5°) com `MS` alto engrossa bordas e letreiros do `mapa_base` e o litoral do paises.geojson fica grosseiro | `mapa_base` próprio no filme.py com terra = uf.json e mar claro (rótulo escuro legível) | infra |
| 10/10/2026 | #12: voz `nei` estropiou nome espanhol ("El Tatio" 3× → Altatiel/Eltatil; "San Antonio de los Cobres" → Luscovitz) | tirar o nome da fala e deixar no letreiro | prompt |
| 10/10/2026 | #7: render travou 20 min sem erro (âncora `Wd` inexistente → SystemExit no worker do Pool) | validar `filme.blocos()` num processo só antes do render | prompt |
| 10/10/2026 | #7: contador `conta=(2500, 4800, …)` mostrou "27.300 METROS" (precedência na fórmula do render_v4) | parênteses na fórmula do motor (corrigido em motor/render_v4.py) | infra |
