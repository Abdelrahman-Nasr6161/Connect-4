from functions import *
from graphviz import Digraph
DEFAULT_OUTPUT_NAME = "expected-minimax"

memo = {}

def board_key(board):
    """Convert board into a tuple-of-tuples for hashing."""
    return tuple(tuple(row) for row in board)

def expected_minimax_with_tree(board, depth, maximizing_player, current_depth=0):
    valid_moves = get_moves(board)
    key = (board_key(board), depth, maximizing_player)

    # Create decision node for this state
    node = TreeNode(
        move=None,
        player=2 if maximizing_player else 1,
        depth=current_depth
    )

    # ✔️ Memoized return
    if key in memo:
        node.score = memo[key]
        return node, node.score, None

    # Terminal condition
    if depth == 0 or is_terminal(board) or not valid_moves:
        node.score = heurestic(board)
        memo[key] = node.score
        return node, node.score, None

    if maximizing_player:
        max_eval = float('-inf')
        best_move = None

        for move in valid_moves:
            chance_node = TreeNode(
                move=move,
                player=2,
                depth=current_depth,
                probability=1.0
            )

            expected_score = 0
            neighbors = [n for n in (move-1, move+1) if n in valid_moves]

            if len(neighbors) == 2:
                outcomes = [(move, 0.6), (neighbors[0], 0.2), (neighbors[1], 0.2)]
            elif len(neighbors) == 1:
                outcomes = [(move, 0.6), (neighbors[0], 0.4)]
            else:
                outcomes = [(move, 1.0)]

            for actual_move, prob in outcomes:
                new_board = drop_piece(board, actual_move, 2)
                child_node, score, _ = expected_minimax_with_tree(
                    new_board, depth-1, False, current_depth+1
                )

                child_node.move = actual_move
                child_node.probability = prob
                chance_node.children.append(child_node)

                expected_score += prob * score

            chance_node.score = expected_score
            node.children.append(chance_node)

            if expected_score > max_eval:
                max_eval = expected_score
                best_move = move

        node.score = max_eval
        memo[key] = max_eval
        return node, max_eval, best_move

    # ---------------- MINIMIZING PLAYER ----------------
    else:
        min_eval = float('inf')
        best_move = None

        for move in valid_moves:
            chance_node = TreeNode(
                move=move,
                player=1,
                depth=current_depth,
                probability=1.0
            )

            expected_score = 0
            neighbors = [n for n in (move-1, move+1) if n in valid_moves]

            if len(neighbors) == 2:
                outcomes = [(move, 0.6), (neighbors[0], 0.2), (neighbors[1], 0.2)]
            elif len(neighbors) == 1:
                outcomes = [(move, 0.6), (neighbors[0], 0.4)]
            else:
                outcomes = [(move, 1.0)]

            for actual_move, prob in outcomes:
                new_board = drop_piece(board, actual_move, 1)
                child_node, score, _ = expected_minimax_with_tree(
                    new_board, depth-1, True, current_depth+1
                )

                child_node.move = actual_move
                child_node.probability = prob
                chance_node.children.append(child_node)

                expected_score += prob * score

            chance_node.score = expected_score
            node.children.append(chance_node)

            if expected_score < min_eval:
                min_eval = expected_score
                best_move = move

        node.score = min_eval
        memo[key] = min_eval
        return node, min_eval, best_move


class TreeNode:
    def __init__(self, move=None, player=None, score=None, depth=0, probability=None):
        self.move = move
        self.player = player
        self.score = score
        self.depth = depth
        self.probability = probability
        self.children = []


def build_graphviz(node, graph=None):
    if graph is None:
        graph = Digraph(format='png')
        graph.attr(rankdir="TB")

    nid = id(node)
    label = f"{round(node.score,3)}"
    if node.probability is not None:
        label += f"\nP={node.probability:.2f}"

    if node.probability == 1 and node.children:
        color = "yellow"
    else:
        color = "lightblue" if node.player == 2 else "lightcoral"

    graph.node(str(nid), label=label, style="filled", fillcolor=color)

    for child in node.children:
        cid = id(child)
        graph.edge(str(nid), str(cid))
        build_graphviz(child, graph)

    return graph


def write_tree_to_file(root, filename="minimax_tree.txt"):
    with open(filename, "w") as f:
        def recurse(node, indent=0):
            prefix = "    " * indent
            line = (
                f"{prefix}- Depth {node.depth} | "
                f"Player {node.player} | "
                f"Move {node.move} | "
                f"Score {node.score}"
            )
            if node.probability == 1:
                line += f" | Chance Node"

            f.write(line + "\n")

            for child in node.children:
                recurse(child, indent + 1)

        recurse(root)