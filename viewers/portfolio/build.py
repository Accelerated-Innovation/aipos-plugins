"""Package dependency-free viewer assets. Run from any directory; --check detects drift."""
from pathlib import Path
import argparse
ROOT=Path(__file__).resolve().parents[2]
SOURCE=Path(__file__).resolve().parent
DEST=ROOT/'plugins/aipos/skills/aipos-portfolio-dashboard/scripts/assets'
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--check',action='store_true');args=parser.parse_args()
    app=(SOURCE/'app.mjs').read_text()
    first,rest=app.split('\n',1)
    if not first.startswith('import ') or "from './model.mjs';" not in first:raise SystemExit('Unexpected app import; update the dependency-free build.')
    assets={'template.html':(SOURCE/'template.html').read_text(),'style.css':(SOURCE/'style.css').read_text(),
            'dashboard.mjs':(SOURCE/'model.mjs').read_text()+'\n'+rest}
    for name,text in assets.items():
        dest=DEST/name
        if args.check:
            if not dest.exists() or dest.read_text()!=text:raise SystemExit(f'Stale packaged viewer: {name}')
        else:DEST.mkdir(parents=True,exist_ok=True);dest.write_text(text)
    print('Portfolio assets match source.' if args.check else 'Packaged three portfolio assets.')
if __name__=='__main__':main()
