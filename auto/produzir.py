#!/usr/bin/env python3
"""Executa o produtor pela assinatura selecionada; log JSON sem preço fictício."""
import json
from pathlib import Path
import sys
from ia_motor import carregar, executar


def main():
    try:
        c = carregar()['etapas']['producao']
        print('IA selecionada: ' + '/'.join(c[k] for k in ('tipo', 'motor', 'modelo', 'esforco')), file=sys.stderr, flush=True)
        resposta = executar('producao', sys.stdin.read(), Path.cwd(), agente=True)
        print(json.dumps({'is_error': False, 'result': resposta, 'cobranca': 'assinatura'}, ensure_ascii=False))
        return 0
    except Exception as e:
        print(json.dumps({'is_error': True, 'erro_motor': True, 'result': str(e)}, ensure_ascii=False))
        return 1

if __name__ == '__main__':
    sys.exit(main())
