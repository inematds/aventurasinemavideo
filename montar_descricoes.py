#!/usr/bin/env python3
"""Monta a descrição completa de cada episódio no canal Aventuras INEMA (pedido do Nei, 10/10/2026):
abertura + a narração inteira do filme + dados do registro + link da matéria (ao lado, sem http,
e de novo numa linha própria com https) + outros episódios. Saída em descricoes/<ep>.txt.
Uso: montar_descricoes.py [ep ...]"""
import json, os, re, sys

D = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.expanduser('~/projetos/output')
EPS = {  # ep: (pasta, vídeo, matéria principal, rótulo na lista de episódios)
    'telmo': ('memorias-aventura-telmo', 'sZ6PUmt_jp0', '063893', '#1 Telmo, 6.700 km de moto pela América do Sul'),
    'lameiros': ('memorias-aventura-lameiros', 'V9MKId8SaIc', '077235', '#2 Lameiros do Sul, Bonito e Pantanal'),
    'naoki': ('memorias-aventura-naoki', '4TIIarV5qoc', '020589', '#3 Naoki e Ricardo, escalada no Chile'),
    'natan': ('memorias-aventura-natan', 'LDSdt3WCwhk', '009355', '#4 Natan Smaniotto, de pai para filho nas pistas'),
    'ana': ('memorias-aventura-ana', 'cvu0vQpm_SQ', '010456', '#5 Ana Cristina Sommer, roupa para mulheres motociclistas'),
    'guilherme': ('memorias-aventura-guilherme', 'ZeFrkHhlhuY', '088434', '#6 Guilherme Borges, Andes Kids Expedition 2003'),
}
REGISTRO = {
    'telmo': ['Viagem: 13 a 26 de novembro de 2004, Porto Alegre → Argentina → Chile → Uruguai → Porto Alegre',
              'Diário de Telmo Machado da Silva, publicado no INEMA em 2005 em 12 partes, mais as considerações finais',
              'Fotos do álbum de Telmo Machado da Silva'],
    'lameiros': ['Expedição Bonito/Pantanal: 12 a 22 de julho de 2006, 11 jipes e 37 pessoas',
                 'Relato de Jerri Garfão, publicado no INEMA em 27/07/2006 em duas partes',
                 'Organização: Luís Klauck e Luciano Strelow · 882 fotos no álbum da expedição'],
    'naoki': ['Viagem: 9 a 25 de outubro de 2002, Las Chilcas, Cajón del Maipo, Las Palestras e Piedra Romel (Chile)',
              'Relato de Naoki Arima, publicado no INEMA em 11/09/2003',
              'Escaladores: Naoki Arima e Ricardo Rutz, de Porto Alegre'],
    'natan': ['"Os Smaniotto e a paixão pelo motociclismo!", publicado no INEMA em 18/04/2002 (fonte: Vlademir Smaniotto)',
              '"III Enduro de Regularidade - Natan Smaniotto", Ivoti, 17/04/2005: Natan campeão da categoria Júnior',
              'Família: Vlademir (pai), Natan e Jessé Smaniotto, de Novo Hamburgo'],
    'ana': ['"Grife Cristina Sommer chega ao mercado", publicado no INEMA em 13/06/2002 (fonte: Ana Cristina Sommer Pereira)',
            'Lançamento da coleção: sábado, 15/06/2002, 9h, no café dos motociclistas da Turbo Motos, Porto Alegre',
            'Fotos de Ayumi Miyazaki'],
}
NUM = [('dois mil e seis', '2006'), ('dois mil e cinco', '2005'), ('dois mil e três', '2003'),
       ('dois mil e dois', '2002'), ('dois mil e quatro', '2004')]


def narracao(pasta):
    txt = open(f'{OUT}/{pasta}/roteiro.md').read().split('## Narração', 1)[1]
    blocos = [re.sub(r'^B\d+( \([^)]*\))? — ', '', l).strip() for l in txt.splitlines() if re.match(r'^B\d+', l)]
    s = '\n\n'.join(blocos)
    for a, b in NUM:
        s = s.replace(a, b).replace(a.capitalize(), b)
    return s


def montar(ep):
    pasta, vid, mat, _ = EPS[ep]
    plano = json.load(open(f'{D}/planos-aventuras/{ep}/plano.json'))['youtube']['snippet']['description'].split('\n\n')
    abertura, tags = plano[0], [p for p in plano if p.startswith('#')][-1]
    partes = [abertura, 'A HISTÓRIA', narracao(pasta), 'SOBRE O REGISTRO', '\n'.join(REGISTRO[ep]),
              f'Matéria original com as fotos (para assinantes): aventura.inema.club/mat/idmat{mat}.htm',
              f'https://aventura.inema.club/mat/idmat{mat}.htm',
              'Você esteve nessa aventura ou tem a sua própria história guardada no INEMA? Conte nos comentários.',
              'OUTROS EPISÓDIOS DE MEMÓRIAS DE AVENTURA',
              '\n'.join(f'{r}: https://www.youtube.com/watch?v={v}' for e, (_, v, _, r) in EPS.items() if e != ep),
              'Acervo INEMA Aventura: https://aventura.inema.club', tags]
    d = '\n\n'.join(partes)
    assert len(d) <= 4900 and '<' not in d and '>' not in d, (ep, len(d))
    open(f'{D}/descricoes/{ep}.txt', 'w').write(d + '\n')
    return len(d)


if __name__ == '__main__':
    for ep in sys.argv[1:] or [e for e in EPS if e != 'guilherme']:
        print(ep, montar(ep), 'caracteres')
