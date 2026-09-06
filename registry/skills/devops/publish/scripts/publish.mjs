import { readFile, readdir, lstat, mkdir, writeFile, appendFile, mkdtemp, access, realpath } from 'node:fs/promises';
import { constants } from 'node:fs';
import { resolve, relative, join, dirname, basename, extname } from 'node:path';
import { tmpdir } from 'node:os';
import { createHash } from 'node:crypto';
import { spawnSync } from 'node:child_process';

const args = process.argv.slice(2), options = {};
for (let i = 0; i < args.length; i++) {
  const key = args[i];
  if (['--public', '--dry-run'].includes(key)) options[key] = true;
  else if (['--input', '--project', '--branch', '--handoff', '--wrangler'].includes(key) && args[i + 1] && !args[i + 1].startsWith('--')) options[key] = args[++i];
  else throw new Error(`Unknown or missing argument: ${key}`);
}
for (const key of ['--input', '--project', '--handoff', '--wrangler']) if (!options[key]) throw new Error(`Required: ${key}`);
if (!options['--public']) throw new Error('Explicit public authorization is required; private publishing is unsupported');
if (!/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(options['--project'])) throw new Error('Invalid project name');
const input = resolve(options['--input']), handoff = resolve(options['--handoff']);
const inputStat = await lstat(input);
if (inputStat.isSymbolicLink() || (!inputStat.isDirectory() && extname(input) !== '.html')) throw new Error('Input must be a real static directory or HTML file');
const actualInput = await realpath(input);
const actualHandoff = join(await realpath(dirname(handoff)), basename(handoff));
const inside = relative(actualInput, actualHandoff);
if (actualInput === actualHandoff || (inputStat.isDirectory() && inside !== '..' && !inside.startsWith('../') && !inside.startsWith('/'))) throw new Error('Handoff must be outside public input');
await access(dirname(handoff), constants.W_OK);
try {
  if (!(await lstat(handoff)).isFile()) throw new Error('Handoff must be a regular file; symlinks are refused');
  await access(handoff, constants.W_OK);
} catch (error) { if (error.code !== 'ENOENT') throw error; }
const allowed = new Set(['.html','.css','.js','.json','.svg','.png','.jpg','.jpeg','.webp','.ico','.woff','.woff2','.txt','.xml','.md']);
const hash = bytes => createHash('sha256').update(bytes).digest('hex');
const files = [];
let totalBytes = 0;
const maxTotalBytes = 128 * 1024 * 1024;
async function inspect(file, name) {
  const stat = await lstat(file);
  if (stat.isSymbolicLink()) throw new Error(`Symlink refused: ${name}`);
  if (name.split('/').some(part => part.startsWith('.') || ['node_modules', 'functions'].includes(part))) throw new Error(`Hidden or source path refused: ${name}`);
  if (stat.isDirectory()) { for (const child of (await readdir(file)).sort()) await inspect(join(file, child), name ? `${name}/${child}` : child); return; }
  if (!stat.isFile() || stat.size > 25 * 1024 * 1024 || (!allowed.has(extname(name)) && name !== '_headers') || /^(?:package(?:-lock)?\.json|wrangler\..*|AGENTS\.md|SKILL\.md)$/i.test(name.split('/').at(-1))) throw new Error(`Not a bounded static asset: ${name}`);
  if (files.length >= 20000) throw new Error('Pages file count exceeded');
  if (totalBytes + stat.size > maxTotalBytes) throw new Error('Static upload exceeds the 128 MiB memory budget; split the publication');
  const bytes = await readFile(file);
  totalBytes += bytes.length;
  if (totalBytes > maxTotalBytes) throw new Error('Static input grew beyond the 128 MiB memory budget');
  if (!['.png','.jpg','.jpeg','.webp','.ico','.woff','.woff2'].includes(extname(name))) {
    const text = bytes.toString('utf8');
    if (/BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY|\b(?:ghp|gho|github_pat)_[A-Za-z0-9_]{16,}|\bsk-[A-Za-z0-9_-]{16,}|\bAKIA[0-9A-Z]{16}|(?:\/Users\/|\/home\/)[^\s<>"']+|file:\/\//.test(text)) throw new Error(`Publication scan failed: ${name}`);
  }
  files.push({ name, bytes, sha256: hash(bytes) });
}
if (inputStat.isDirectory()) { for (const name of (await readdir(input)).sort()) await inspect(join(input, name), name); }
else await inspect(input, 'index.html');
const root = files.find(file => file.name === 'index.html');
if (!root) throw new Error('Static output must contain index.html');
const artifact = hash(JSON.stringify(files.map(({ name, sha256 }) => ({ name, sha256 }))));
console.log(JSON.stringify({ verdict: 'preflight-pass', files: files.length, bytes: totalBytes, artifact_sha256: artifact }));
if (!options['--dry-run']) {
  const stage = await mkdtemp(join(tmpdir(), 'siso-publish-'));
  for (const file of files) { const target = join(stage, file.name); await mkdir(dirname(target), { recursive: true }); await writeFile(target, file.bytes); }
  const result = spawnSync(process.execPath, [resolve(options['--wrangler']), 'pages', 'deploy', stage, '--project-name', options['--project'], '--branch', options['--branch'] || 'main', '--commit-dirty=true'], { encoding: 'utf8', maxBuffer: 1024 * 1024, env: { ...process.env, NODE_OPTIONS: '--max-old-space-size=512', CI: '1' } });
  const output = `${result.stdout || ''}\n${result.stderr || ''}`;
  const urls = [...output.matchAll(/https:\/\/[a-z0-9-]+\.[a-z0-9-]+\.pages\.dev/g)].map(match => match[0]);
  const url = urls.find(value => new URL(value).hostname.endsWith(`.${options['--project']}.pages.dev`));
  if (url) console.log(`Deployment URL: ${url}`);
  if (result.status !== 0 || !url) throw new Error(`Wrangler failed or returned no matching deployment URL (exit ${result.status}); inspect Cloudflare before retrying`);
  let verified = false;
  for (let attempt = 0; attempt < 5; attempt++) {
    try { const response = await fetch(url, { signal: AbortSignal.timeout(15000) }); if (response.status === 200 && hash(Buffer.from(await response.arrayBuffer())) === root.sha256) { verified = true; break; } } catch {}
    if (attempt < 4) await new Promise(done => setTimeout(done, 2000));
  }
  if (!verified) throw new Error(`Deployment exists but exact HTML readback failed: ${url}; do not blindly redeploy`);
  const receipt = { at: new Date().toISOString(), url, project: options['--project'], files: files.length, artifact_sha256: artifact, root_sha256: root.sha256, verification: 'HTTP 200 + exact root HTML hash' };
  await appendFile(handoff, `\nPublish receipt: ${JSON.stringify(receipt)}\n`);
  console.log(JSON.stringify({ verdict: 'published', ...receipt }));
}
