"""CLI entry point."""
import defopt
from summarizer.app.main import main

if __name__ == '__main__':
    defopt.run([main],
               short=dict(host='H', port='p'))
