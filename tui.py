from textual import on, work
from textual.app import App, ComposeResult
from textual.containers import Horizontal, VerticalScroll, Center, Middle, Grid
from textual.screen import Screen
from textual.binding import Binding
from textual.timer import Timer
from textual.widgets import Header, Footer, MarkdownViewer, Button, Static, ProgressBar, Label

EXAMPLE_MARKDOWN = """\
# Markdown Viewer

This is an example of Textual's `MarkdownViewer` widget.


## Features

Markdown syntax and extensions are supported.

- Typography *emphasis*, **strong**, `inline code` etc.
- Headers
- Lists (bullet and ordered)    
- Syntax highlighted code blocks
- Tables!

## Tables

Tables are displayed in a DataTable widget.

| Name            | Type   | Default | Description                        |
| --------------- | ------ | ------- | ---------------------------------- |
| `show_header`   | `bool` | `True`  | Show the table header              |
| `fixed_rows`    | `int`  | `0`     | Number of fixed rows               |
| `fixed_columns` | `int`  | `0`     | Number of fixed columns            |
| `zebra_stripes` | `bool` | `False` | Display alternating colors on rows |
| `header_height` | `int`  | `1`     | Height of header row               |
| `show_cursor`   | `bool` | `True`  | Show a cell cursor                 |


## Code Blocks

Code blocks are syntax highlighted.

```python
class ListViewExample(App):
    def compose(self) -> ComposeResult:
        yield ListView(
            ListItem(Label("One")),
            ListItem(Label("Two")),
            ListItem(Label("Three")),
        )
        yield Footer()
```

## Litany Against Fear

I must not fear.
Fear is the mind-killer.
Fear is the little-death that brings total obliteration.
I will face my fear.
I will permit it to pass over me and through me.
And when it has gone past, I will turn the inner eye to see its path.
Where the fear has gone there will be nothing. Only I will remain.
"""

class CompletionScreen(Screen):
    def compose(self) -> ComposeResult: 
        yield Grid(
            Label("Completed!"),
            Button("Obsidian", variant="primary", id="obsidian"),
            Button("View Local", variant="primary", id="local"),
            Button("Cancel", variant="primary", id="cancel"),
            id="dialog"
        )
    
    @on(Button.Pressed, "#obsidian")
    def handle_obsidian(self) -> None: 
        self.dismiss(True)

    @on(Button.Pressed, "#local")
    def handle_local(self) -> None: 
        self.app.switch_screen(MarkdownViewerScreen())

    @on(Button.Pressed, "#cancel")
    def handle_cancel(self) -> None: 
        self.app.pop_screen()

class MarkdownViewerScreen(Screen): 
    def markdown_viewer(self): 
        markdown_viewer = MarkdownViewer(EXAMPLE_MARKDOWN, show_table_of_contents=True)
        markdown_viewer.code_indent_guides = False
        return markdown_viewer
    
    def compose(self) -> ComposeResult: 
        markdown_viewer = self.markdown_viewer()
        yield markdown_viewer

class Summarizerr(App[None]):
    CSS_PATH = "style.tcss"

    BINDINGS = [
        Binding(key="q", action="request_quit", description="Quit the app"),
    ]
    progress_timer: Timer
    
    def on_mount(self) -> None:
        """Set up a timer to simulate progess happening."""
        self.progress_timer = self.set_interval(1 / 10, self.make_progress, pause=True)

    def make_progress(self) -> None:
        """Called automatically to advance the progress bar."""
        self.query_one(ProgressBar).advance(1)

    def action_start(self) -> None:
        """Start the progress tracking."""
        self.query_one(ProgressBar).update(total=10)
        self.progress_timer.resume()

    def action_request_quit(self) -> None:
        self.push_screen(CompletionScreen())

    def compose(self) -> ComposeResult:
        yield Header()
        # yield Static("Welcome to Summarizerr", classes="box")
        # yield Horizontal(
        #     Button("Default")
        # )
        # yield Footer()

        with Center():
            with Middle():
                yield ProgressBar()
        yield Footer()

        

if __name__ == "__main__":
    app = Summarizerr()
    app.run()