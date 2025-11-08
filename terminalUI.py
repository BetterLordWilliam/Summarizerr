from textual import on, work
from textual.app import App, ComposeResult
from textual.containers import Horizontal, VerticalScroll, Center, Middle, Grid
from textual.screen import Screen
from textual.binding import Binding
from textual.timer import Timer
from textual.widgets import Header, Footer, MarkdownViewer, Button, Static, ProgressBar, Label, Input, DirectoryTree


# async def main(**kwargs):
#     tokens = kwargs['mrts'] 
#     temp = kwargs['temp']
    
#     md = asyncio.create_task(U.to_markdown_async(kwargs['file']))
#     md_result = await md
    
#     model_response = asyncio.create_task(U.send_md_to_model(md_result, tokens, temp))
#     model_response_result = await model_response
    
#     file_write = asyncio.create_task(U.write_model_response(kwargs['ofile'], model_response_result))
#     file_write_result = await file_write    

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
        self.app.switch_screen(RunnerMenu())

    @on(Button.Pressed, "#cancel")
    def handle_cancel(self) -> None: 
        self.app.pop_screen()


class RunnerMenu(Screen):
    def compose(self) -> ComposeResult:
        yield(
            Label('We are running')
        )

   
class StartMenu(Screen):
    def compose(self) -> ComposeResult:
        yield Grid(
            Label('Input file'),
            Input(),
            Label('Output directory'),
            Input(),
            Button('Confirm', variant='primary', id='confirm')
        )
        
    @on(Button.Pressed, '#confirm')
    def handle_confirm(self) -> None:
        self.app.switch_screen(RunnerMenu())

    
class MarkdownViewerScreen(Screen): 
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
    
    def __init__(self, file: str, ofile: str, mrts: int, temp: float, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._file = file
        self._ofile = ofile

    def compose(self) -> ComposeResult:
        with Center():
            with Middle():
                yield VerticalScroll(
                    Label(f'Input file: {self._file}'),
                    Label(f'Output directory: {self._ofile}')
                )
                yield Label("Processing")
                yield VerticalScroll(
                    Label('Input file'),
                    DirectoryTree(),
                    Label('Output directory'),
                    DirectoryTree()
                )
                yield Horizontal(
                    Button('Confirm', variant='primary', id='confirm'),
                    Button('Exit', variant='error', id='quit')
                )

    @on(Button.Pressed, "#quit")
    def handle_exit(self) -> None: 
        self.exit()

    def on_mount(self) -> None:
        self.progress_timer = self.set_interval(0.1, self.make_progress, pause=True)

    def make_progress(self) -> None:
        self.query_one(ProgressBar).advance(1)
    
    def action_start(self) -> None:
        start.query(ProgressBar).update(total=100)
        self.progress_timer.resume()


