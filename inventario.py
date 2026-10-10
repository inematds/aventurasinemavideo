#!/usr/bin/env python3
"""Inventário das matérias do acervo com relato e fotos (critério do PLANO.md).
1) exporta do D1 as matérias com álbum → privado/materias_album.json
2) baixa cada matéria do B2 público, tira o texto padrão do INEMA e conta as palavras do relato
   → privado/inventario.jsonl (retomável: pula o que já foi medido); guarda o texto das que passam
   do corte em privado/textos/<idmat>.txt
Uso: inventario.py [exportar|medir|resumo]   (sem argumento = os três)"""
import html, json, os, re, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
import urllib.request

D = os.path.dirname(os.path.abspath(__file__))
P = f'{D}/privado'
WORKER = os.path.expanduser('~/projetos/inemaonline/worker')
B2 = 'https://f005.backblazeb2.com/file/inemaaventura/mat/idmat{:06d}.htm'
CORTE = 250
PADRAO = [  # frases do texto padrão das pautas de fotos e do rodapé
    r'O INEMA partiu de uma id[ée]ia.*?seu esporte!', r'Confira as fotos enviadas por[^.!]*[.!]',
    r'Contatos com a Equipe INEMA:.*', r'Aconteceu \d+ \w+ \d{4}, Evento:[^.!]*[.!]',
    r'Qualquer pessoa pode ser um colaborador.*?Upload[^.]*\.', r'Chamamos ent[ãa]o, COLABORADORES.*?compartilhar conosco\.',
]


def d1(sql):
    r = subprocess.run(['npx', 'wrangler', 'd1', 'execute', 'inemaonline', '--remote', '--json', '--command', sql],
                       cwd=WORKER, capture_output=True, text=True, timeout=300)
    return json.loads(r.stdout)[0]['results']


def exportar():
    rows = d1("select idmat, assunto, trim(area) area, cidade, uf, dt_publicado dt, linkimg from materias "
              "where linkimg like '%lbuns/%'")
    for r in rows:
        m = re.search(r'lbuns/(\d+)/', r.pop('linkimg') or '')
        r['album'] = m.group(1) if m else None
    os.makedirs(P, exist_ok=True)
    json.dump(rows, open(f'{P}/materias_album.json', 'w'), ensure_ascii=False)
    print('exportadas', len(rows))


def texto(idmat):
    raw = urllib.request.urlopen(B2.format(idmat), timeout=30).read().decode('latin-1', 'replace')
    if 'Ã' in raw:  # página já em utf-8
        raw = raw.encode('latin-1', 'replace').decode('utf-8', 'replace')
    raw = re.sub(r'(?is)<(script|style)[^>]*>.*?</\1>', ' ', raw)
    t = html.unescape(re.sub(r'(?s)<[^>]+>', '\n', raw))
    t = re.sub(r'[ \t\r]+', ' ', t)
    linhas = [l.strip() for l in t.split('\n') if len(l.strip()) > 60]  # menus e rótulos são curtos
    corpo = '\n'.join(linhas)
    for p in PADRAO:
        corpo = re.sub(p, ' ', corpo, flags=re.S | re.I)
    return corpo.strip()


def medir_um(r):
    try:
        t = texto(r['idmat'])
        n = len(re.findall(r'\w+', t))
        if n >= CORTE:
            open(f"{P}/textos/{r['idmat']}.txt", 'w').write(t)
        return {'idmat': r['idmat'], 'palavras': n}
    except Exception as e:
        return {'idmat': r['idmat'], 'erro': str(e)[:80]}


def medir():
    os.makedirs(f'{P}/textos', exist_ok=True)
    feitos = set()
    if os.path.exists(f'{P}/inventario.jsonl'):
        feitos = {json.loads(l)['idmat'] for l in open(f'{P}/inventario.jsonl')}
    todos = [r for r in json.load(open(f'{P}/materias_album.json')) if r['idmat'] not in feitos]
    print('a medir', len(todos), flush=True)
    with open(f'{P}/inventario.jsonl', 'a') as out, ThreadPoolExecutor(16) as ex:
        for k, res in enumerate(ex.map(medir_um, todos), 1):
            out.write(json.dumps(res) + '\n')
            if k % 1000 == 0:
                out.flush()
                print(k, flush=True)


def resumo():
    med = {}
    for l in open(f'{P}/inventario.jsonl'):
        r = json.loads(l)
        med[r['idmat']] = r
    ok = [r for r in med.values() if r.get('palavras', 0) >= CORTE]
    print('medidas', len(med), '| erros', sum('erro' in r for r in med.values()), f'| ≥{CORTE} palavras', len(ok))



def pessoas():
    """Liga as matérias que passaram do corte às pessoas (materias_pessoas → pessoas → contacts) e marca assinante ativo.
    Saída: privado/candidatos.json (e-mail fica só aqui, fora do git)."""
    med = {}
    for l in open(f'{P}/inventario.jsonl'):
        r = json.loads(l)
        med[r['idmat']] = r.get('palavras', 0)
    base = {r['idmat']: r for r in json.load(open(f'{P}/materias_album.json'))}
    ok = sorted(i for i, n in med.items() if n >= CORTE)
    lig = {}
    for k in range(0, len(ok), 400):
        ids = ','.join(map(str, ok[k:k + 400]))
        for r in d1(f"select mp.idmat, p.idf, p.nome from materias_pessoas mp join pessoas p on p.idf = mp.idf where mp.idmat in ({ids})"):
            lig.setdefault(r['idmat'], []).append({'idf': r['idf'], 'nome': r['nome']})
    idfs = sorted({p['idf'] for v in lig.values() for p in v})
    cont = {}
    for k in range(0, len(idfs), 400):
        ids = ','.join(map(str, idfs[k:k + 400]))
        for r in d1(f"select legacy_idf idf, email, unsubscribed_at u, opt_in_email o from contacts where legacy_idf in ({ids})"):
            cont[r['idf']] = r
    ass = {r['idf'] for r in d1("select c.legacy_idf idf from subscriptions s join users u on u.id = s.user_id "
                                "join contacts c on lower(c.email) = lower(u.email) where s.status = 'active' and c.legacy_idf is not null")}
    out = []
    for i in ok:
        m = base[i]
        ps = []
        for p in lig.get(i, []):
            c = cont.get(p['idf'], {})
            ps.append({**p, 'email': c.get('email') if c and not c.get('u') and c.get('o', 1) else None,
                       'assinante': p['idf'] in ass})
        out.append({**m, 'palavras': med[i], 'pessoas': ps, 'assinante': any(p['assinante'] for p in ps), 'status': 'pendente'})
    feitos = {63893, 77235, 77151, 20589, 9355, 61145, 10456, 10521, 88434}
    for c in out:
        if c['idmat'] in feitos:
            c['status'] = 'feito'
    json.dump(out, open(f'{P}/candidatos.json', 'w'), ensure_ascii=False, indent=0)
    print('candidatos', len(out), '| de assinante', sum(c['assinante'] for c in out),
          '| com e-mail', sum(any(p['email'] for p in c['pessoas']) for c in out))

if __name__ == '__main__':
    passos = sys.argv[1:] or ['exportar', 'medir', 'resumo', 'pessoas']
    for p in passos:
        globals()[p]()
