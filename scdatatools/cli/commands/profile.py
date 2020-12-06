import io
import json
from pathlib import Path

from nubia import command, argument

from scdatatools.sc import StarCitizen


@command(help="Dumps the default profile action map (keybinds) as JSON")
@argument("scdir", description="StarCitizen Game Folder")
@argument("csv", description="Output as a CSV instead", aliases=["-c"])
def actionmap(
        scdir: Path,
        csv: bool = False,
):
    sc = StarCitizen(scdir)
    am = sc.default_profile.actionmap()

    if csv:
        out = io.StringIO()
        sc.default_profile.dump_actionmap_csv(out)
        print(out.getvalue())
    else:
        print(json.dumps(am, indent=4))
