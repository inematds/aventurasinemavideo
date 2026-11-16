import copy
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('motor_aventura', ROOT/'auto/ia_motor.py')
ia = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ia)

class Contrato(unittest.TestCase):
    def test_seletores_explicitos_e_ambiente_sem_chaves(self):
        for motor, modelo in [('codex', 'gpt-6.1-sol'), ('claude', 'claude-opus-5-5')]:
            c = dict(ia.carregar()['etapas']['producao'], motor=motor, modelo=modelo)
            cmd = ia.comando(c, agente=True, saida='/tmp/resposta')
            self.assertIn(modelo, cmd)
            self.assertTrue(any('medium' in x for x in cmd))
        with patch.dict(os.environ, {'ANTHROPIC_API_KEY':'sintetico','OPENAI_API_KEY':'sintetico','CLAUDE_MODEL':'outro'}):
            env = ia.ambiente()
            self.assertNotIn('ANTHROPIC_API_KEY', env)
            self.assertNotIn('OPENAI_API_KEY', env)
            self.assertNotIn('CLAUDE_MODEL', env)

    def test_api_agente_bloqueada_e_comentarios_preservados(self):
        d = copy.deepcopy(ia.carregar())
        d['etapas']['producao'].update(tipo='api', motor='anthropic', modelo='claude-opus-5-5')
        with self.assertRaises(ValueError): ia.validar(d)
        text = (ROOT/'auto/ia.yaml').read_text()
        changed = ia.alterar_com_comentarios(text, 'classificacao', {'esforco':'high'})
        self.assertEqual([l for l in text.splitlines() if l.startswith('#')], [l for l in changed.splitlines() if l.startswith('#')])
        self.assertIn('"high"', changed)

    def test_api_visao_nao_le_chave_sem_autorizacao(self):
        with patch.object(ia, 'ler_chave', side_effect=AssertionError('leu chave')):
            with self.assertRaisesRegex(ValueError, 'desativada'):
                ia.chamar_api({'motor':'anthropic'}, {'autorizada':False}, 'teste', [])

    def rodar_loop(self, rc):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td); (p/'auto').mkdir(); (p/'privado/tarefas').mkdir(parents=True)
            tarefa={'n':9999,'idmat':999999,'slug':'teste-isolado','pasta':str(p/'ep')}
            (p/'ep').mkdir()
            candidatos=[dict(tarefa,status='em_producao')]
            (p/'privado/candidatos.json').write_text(json.dumps(candidatos))
            (p/'privado/fila_publicar.txt').write_text('')
            (p/'PRODUZIR.md').write_text('TESTE SEM PRODUCAO')
            (p/'escolhe.py').write_text('print('+repr(json.dumps(tarefa))+')')
            (p/'auto/ia_motor.py').write_text('')
            (p/'auto/produzir.py').write_text('raise SystemExit('+str(rc)+')')
            (p/'verifica_ep.py').write_text("print('REPROVADO: ensaio')")
            shim=p/'scope'; shim.write_text('#!/bin/bash\nwhile [ "$1" != python3 ]; do shift; done\nexec "$@"\n'); shim.chmod(0o755)
            script=(ROOT/'produz_loop.sh').read_text().replace('systemd-run --user --scope',str(shim)+' --user --scope').replace('AVISA="$HOME/projetos/wifi/scripts/avisa-v3.sh"','AVISA=/bin/true')
            (p/'produz_loop.sh').write_text(script)
            result=subprocess.run(['bash',str(p/'produz_loop.sh')],env=dict(os.environ,UMA='1',NA_FILA='0'),capture_output=True,text=True,timeout=15)
            state=json.loads((p/'privado/candidatos.json').read_text())
            self.assertEqual((p/'privado/fila_publicar.txt').read_text(),'')
            if rc:
                self.assertEqual(result.returncode,rc)
                self.assertEqual(state,candidatos)
            else:
                self.assertEqual(result.returncode,0)
                self.assertEqual(state[0]['status'],'erro_producao')

    def test_falha_motor_preserva_materia_e_fila(self): self.rodar_loop(23)
    def test_portao_editorial_continua_reprovando(self): self.rodar_loop(0)

if __name__ == '__main__': unittest.main()
