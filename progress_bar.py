from textual import on, work
from textual.app import App, ComposeResult
from textual.containers import Horizontal, VerticalScroll, Center, Middle, Grid
from textual.screen import Screen
from textual.binding import Binding
from textual.timer import Timer
from textual.widgets import Header, Footer, MarkdownViewer, Button, Static, ProgressBar, Label
class CompletionScreen(Screen):
    """
    A textual component that displays a screen on terminal. Includes buttons to open MD on screen or to upload it to obsidian endpoint.
    """
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
    """
    Markdown viewer screen, to view markdown local file on terminal.
    """
    def markdown_viewer(self, mdFile: str): 
        markdown_viewer = MarkdownViewer(mdFile, show_table_of_contents=True)
        markdown_viewer.code_indent_guides = False
        return markdown_viewer
    
    def compose(self) -> ComposeResult: 
        markdown_viewer = self.markdown_viewer()
        yield markdown_viewer

class SummarizerApp(App[None]):
    """
    A Textual app to display a progress bar that fills up over our upload progress.
    NOTE: Currently a mock implementation that fills the bar over time. 
    """

    BINDINGS = [("s", "start", "Start")]
    progress_timer: Timer

    def compose(self) -> ComposeResult:
        with Center():
            with Middle():
                yield ProgressBar()
        yield Footer()
    
    def on_mount(self) -> None:
        self.progress_timer = self.set_interval(0.1, self.make_progress, pause=True)

    def make_progress(self) -> None:
        self.query_one(ProgressBar).advance(1)
    
    def action_start(self) -> None:
        start.query(ProgressBar).update(total=100)
        self.progress_timer.resume()

    def notify_process(self) -> ComposeResult:
        yield Label("Processing")

