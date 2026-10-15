# Problema dos Jarros d’Água — Algoritmos de Busca

Implementação em Python para o trabalho de Inteligência Artificial: resolver o problema dos jarros de 4 L e 3 L usando **busca em largura (BFS)**, **busca em profundidade (DFS)** e **busca com aprofundamento iterativo (IDDFS)**.

## Requisitos

- Python 3.10 ou superior
- Nenhuma biblioteca externa

## Como executar

No terminal, dentro da pasta do projeto:

```bash
python main.py
```

O programa solicitará o estado inicial dos jarros. Para informar o estado pela linha de comando:

```bash
python main.py --quatro 0 --tres 0
```

`--quatro` deve estar entre 0 e 4; `--tres`, entre 0 e 3.

## Modelagem do problema

- **Estado:** `(x, y)`, onde `x` é a quantidade de água no jarro de 4 L e `y` a quantidade no jarro de 3 L.
- **Estado inicial padrão:** `(0, 0)`, os dois jarros vazios.
- **Teste de objetivo:** `x == 2` ou `y == 2`.
- **Ações:** encher cada jarro; esvaziar cada jarro; transferir água de um jarro para o outro até que a origem fique vazia ou o destino fique cheio.
- **Restrições:** `0 ≤ x ≤ 4` e `0 ≤ y ≤ 3`. Transições que não alteram o estado são descartadas.

## Saída

Para cada algoritmo, o programa apresenta:
- caminho encontrado, com a ação entre cada estado;
- árvore de busca armazenada, com `*` destacando os estados do caminho da solução;
- número de ações, nós expandidos, nós gerados e tempo de execução;
- resumo comparativo dos três algoritmos.

Os tempos são medidos durante a execução e podem variar de uma máquina para outra. O BFS encontra uma solução com o menor número de ações quando cada ação tem custo unitário. O DFS não garante o caminho mais curto. O IDDFS executa buscas com limites de profundidade crescentes.

## Estrutura

- `main.py` — implementação dos três algoritmos e visualização textual da árvore.
- `relatorio.md` — relatório do trabalho, com formalização e análise comparativa.
- `.gitignore` — arquivos que não precisam ser enviados ao GitHub.

## Enviar ao GitHub

1. Crie um repositório no GitHub (por exemplo, `trabalho-jarros-busca`).
2. Abra um terminal nesta pasta.
3. Execute:

```bash
git init
git add main.py relatorio.md README.md .gitignore
git commit -m "Implementa busca para o problema dos jarros"
git branch -M main
git remote add origin https://github.com/SEU-USUARIO/SEU-REPOSITORIO.git
git push -u origin main
```

Substitua a URL de exemplo pela URL real do seu repositório. Se o Git pedir identificação, configure `user.name` e `user.email`. Nunca compartilhe sua senha ou token no código.
