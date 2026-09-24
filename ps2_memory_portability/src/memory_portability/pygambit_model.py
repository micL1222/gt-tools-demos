"""Optional PyGambit representation of the memory-portability Bayesian game."""

from __future__ import annotations

from pathlib import Path

from .model import Action, CostType, ModelParameters, payoff


class PyGambitUnavailable(RuntimeError):
    """Raised when the optional PyGambit dependency cannot be imported."""


def import_pygambit():
    """Import PyGambit without making the authoritative direct model depend on it."""

    try:
        import pygambit as gb
    except (ImportError, OSError) as error:
        raise PyGambitUnavailable(f"PyGambit is unavailable: {error}") from error
    return gb


def pygambit_availability() -> tuple[bool, str]:
    """Return whether PyGambit imports and a readable status message."""

    try:
        gb = import_pygambit()
    except PyGambitUnavailable as error:
        return False, str(error)
    return True, f"PyGambit {getattr(gb, '__version__', 'version unavailable')} imported"


def build_game(parameters: ModelParameters):
    """Build the four-state Harsanyi game with simultaneous actions.

    Nature selects the joint type.  Platform A's two information sets reveal
    only A's own type.  Platform B's two information sets reveal only B's own
    type and connect nodes following both A actions, so B does not observe A's
    simultaneous choice.
    """

    if not parameters.has_full_support:
        raise ValueError("The PyGambit cross-check requires 0 < p_low < 1.")
    gb = import_pygambit()
    game = gb.Game.new_tree(
        players=["Platform A", "Platform B"],
        title="Stay or Switch? Bayesian memory portability",
    )
    joint_labels = ["Low, Low", "Low, High", "High, Low", "High, High"]
    game.append_move(game.root, game.players.chance, joint_labels)
    game.root.infoset.label = "Nature: joint cost types"
    p = gb.Rational(str(parameters.p_low))
    one_minus_p = 1 - p
    game.set_chance_probs(
        game.root.infoset,
        [p * p, p * one_minus_p, one_minus_p * p, one_minus_p * one_minus_p],
    )
    type_nodes = list(game.root.children)

    # A observes A's type, not B's type.
    game.append_move(type_nodes[0:2], "Platform A", ["Portable", "Locked"])
    type_nodes[0].infoset.label = "Platform A: low"
    game.append_move(type_nodes[2:4], "Platform A", ["Portable", "Locked"])
    type_nodes[2].infoset.label = "Platform A: high"

    # B observes B's type, but neither A's type nor A's simultaneous action.
    b_low_nodes = [
        action_node
        for state_index in (0, 2)
        for action_node in type_nodes[state_index].children
    ]
    b_high_nodes = [
        action_node
        for state_index in (1, 3)
        for action_node in type_nodes[state_index].children
    ]
    game.append_move(b_low_nodes, "Platform B", ["Portable", "Locked"])
    b_low_nodes[0].infoset.label = "Platform B: low"
    game.append_move(b_high_nodes, "Platform B", ["Portable", "Locked"])
    b_high_nodes[0].infoset.label = "Platform B: high"

    joint_types = [
        (CostType.LOW, CostType.LOW),
        (CostType.LOW, CostType.HIGH),
        (CostType.HIGH, CostType.LOW),
        (CostType.HIGH, CostType.HIGH),
    ]
    actions = [Action.PORTABLE, Action.LOCKED]
    for type_node, (type_a, type_b) in zip(type_nodes, joint_types):
        for action_a, b_node in zip(actions, type_node.children):
            for action_b, leaf in zip(actions, b_node.children):
                payoffs = [
                    payoff(action_a, action_b, parameters.cost(type_a)),
                    payoff(action_b, action_a, parameters.cost(type_b)),
                ]
                label = (
                    f"A {type_a.value}/{action_a.value}; "
                    f"B {type_b.value}/{action_b.value}"
                )
                game.set_outcome(
                    leaf,
                    game.add_outcome(label=label, payoffs=payoffs),
                )
    return game


def enumerate_pure_bne_pygambit(parameters: ModelParameters) -> list[tuple[str, str]]:
    """Enumerate PyGambit pure equilibria and translate them to LL/PL/LP/PP."""

    gb = import_pygambit()
    game = build_game(parameters)
    infosets = {infoset.label: infoset for infoset in game.infosets}
    profiles: set[tuple[str, str]] = set()
    for equilibrium in gb.nash.enumpure_solve(game).equilibria:
        behavior = equilibrium.as_behavior()
        strategy_a = _strategy_from_behavior(
            behavior,
            infosets["Platform A: low"],
            infosets["Platform A: high"],
        )
        strategy_b = _strategy_from_behavior(
            behavior,
            infosets["Platform B: low"],
            infosets["Platform B: high"],
        )
        profiles.add((strategy_a, strategy_b))
    return sorted(profiles)


def export_efg(parameters: ModelParameters, path: Path) -> Path:
    """Export the actual benchmark game in Gambit EFG format."""

    game = build_game(parameters)
    path.parent.mkdir(parents=True, exist_ok=True)
    game.to_efg(path)
    return path


def _strategy_from_behavior(behavior, low_infoset, high_infoset) -> str:
    def selected(infoset) -> str:
        chosen = [action for action in infoset.actions if float(behavior[action]) > 0.5]
        if len(chosen) != 1:
            raise RuntimeError("Expected a pure action at every type information set.")
        return "P" if chosen[0].label == "Portable" else "L"

    return selected(low_infoset) + selected(high_infoset)
