import typer

from algotrader.cli import processors, strategies, sources, pipeline

app = typer.Typer(no_args_is_help=True)
app.add_typer(processors.app, name='processor', short_help='Processors related commands')
app.add_typer(strategies.app, name='strategy', short_help='Strategies related commands')
app.add_typer(sources.app, name='source', short_help='Sources related commands')
app.add_typer(pipeline.app, name='pipeline', short_help='Pipelines related commands')


def initiate_cli():
    app()
