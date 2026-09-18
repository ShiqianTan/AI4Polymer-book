"""Reader-facing CLI. Default calculations are offline and require no GPU."""
import argparse
import inspect
import json
from pathlib import Path
import sys

from .report import markdown
from .schema import read_json_object, to_json
from .sources import verify_sources
from .topics import TOPIC_DESCRIPTIONS, TOPIC_MODULES


def _add_common(topic) -> None:
    topic.add_argument("--inputs", type=Path, help="JSON object of calculate() keyword arguments")
    topic.add_argument("--format", choices=("json", "md"), default="json")
    topic.add_argument("--output", type=Path)


def parser() -> argparse.ArgumentParser:
    command = argparse.ArgumentParser(description=__doc__)
    sub = command.add_subparsers(dest="command", required=True)

    representation = sub.add_parser("descriptor-budget", help=TOPIC_DESCRIPTIONS["descriptor-budget"])
    representation.add_argument("--representation", choices=("morgan", "mordred", "graph", "psmiles"), default="morgan")
    representation.add_argument("--n-bits", type=int, default=2048)
    representation.add_argument("--radius", type=int, default=2)
    representation.add_argument("--atoms", type=int, default=100)
    representation.add_argument("--bonds", type=int, default=105)
    representation.add_argument("--library-size", type=int, default=1000000)
    _add_common(representation)

    space = sub.add_parser("chemical-space", help=TOPIC_DESCRIPTIONS["chemical-space"])
    space.add_argument("--monomers", type=int, default=10)
    space.add_argument("--chain-length", type=int, default=100)
    space.add_argument("--copolymer", choices=("homopolymer", "random", "block", "alternating"), default="random")
    space.add_argument("--stoichiometry", default="1,1")
    _add_common(space)

    md = sub.add_parser("md-cost", help=TOPIC_DESCRIPTIONS["md-cost"])
    md.add_argument("--atoms", type=int, default=5000)
    md.add_argument("--timesteps", type=int, default=1000000)
    md.add_argument("--timestep-fs", type=float, default=1.0)
    md.add_argument("--method", choices=("md-ff", "md-mlff", "dft"), default="md-ff")
    md.add_argument("--device", dest="device_id", default="a100-80gb-sxm")
    md.add_argument("--efficiency", type=float, default=0.3)
    md.add_argument("--gpus", type=int, default=1)
    _add_common(md)

    gnn = sub.add_parser("gnn-forward", help=TOPIC_DESCRIPTIONS["gnn-forward"])
    gnn.add_argument("--layers", type=int, default=4)
    gnn.add_argument("--hidden", type=int, default=256)
    gnn.add_argument("--atoms", type=int, default=100)
    gnn.add_argument("--bonds", type=int, default=105)
    gnn.add_argument("--edge-features", type=int, default=32)
    gnn.add_argument("--heads", type=int, default=8)
    gnn.add_argument("--readout", choices=("sum", "mean", "attention"), default="attention")
    gnn.add_argument("--device", dest="device_id", default="a100-80gb-sxm")
    gnn.add_argument("--efficiency", type=float, default=0.3)
    _add_common(gnn)

    curve = sub.add_parser("learning-curve", help=TOPIC_DESCRIPTIONS["learning-curve"])
    curve.add_argument("--mae-inf", type=float, default=0.05)
    curve.add_argument("--a", type=float, default=1.0)
    curve.add_argument("--alpha", type=float, default=0.5)
    curve.add_argument("--target-mae", type=float, default=0.2)
    curve.add_argument("--n-max", type=int, default=100000)
    curve.add_argument("--strict-mae", type=float, default=0.1)
    _add_common(curve)

    loop = sub.add_parser("closed-loop", help=TOPIC_DESCRIPTIONS["closed-loop"])
    loop.add_argument("--space-size", type=int, default=1000000)
    loop.add_argument("--top-fraction", type=float, default=0.001)
    loop.add_argument("--bo-speedup", type=float, default=5.0)
    loop.add_argument("--experiments-per-day", type=int, default=50)
    _add_common(loop)

    pareto = sub.add_parser("pareto-screen", help=TOPIC_DESCRIPTIONS["pareto-screen"])
    pareto.add_argument("--monomers", type=int, default=10)
    pareto.add_argument("--chain-length", type=int, default=100)
    pareto.add_argument("--reference", type=float, nargs=2, default=(0.0, 0.0))
    pareto.add_argument("--weight-steps", type=int, default=11)
    pareto.add_argument("--epsilon-steps", type=int, default=21)
    _add_common(pareto)

    robust = sub.add_parser("robust-ranking", help=TOPIC_DESCRIPTIONS["robust-ranking"])
    robust.add_argument("--means", type=float, nargs="+", default=(205.0, 205.0))
    robust.add_argument("--half-widths", type=float, nargs="+", default=(20.0, 3.0))
    robust.add_argument("--spec-low", type=float, default=200.0)
    robust.add_argument("--spec-high", type=float, default=210.0)
    _add_common(robust)

    polymerization = sub.add_parser("polymerization", help=TOPIC_DESCRIPTIONS["polymerization"])
    polymerization.add_argument("--step-conversions", default="0.9,0.99,0.999")
    polymerization.add_argument("--living-ratios", default="50,100,200")
    polymerization.add_argument("--living-conversion", type=float, default=0.99)
    polymerization.add_argument("--copolymer-pairs", default="0.1:0.1;1:1;10:0.1;0.1:10")
    polymerization.add_argument("--feed-fraction", type=float, default=0.5)
    polymerization.add_argument("--max-conversion", type=float, default=0.99)
    polymerization.add_argument("--drift-steps", type=int, default=100)
    polymerization.add_argument("--flory-conversion", type=float, default=0.99)
    polymerization.add_argument("--poisson-mean-dp", type=float, default=100)
    polymerization.add_argument("--curve-points", type=int, default=80)
    _add_common(polymerization)

    route = sub.add_parser("synthesis-route", help=TOPIC_DESCRIPTIONS["synthesis-route"])
    route.add_argument("--branching", type=int, default=50)
    route.add_argument("--depth", type=int, default=5)
    route.add_argument("--beam", type=int, default=10)
    route.add_argument("--step-yield", type=float, default=0.8)
    route.add_argument("--target-yield", type=float, default=0.3)
    route.add_argument("--initial-candidates", type=int, default=8910)
    route.add_argument("--feasibility", type=float, default=0.6)
    route.add_argument("--route-length-pass", type=float, default=0.6)
    route.add_argument("--yield-pass", type=float, default=0.5)
    route.add_argument("--cost-pass", type=float, default=0.4)
    _add_common(route)

    variants = sub.add_parser("bo-variants", help=TOPIC_DESCRIPTIONS["bo-variants"])
    variants.add_argument("--space-size", type=int, default=1000000)
    variants.add_argument("--top-fraction", type=float, default=0.001)
    variants.add_argument("--batch-size", type=int, default=8)
    variants.add_argument("--batch-correlation", type=float, default=0.5)
    variants.add_argument("--feasible-fraction", type=float, default=0.3)
    variants.add_argument("--fidelity-cost-ratio", type=float, default=0.05)
    variants.add_argument("--screening-pass-fraction", type=float, default=0.2)
    variants.add_argument("--expensive-cost-ratio", type=float, default=20.0)
    variants.add_argument("--budget", type=int, default=1000)
    _add_common(variants)

    for admin_name, admin_help in (("models", "List registered topics and their default inputs"),
                                   ("verify-sources", "Check configs against sources.lock.json"),
                                   ("verify-results", "Check generated results are current")):
        admin = sub.add_parser(admin_name, help=admin_help)
        admin.add_argument("--format", choices=("json", "md"), default="json")
        admin.add_argument("--output", type=Path)
    reproduce = sub.add_parser("reproduce", help="Regenerate all fixed scenarios and results/README.md")
    reproduce.add_argument("--format", choices=("json", "md"), default="json")
    reproduce.add_argument("--output", type=Path)
    return command


def topic_list() -> dict:
    topics = []
    for name, module, description in ((name, TOPIC_MODULES[name], TOPIC_DESCRIPTIONS[name])
                                      for name in TOPIC_MODULES):
        signature = inspect.signature(module.calculate)
        defaults = {parameter.name: parameter.default for parameter in signature.parameters.values()
                    if parameter.default is not inspect.Parameter.empty}
        topics.append({"topic": name, "description": description,
                       "defaults": defaults,
                       "calculation": (inspect.getdoc(module.calculate) or description).splitlines()[0]})
    return {"command": "models", "count": len(topics), "topics": topics}


def _calculate_from_json_inputs(calculate, path: Path):
    payload = read_json_object(path)
    signature = inspect.signature(calculate)
    try:
        signature.bind(**payload)
    except TypeError as error:
        raise ValueError(f"--inputs {path}: {error}") from error
    return calculate(**payload)


def _admin_markdown(payload: dict) -> str:
    lines = [f"# {payload.get('command', 'report')}", ""]
    for key, value in payload.items():
        if key == "command":
            continue
        lines.extend([f"## {key}", "", "```json",
                      json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False), "```", ""])
    return "\n".join(lines)


def _admin_text(payload: dict, fmt: str) -> str:
    if fmt == "md":
        return _admin_markdown(payload)
    return json.dumps(payload, ensure_ascii=False, indent=2, allow_nan=False) + "\n"


def main(argv: list[str] | None = None) -> None:
    command = parser()
    args = command.parse_args(argv)
    try:
        if args.command == "models":
            text = _admin_text(topic_list(), args.format)
        elif args.command == "verify-sources":
            text = _admin_text({"command": "verify-sources", **verify_sources()}, args.format)
        elif args.command == "reproduce":
            from .reproduce import run
            text = _admin_text({"command": "reproduce", **run()}, args.format)
        elif args.command == "verify-results":
            from .reproduce import verify_results
            text = _admin_text({"command": "verify-results", **verify_results()}, args.format)
        else:
            module = TOPIC_MODULES[args.command]
            if getattr(args, "inputs", None) is not None:
                payload = _calculate_from_json_inputs(module.calculate, args.inputs)
            else:
                kwargs = {key: value for key, value in vars(args).items()
                          if key not in ("command", "format", "output", "inputs")}
                payload = module.calculate(**kwargs)
            text = markdown(payload) if args.format == "md" else to_json(payload)
        output = getattr(args, "output", None)
        if output:
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(text, encoding="utf-8")
        else:
            sys.stdout.write(text)
    except (ValueError, KeyError, OSError) as error:
        command.error(str(error))
