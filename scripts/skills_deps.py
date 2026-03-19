import json
from pathlib import Path
from collections import defaultdict, deque

class SkillDeps:
    def __init__(self, registry_path):
        with open(registry_path) as f:
            self.registry = json.load(f)
        self.skills = {s['skill_id']: s for s in self.registry['skills']}
        self.graph = self._build_graph()

    def _build_graph(self):
        """Build adjacency list: skill_id -> [dependency_ids]"""
        g = defaultdict(list)
        for s in self.registry['skills']:
            deps = s.get('dependencies', {}).get('skills', [])
            for dep in deps:
                g[s['skill_id']].append(dep)
        return g

    def get_install_order(self, skill_id):
        """Return list of skill_ids in topological install order. Raises if cycle."""
        visited = set()
        order = []

        def dfs(node):
            if node in visited:
                return
            visited.add(node)
            if node not in self.graph:
                # skill exists in registry but has no deps - it's a leaf
                order.append(node)
                return
            for dep in self.graph[node]:
                if dep not in self.skills:
                    raise ValueError(f"Skill '{skill_id}' depends on unknown skill '{dep}'")
                dfs(dep)
            order.append(node)

        dfs(skill_id)
        return order

    def detect_cycles(self):
        """Return list of cycles found. Empty if no cycles."""
        visited = set()
        rec_stack = set()
        cycles = []

        def dfs(node, path):
            visited.add(node)
            rec_stack.add(node)
            path.append(node)

            for dep in self.graph.get(node, []):
                if dep not in visited:
                    dfs(dep, path[:])
                elif dep in rec_stack:
                    cycle_start = path.index(dep)
                    cycles.append(path[cycle_start:] + [dep])

            rec_stack.remove(node)

        for skill_id in self.skills:
            if skill_id not in visited:
                dfs(skill_id, [])

        return cycles

    def detect_diamond_deps(self, skill_id):
        """Check if skill has diamond dependencies (A->B, A->C, B->D, C->D)."""
        install_order = self.get_install_order(skill_id)
        # Simple check: if same dep appears via multiple paths
        order_idx = {s: i for i, s in enumerate(install_order)}
        deps_seen = {}
        diamonds = []

        def check(node, ancestors):
            for dep in self.graph.get(node, []):
                for anc in ancestors:
                    if anc in deps_seen and deps_seen[anc] != dep:
                        diamonds.append((anc, dep, node))
                    deps_seen[dep] = anc
                check(dep, ancestors + [dep])

        check(skill_id, [])
        return diamonds

    def resolve_all(self, skill_id):
        """Return dict with install_order, cycles, diamonds for a skill."""
        cycles = self.detect_cycles()
        diamonds = self.detect_diamond_deps(skill_id)
        try:
            order = self.get_install_order(skill_id)
        except ValueError as e:
            order = str(e)
        return {
            'skill_id': skill_id,
            'install_order': order,
            'cycles': cycles,
            'diamonds': diamonds
        }