from functions import *
from graphviz import Digraph

DEFAULT_OUTPUT_NAME = "minimax_tree"

memo = {}

def board_key(board):
    """Convert board into a tuple-of-tuples for hashing."""
    return tuple(tuple(row) for row in board)

def build_graphviz(node, graph=None):
    if graph is None:
        graph = Digraph(format='png', encoding='utf-8')
        graph.attr(rankdir="TB")  # top → bottom tree

    # Unique id for node
    nid = id(node)

    label = f"{round(node.score, 3)}"
    color = "lightblue" if node.player == 2 else "lightcoral"

    graph.node(str(nid), label=label, style="filled", fillcolor=color)

    for child in node.children:
        cid = id(child)
        graph.edge(str(nid), str(cid))
        build_graphviz(child, graph)

    return graph

def write_tree_to_file(root, filename="minimax_tree.txt"):
    """Write the minimax tree to a text file in a readable hierarchical format."""
    with open(filename, "w") as f:
        def recurse(node, indent=0):
            prefix = "    " * indent
            line = (
                f"{prefix}- Depth {node.depth} | "
                f"Player {node.player} | "
                f"Move {node.move} | "
                f"Score {node.score}"
            )
            f.write(line + "\n")
            for child in node.children:
                recurse(child, indent + 1)

        recurse(root)
        
def minimax_with_tree(board, depth, maximizing_player, current_depth=0):
    valid_moves = get_moves(board)
    key = (board_key(board),depth,maximizing_player)
    # Create a node for this state
    node = TreeNode(
        move=None,
        player=2 if maximizing_player else 1,
        depth=current_depth
    )
    if key in memo:
        node.score = memo[key]
        return node , node.score, None
    if depth == 0 or is_terminal(board):
        node.score = heurestic(board)
        return node, node.score, None

    if maximizing_player:
        max_eval = float('-inf')
        best_move = None

        for col in valid_moves:
            new_board = drop_piece(board, col, 2)
            child_node, eval_score, _ = minimax_with_tree(
                new_board, depth-1, False, current_depth+1
            )
            child_node.move = col

            node.children.append(child_node)

            if eval_score > max_eval:
                max_eval = eval_score
                best_move = col

        node.score = max_eval
        return node, max_eval, best_move

    else:
        min_eval = float('inf')
        best_move = None

        for col in valid_moves:
            new_board = drop_piece(board, col, 1)
            child_node, eval_score, _ = minimax_with_tree(
                new_board, depth-1, True, current_depth+1
            )
            child_node.move = col

            node.children.append(child_node)

            if eval_score < min_eval:
                min_eval = eval_score
                best_move = col

        node.score = min_eval
        return node, min_eval, best_move
class TreeNode:
    def __init__(self, move=None, player=None, score=None, depth=0):
        self.move = move          # which column was played
        self.player = player      # 1 or 2
        self.score = score        # heuristic score at this node
        self.depth = depth        # depth in the tree
        self.children = []        # list of TreeNode
