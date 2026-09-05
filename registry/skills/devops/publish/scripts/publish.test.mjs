import { test } from 'node:test';
import assert from 'node:assert/strict';
import { mkdtemp, mkdir, writeFile, symlink, readFile, rm } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
test('public preflight accepts static assets and fails closed at publication boundaries', async () => {
  const root = await mkdtemp(join(tmpdir(), 'publish-test-'));
  const input = join(root, 'site'), handoff = join(root, 'handoff.md');
  await mkdir(input); await writeFile(join(input, 'index.html'), '<!doctype html><title>Public fixture</title>'); await writeFile(handoff, 'preserve');
  const run = (extra = [], publicFlag = true) => spawnSync(process.execPath, [fileURLToPath(new URL('./publish.mjs', import.meta.url)), '--input', input, '--project', 'fixture', '--handoff', handoff, '--wrangler', 'unused.js', '--dry-run', ...(publicFlag ? ['--public'] : []), ...extra], { encoding: 'utf8' });
  try {
    assert.equal(run().status, 0);
    assert.notEqual(run([], false).status, 0);
    assert.notEqual(run(['--handoff', join(input, 'handoff.md')]).status, 0);
    await symlink(handoff, join(input, 'linked.txt')); assert.notEqual(run().status, 0); await rm(join(input, 'linked.txt'));
    await writeFile(join(input, 'package.json'), '{}'); assert.notEqual(run().status, 0); await rm(join(input, 'package.json'));
    await writeFile(join(input, 'note.txt'), '/' + 'Users/' + 'fixture/private'); assert.notEqual(run().status, 0);
    assert.equal(await readFile(handoff, 'utf8'), 'preserve');
  } finally { await rm(root, { recursive: true }); }
});
