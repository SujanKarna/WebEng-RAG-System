def print_tree(node, level=0):

    indent = "    " * level


    print(
        indent
        + f"{node.node_type}: {node.title}"
    )


    for child in node.children:

        print_tree(
            child,
            level + 1
        )