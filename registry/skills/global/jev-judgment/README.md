# Jev judgment skill

Jev is an optional, conservative second opinion for an agent. It helps check
intent, completion evidence, progress, route or skill selection, bounded Camofox
navigation, and shadow context relevance. It does not run the task, grant
permissions, spawn workers, or install hooks.

This first public release is **v1.3.0**, MIT licensed by SISO. It was promoted
from the [SISO Skills Hub](https://github.com/sisodias/siso-skills-hub). The pack
uses only Python 3.10+ standard-library modules and makes no API calls in
dry-run mode.

## Install one copy

Choose the skill directory used by your agent. The default Codex install is:

```sh
git clone --branch v1.3.0 --depth 1 https://github.com/sisodias/jev-agent-skills.git ~/.codex/skills/jev-judgment
```

For Claude, use `~/.claude/skills/jev-judgment`; for a shared SISO agent
installation, use `~/.agents/skills/jev-judgment`. Pick one target for the
agent you are configuring; do not install three duplicate copies automatically.

Supply your own OpenRouter key as `OPENROUTER_API_KEY` in the agent's process
environment. No credential is included in this repository. An existing
`~/.config/siso/.env` with that variable remains optional compatibility. Never
put a key in a packet, example, shell history, or repository.

An agent must load this directory's `SKILL.md` when it chooses to use Jev. The
pack does not promise automatic skill activation or install hooks.

## Dry-run first

Validate packets without a paid provider call or browser call:

```sh
cd ~/.codex/skills/jev-judgment
python3 harness.py intent examples/intent.json --dry-run
python3 harness.py complete examples/completion.json --dry-run
python3 context.py examples/context.json --dry-run
python3 browser_loop.py examples/browser-loop.json --dry-run
```

Then make an explicit live invocation after reviewing the packet and the
provider/data boundary:

```sh
python3 harness.py intent examples/intent.json
```

The other checks are selected explicitly in the same way: `progress`, `route`,
or `select` through `harness.py`; `browser.py` for one observed link; and
`browser_loop.py` for bounded fill/click/link navigation.

The browser adapters require an existing Camofox service and caller-owned tab;
all other checks work without Camofox. Browser packets use narrow permitted URL
prefixes and never turn a model result into broad browser authority.

## What to expect

Jev scores are advisory and are not calibrated truth. Missing evidence keeps a
completion result incomplete; uncertainty or provider failure falls back to the
calling agent's normal workflow. Shadow context suggestions never delete or
rewrite source context. The advisory checks do not spawn workers, change
permissions or declare the overall task complete. When explicitly invoked, the
browser adapters execute the caller-permitted actions. Browser success means
only that the requested observation was seen. There is no
guaranteed 10x speed or cost improvement.

Read the [packet examples](references/packets.md), [browser limits](references/browser.md),
and [research notes](references/research.md) before using a mode.

## Verification

The standalone pack has 51 offline unittest cases covering validation,
uncertainty, safety boundaries, browser freshness and bounded behavior. The
browser-loop fixture also covers a synthetic three-action search flow. Run:

```sh
python3 -B -m unittest discover -s tests -p 'test_*.py'
```

The tests use no provider credentials and no live browser.
