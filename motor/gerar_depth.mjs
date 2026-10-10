// depth (Depth-Anything-V2-small, mesmo modelo do pixflow) para as fotos cheias da v4; branco = perto
const { generateDepth } = await import((process.env.PIXFLOW_DIR || process.env.HOME + '/projetos/pixflow/skill') + '/cli/depth.mjs');
import { existsSync } from 'fs';
for (const img of process.argv.slice(2)) {
  const out = `v1/depth/${img.split('/').pop().replace(/\.(jpg|png)$/, '')}.png`;
  if (!existsSync(out)) { await generateDepth(img, out); console.log(out); }
}
process.exit(0);
