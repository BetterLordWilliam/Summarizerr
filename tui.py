from textual import on, work
from textual.app import App, ComposeResult
from textual.containers import Horizontal, VerticalScroll, Center, Middle, Grid, Container
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
            Button("Preview Local", variant="primary", id="local"),
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
    BINDINGS = [
        Binding(key="o", action="obsidian", description="Open obsidian")
    ]

    def markdown_viewer(self): 
        markdown_viewer = MarkdownViewer(EXAMPLE_MARKDOWN, show_table_of_contents=True)
        markdown_viewer.code_indent_guides = False
        return markdown_viewer
    
    def compose(self) -> ComposeResult: 
        markdown_viewer = self.markdown_viewer()
        yield markdown_viewer
        yield Footer()

class Summarizerr(App[None]):
    CSS_PATH = "style.tcss"

    BINDINGS = [
        Binding(key="q", action="request_quit", description="Quit the app"),
        Binding(key="s", action="start", description="Start the timer")
    ]

    progress_timer: Timer

    def on_mount(self) -> None:
        """Start the sequential progress animation."""
        # hide all bars except the first, then start the tick timer
        bars = list(self.query(ProgressBar))
        for i, bar in enumerate(bars):
            bar.update(progress=0)
            bar.styles.display = "block" if i == 0 else "none"
        # run _tick every 0.05s
        self.progress_timer = self.set_interval(0.05, self._tick)

        # ensure first bar is visible
        self.query_one("#bar1").styles.display = "block"

        # store index state
        self._current_index = 0

    def action_request_quit(self) -> None:
        self.push_screen(CompletionScreen())

    def compose(self) -> ComposeResult:
        yield Header()

        with Center():
            with Middle():
                yield Container(
                    ProgressBar(id="bar1"),
                    ProgressBar(id="bar2"),
                    ProgressBar(id="bar3"),
                )
        yield Footer()

    def _tick(self) -> None:
        """Called periodically to advance the current progress bar. When it reaches 100, move to next."""
        bars = list(self.query(ProgressBar))
        if self._current_index >= len(bars):
            # nothing left; stop timer
            try:
                self.progress_timer.stop()
            except Exception:
                pass
            return

        bar = bars[self._current_index]
        # increment progress
        new_progress = min(100, (bar.progress or 0) + 3)
        bar.update(progress=new_progress)

        if new_progress >= 100:
            # hide finished bar
            bar.styles.display = "none"
            self._current_index += 1
            if self._current_index < len(bars):
                # show next bar and reset its progress
                next_bar = bars[self._current_index]
                next_bar.update(progress=0)
                next_bar.styles.display = "block"
            else:
                # finished all bars; stop timer
                try:
                    self.progress_timer.stop()
                except Exception:
                    pass
        

if __name__ == "__main__":
    app = Summarizerr()
    app.run()