from textual import on, work
from textual_fspicker import FileOpen, SelectDirectory
from textual.app import App, ComposeResult
from textual.containers import Horizontal, VerticalScroll, Center, Middle, Grid, Container
from textual.screen import Screen
from textual.binding import Binding
from textual.timer import Timer
from textual.widgets import Header, Footer, MarkdownViewer, Button, Static, ProgressBar, Label, Input, Rule
import asyncio
import utility
import time


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

class RunnerMenu(Screen):
    def __init__(self, file: str, odir: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._file = file
        self._odir = odir

    def compose(self) -> ComposeResult:
        yield Header()
        with Center(): 
            with Middle():
                yield Container(
                    Label(id='inputfile'),
                    Label(id='outputdir'),
                    Rule(),
                    Container(
                        ProgressBar(id='converting', show_eta=False),
                        Label(id='finished_converting'),
                        id='converting_container'
                    ),
                    Container(
                        ProgressBar(id='modeling',show_eta=False),
                        Label(id="finished_modeling"),
                        id='modeling_container'
                    ),
                    Container(
                        ProgressBar(id='writing', show_eta=False),
                        Label(id="finished_writing"),
                        id='writing_container'
                    )
                )
        yield Footer()
    
    async def do_the_thing(self) -> None:
        self.notify(self._file)
        self.notify(self._odir)
        
        self.notify('we are now converting from a pdf') 
        start = time.time()
        md = asyncio.create_task(utility.to_markdown_async(self._file))
        md_result = await md
        end = time.time()
        self.query_one(ProgressBar).update(total=100, progress=100)
        self.notify(f'finished converting from pdf, {end - start}s')
        
        self.notify('we are now sending the converted pdf to epic model') 
        start = time.time()
        model_response = asyncio.create_task(utility.send_md_to_model(md_result, 1024, 0.))
        model_response_result = await model_response
        end = time.time()
        self.notify(f'finished getting response from model {end - start}s')
        
        self.notify('we are now saving the models response') 
        start = time.time()
        file_write = asyncio.create_task(utility.write_model_response(self._odir, model_response_result))
        file_write_result = await file_write  
        end = time.time()
        self.notify(f'finished writing the models response to disk {end - start}')
        self.app.push_screen(CompletionScreen())
        
    
    def on_mount(self) -> None:        
        if (self._file is not None):
            self.query_one('#inputfile').update(str(self._file))
        if (self._odir is not None):
            self.query_one('#outputdir').update(str(self._odir))

        self.run_worker(self.do_the_thing)

    # def make_progress(self) -> None:
    #     self.query_one(ProgressBar).advance(1)
    
    # def action_start(self) -> None:
    #     self.query_one(ProgressBar).update(total=100)
    #     self.progress_timer.resume()


class MarkdownViewerScreen(Screen): 
    def __init__(self, mdFile: str): 
        self._mdFile = mdFile

    def markdown_viewer(self): 
        markdown_viewer = MarkdownViewer(self._mdFile, show_table_of_contents=True)
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

    CSS_PATH = "style.tcss"

    BINDINGS = [
        Binding(key="q", action="exit", description="Quit the app"),
        # Binding(key="c", action="confirm", description="Confirm choices")
    ]

    progress_timer: Timer
    
    def __init__(self, file: str, ofile: str, mrts: int, temp: float, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self._file = file or None
        self._odir = ofile or None
        self._mrts = mrts
        self._temp = temp

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static("Welcome to Summarizerr", id="main_title")
        with Center():
            with Middle():
                yield Container(
                    VerticalScroll(
                        Label(id='inputfile'),
                        Label(id='outputdir'),
                        Horizontal(
                            Button('Input file', id='ifile'),
                            Button('Output directory', id='odir'),
                        ), 
                    ),
                    Horizontal(
                        Button('Confirm', variant='primary', id='confirm'),
                    )
                )
        yield Footer()

    @on(Button.Pressed, "#quit")
    def action_exit(self) -> None: 
        self.exit()
        
    @on(Button.Pressed, '#confirm')
    def confirm(self) -> None:
        good = True 
        if (self._file is None): 
            self.notify('You need a file')
            good = False
        if (self._odir is None):
            self.notify('You need an output location')
            good = False
        if (good):
            self.notify(f'{self._file}\n{self._odir}')
            self.push_screen(RunnerMenu(file = self._file, odir = self._odir))
    
    @work 
    @on(Button.Pressed, '#ifile')
    async def handle_ifile(self) -> None:
        if opened := await self.push_screen_wait(FileOpen(must_exist=True)):
            self._file = opened
            self.query_one('#inputfile').update(str(opened))
        
    @work
    @on(Button.Pressed, '#odir')
    async def handle_odir(self):
        if opened := await self.push_screen_wait(SelectDirectory()):
            self._odir = opened
            self.query_one("#outputdir").update(str(opened)) 
            
    def on_mount(self) -> None:
        self.title = "Summarizerr"
        self.sub_title = "Summarize your lectures"

        if (self._file is not None):
            self.query_one('#inputfile').update(str(self._file))
        if (self._odir is not None):
            self.query_one('#outputdir').update(str(self._odir))
