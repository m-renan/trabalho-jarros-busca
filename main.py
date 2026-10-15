#!/usr/bin/env python3
"""
Problema dos Jarros d'Água (4 L e 3 L)
Busca em largura (BFS), busca em profundidade (DFS) e aprofundamento iterativo (IDDFS).

Estado: (x, y), em que x é a quantidade no jarro de 4 L e y no jarro de 3 L.
O programa aceita um estado inicial pela linha de comando ou solicita os valores.
"""
from __future__ import annotations

import argparse
from collections import deque
from dataclasses import dataclass
from time import perf_counter
from typing import Optional

CAP_A = 4
CAP_B = 3
State = tuple[int, int]


@dataclass
class SearchResult:
    algorithm: str
    path: list[State] | None
    actions: list[str]
    tree_parent: dict[State, Optional[State]]
    tree_action: dict[State, str]
    expanded: int
    generated: int
    elapsed_ms: float
    depth_limit: int | None = None


def is_goal(state: State) -> bool:
    return state[0] == 2 or state[1] == 2


def successors(state: State) -> list[tuple[State, str]]:
    """Retorna estados alcançáveis por uma única ação, sem transições sem efeito."""
    a, b = state
    out: list[tuple[State, str]] = []

    candidates = [
        ((CAP_A, b), "Encher o jarro de 4 L"),
        ((a, CAP_B), "Encher o jarro de 3 L"),
        ((0, b), "Esvaziar o jarro de 4 L"),
        ((a, 0), "Esvaziar o jarro de 3 L"),
    ]

    # Transferir do jarro A (4 L) para B (3 L)
    amount = min(a, CAP_B - b)
    candidates.append(((a - amount, b + amount), "Transferir do jarro de 4 L para o de 3 L"))
    # Transferir do jarro B (3 L) para A (4 L)
    amount = min(b, CAP_A - a)
    candidates.append(((a + amount, b - amount), "Transferir do jarro de 3 L para o de 4 L"))

    seen: set[State] = set()
    for nxt, action in candidates:
        if nxt != state and nxt not in seen:
            out.append((nxt, action))
            seen.add(nxt)
    return out


def reconstruct(goal: State, parent: dict[State, Optional[State]],
                via: dict[State, str]) -> tuple[list[State], list[str]]:
    path = [goal]
    actions: list[str] = []
    current = goal
    while parent[current] is not None:
        actions.append(via[current])
        current = parent[current]  # type: ignore[assignment]
        path.append(current)
    path.reverse()
    actions.reverse()
    return path, actions


def bfs(start: State) -> SearchResult:
    t0 = perf_counter()
    queue = deque([start])
    parent: dict[State, Optional[State]] = {start: None}
    via: dict[State, str] = {}
    expanded = 0
    generated = 1
    goal: State | None = start if is_goal(start) else None

    while queue and goal is None:
        state = queue.popleft()
        expanded += 1
        for nxt, action in successors(state):
            if nxt in parent:
                continue
            parent[nxt] = state
            via[nxt] = action
            generated += 1
            if is_goal(nxt):
                goal = nxt
                break
            queue.append(nxt)

    elapsed = (perf_counter() - t0) * 1000
    path, actions = reconstruct(goal, parent, via) if goal is not None else (None, [])
    return SearchResult("Busca em largura (BFS)", path, actions, parent, via,
                        expanded, generated, elapsed)


def dfs(start: State) -> SearchResult:
    t0 = perf_counter()
    stack = [start]
    parent: dict[State, Optional[State]] = {start: None}
    via: dict[State, str] = {}
    expanded = 0
    generated = 1
    goal: State | None = start if is_goal(start) else None

    while stack and goal is None:
        state = stack.pop()
        expanded += 1
        # Reversed so that the first listed action is explored first.
        for nxt, action in reversed(successors(state)):
            if nxt in parent:
                continue
            parent[nxt] = state
            via[nxt] = action
            generated += 1
            if is_goal(nxt):
                goal = nxt
                break
            stack.append(nxt)

    elapsed = (perf_counter() - t0) * 1000
    path, actions = reconstruct(goal, parent, via) if goal is not None else (None, [])
    return SearchResult("Busca em profundidade (DFS)", path, actions, parent, via,
                        expanded, generated, elapsed)


def depth_limited(start: State, limit: int) -> tuple[
        State | None, dict[State, Optional[State]], dict[State, str], int, int]:
    """Busca em profundidade limitada; evita ciclos no caminho atual."""
    parent: dict[State, Optional[State]] = {start: None}
    via: dict[State, str] = {}
    expanded = 0
    generated = 1
    goal: State | None = start if is_goal(start) else None
    path_states = {start}

    def visit(state: State, depth: int) -> State | None:
        nonlocal expanded, generated, goal
        if is_goal(state):
            return state
        if depth >= limit:
            return None
        expanded += 1
        for nxt, action in successors(state):
            if nxt in path_states:
                continue
            parent[nxt] = state
            via[nxt] = action
            generated += 1
            path_states.add(nxt)
            found = visit(nxt, depth + 1)
            if found is not None:
                return found
            path_states.remove(nxt)
            # Remove abandoned branch from the displayed tree.
            parent.pop(nxt, None)
            via.pop(nxt, None)
        return None

    goal = visit(start, 0)
    return goal, parent, via, expanded, generated


def iddfs(start: State) -> SearchResult:
    t0 = perf_counter()
    total_expanded = 0
    total_generated = 0
    final_parent: dict[State, Optional[State]] = {start: None}
    final_via: dict[State, str] = {}
    found: State | None = None
    found_limit = 0

    # O espaço de estados é finito; uma solução para este problema existe a partir
    # de qualquer estado válido, e 20 é um limite de segurança acima do necessário.
    for limit in range(0, 21):
        goal, parent, via, expanded, generated = depth_limited(start, limit)
        total_expanded += expanded
        total_generated += generated
        final_parent, final_via = parent, via
        if goal is not None:
            found = goal
            found_limit = limit
            break

    elapsed = (perf_counter() - t0) * 1000
    path, actions = reconstruct(found, final_parent, final_via) if found is not None else (None, [])
    return SearchResult("Aprofundamento iterativo (IDDFS)", path, actions,
                        final_parent, final_via, total_expanded, total_generated,
                        elapsed, found_limit)


def print_tree(result: SearchResult, start: State) -> None:
    """Mostra a árvore de busca armazenada, destacando os estados do caminho final."""
    print("\nÁRVORE DE BUSCA ( * indica o caminho da solução )")
    path_set = set(result.path or [])
    children: dict[State, list[State]] = {s: [] for s in result.tree_parent}
    for state, parent in result.tree_parent.items():
        if parent is not None:
            children.setdefault(parent, []).append(state)

    def visit(state: State, prefix: str = "", is_last: bool = True, root: bool = False) -> None:
        mark = "*" if state in path_set else " "
        print(f"{prefix}{'' if root else ('└── ' if is_last else '├── ')}{mark} {state}")
        kids = children.get(state, [])
        for i, child in enumerate(kids):
            action = result.tree_action.get(child, "")
            child_prefix = prefix + ("" if root else ("    " if is_last else "│   "))
            print(f"{child_prefix}{'    ' if i == len(kids)-1 else '│   '}[{action}]")
            visit(child, child_prefix, i == len(kids)-1)

    visit(start, root=True)


def run_all(start: State) -> None:
    algorithms = [bfs, dfs, iddfs]
    results = [algorithm(start) for algorithm in algorithms]

    print(f"\nEstado inicial: {start}  (jarro 4 L, jarro 3 L)")
    print("Objetivo: obter exatamente 2 litros em pelo menos um dos jarros.")
    for result in results:
        print("\n" + "=" * 68)
        print(result.algorithm)
        if result.path is None:
            print("Nenhuma solução encontrada.")
        else:
            print(f"Estados no caminho: {len(result.path)}")
            print(f"Passos/ações: {len(result.actions)}")
            for i, state in enumerate(result.path):
                if i == 0:
                    print(f"  {i}. Estado inicial: {state}")
                else:
                    print(f"  {i}. {result.actions[i-1]} -> {state}")
            print(f"Profundidade limite (IDDFS): {result.depth_limit}"
                  if result.depth_limit is not None else "")
        print(f"Nós expandidos: {result.expanded}")
        print(f"Nós gerados: {result.generated}")
        print(f"Tempo de execução: {result.elapsed_ms:.4f} ms")
        print_tree(result, start)

    print("\n" + "=" * 68)
    print("RESUMO COMPARATIVO")
    print(f"{'Algoritmo':34} {'Ações':>7} {'Expandidos':>11} {'Gerados':>9} {'Tempo (ms)':>12}")
    for r in results:
        steps = len(r.actions) if r.path is not None else -1
        print(f"{r.algorithm:34} {steps:>7} {r.expanded:>11} {r.generated:>9} {r.elapsed_ms:>12.4f}")
    print("\nObservação: tempos variam conforme o computador e a execução.")


def parse_state(args: argparse.Namespace) -> State:
    if args.quatro is None or args.tres is None:
        try:
            a = int(input("Quantidade inicial no jarro de 4 L (0 a 4): "))
            b = int(input("Quantidade inicial no jarro de 3 L (0 a 3): "))
        except ValueError as exc:
            raise SystemExit("Erro: informe quantidades inteiras.") from exc
    else:
        a, b = args.quatro, args.tres
    if not (0 <= a <= CAP_A and 0 <= b <= CAP_B):
        raise SystemExit("Erro: estado inválido. Use 0<=jarro de 4 L<=4 e 0<=jarro de 3 L<=3.")
    return a, b


def main() -> None:
    parser = argparse.ArgumentParser(description="Resolve o problema dos jarros com BFS, DFS e IDDFS.")
    parser.add_argument("--quatro", type=int, help="quantidade inicial no jarro de 4 L (0 a 4)")
    parser.add_argument("--tres", type=int, help="quantidade inicial no jarro de 3 L (0 a 3)")
    args = parser.parse_args()
    start = parse_state(args)
    run_all(start)


if __name__ == "__main__":
    main()
