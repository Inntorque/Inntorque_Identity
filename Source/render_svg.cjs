const sharp = require('/Users/patrickstar/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/sharp');
const fs = require('fs');
const path = require('path');
async function main() {
  const [source, target, width] = process.argv.slice(2);
  let render = sharp(fs.readFileSync(source), {density: 72});
  if (width) render = render.resize({width: Number(width)});
  await render.png().toFile(target);
}
main().catch(e => { process.stderr.write(String(e)); process.exit(1); });
