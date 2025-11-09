from art import *
from textual import on, work
from textual_fspicker import FileOpen, SelectDirectory
from textual.app import App, ComposeResult
from textual.containers import Horizontal, VerticalScroll, Center, Middle, Grid, Container
from textual.screen import Screen, ModalScreen
from textual.binding import Binding
from textual.timer import Timer
from textual.widgets import Header, Footer, MarkdownViewer, Button, Static, ProgressBar, Label, Input, Rule
import asyncio
import utility
import time
import obsidianify


file: str = None
odir: str = None
api_key: str = None
mrts: int = 4096
temp: float = 0.5
md_content: str = None


class MarkdownViewerScreen(Screen): 
    # BINDING = [
    #     Binding(key="o", action="obsidian", description="Open obsidian")
    # ]
    
    BINDINGS = [
        Binding(key='escape', action='app.pop_screen()', description='Pop screen')
    ]

    def markdown_viewer(self): 
        global md_content 
        
        markdown_viewer = MarkdownViewer(markdown = md_content, show_table_of_contents=True)
        markdown_viewer.code_indent_guides = False
        return markdown_viewer

    def compose(self) -> ComposeResult: 
        yield Header()
        markdown_viewer = self.markdown_viewer()
        yield markdown_viewer
        yield Footer()
        

class ObsidianViewerScreen(ModalScreen):
    global api_key
    global md_content

    BINDINGS = [
        Binding(key='escape', action='app.pop_screen()', description='Pop screen')
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        with Center():
            with Middle():
                yield Label("Obsidian Api Key:")
                yield Input(placeholder="Your obsidian API Key", id='apiBro')
                yield Input(placeholder="Your obsidian filename", id='apiSis')
                yield Button("Confirm", variant="primary", id="confirm")
        yield Footer()
    
    @on(Button.Pressed, "#confirm")
    def send_to_obsidian(self) -> None:
        api_key = self.query_one('#apiBro').value
        file_name = self.query_one('#apiSis').value
        obsidianify.push_to_obsidian(api_key=api_key, content=md_content, filename=file_name)
        self.app.notify("Successfully pushed f{file_name} to your obsidian vault!")
        self.app.pop_screen()

        
class CompletionScreen(ModalScreen):
    """
    A textual component that displays a screen on terminal. Includes buttons to open MD on screen or to upload it to obsidian endpoint.
    """
    
    BINDINGS = [
        Binding(key='escape', action='app.pop_screen()', description='Pop screen')
    ]
    
    def compose(self) -> ComposeResult: 
        yield Grid (
            Label("Completed!"),
            Button("Obsidian", variant="primary", id="obsidian"),
            Button("Preview Local", variant="primary", id="local"),
            Button("Cancel", variant="error", id="cancel"),
            id="dialog"
        )
    
    @on(Button.Pressed, "#obsidian")
    def handle_obsidian(self) -> None:
        self.app.pop_screen()
        self.app.push_screen(ObsidianViewerScreen())

    @on(Button.Pressed, "#local")
    def handle_local(self) -> None:
        self.app.pop_screen()
        self.app.push_screen(MarkdownViewerScreen())

    @on(Button.Pressed, "#cancel")
    def handle_cancel(self) -> None:
        self.app.pop_screen()

class RunnerMenu(Screen):
    
    BINDINGS = [
        Binding(key='escape', action='app.pop_screen()', description='Pop screen')
    ]
    
    def compose(self) -> ComposeResult:
        yield Header()
        with Center():
            yield Grid(
                Container (
                    Static(f"{text2art('Loading...', font='Alligator')}", id='ascii_art'),
                    id='right_column'
                ),
                Container (
                    Label(id='inputfile'),
                    Label(id='outputdir'),
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
                            ),
                            id="left_column"
                        ),
                        id="progress_grid"  
                    )
        yield Footer()
    
    async def do_the_thing(self) -> None:
        global file
        global odir 
        global md_content
        
        try:
            self.notify(file)
            self.notify(odir)
            
            self.notify('we are now converting from a pdf') 
            start = time.time()
            md = asyncio.create_task(utility.to_markdown_async(file))
            md_result = await md
            end = time.time()
            self.query_one(ProgressBar).update(total=100, progress=100)
            self.notify(f'finished converting from pdf, {end - start}s')
            
            self.notify('we are now sending the converted pdf to epic model') 
            start = time.time()
            model_response = asyncio.create_task(utility.send_md_to_model(md_result, mrts, temp))
            model_response_result = await model_response
            md_content = model_response_result['summary']
            end = time.time()
            self.query_one(ProgressBar).update(total=100, progress=100)
            self.notify(f'finished getting response from model {end - start}s')
            
            self.notify('we are now saving the models response') 
            start = time.time()
            file_write = asyncio.create_task(utility.write_model_response(file, odir, md_content))
            file_write_result = await file_write
            end = time.time()
            self.query_one(ProgressBar).update(total=100, progress=100)
            self.notify(f'finished writing the models response to disk {end - start}')
            
            self.app.pop_screen() 
            self.app.push_screen(CompletionScreen())
            
        except Exception as e:
            self.notify(f'Error occured during pdf processing, {e}')
            self.app.pop_screen()
        
    def on_mount(self):        
        if (file is not None):
            self.query_one('#inputfile').update(str(file))
        if (odir is not None):
            self.query_one('#outputdir').update(str(odir))

        self.run_worker(self.do_the_thing)

class StartMenu(Screen):
    BINDINGS = [
        Binding(key="i", action="open_ifile", description="Open source file"),
        Binding(key="o", action="open_output_directory", description="Open target"),
        Binding(key="s", action="start_conversion", description="Start conversion")
    ] 
    
    def compose(self) -> ComposeResult:
        yield Header()
        with Center():
            with Middle():
                yield Static(f"{text2art('Summarizerr', font='Alligator')}", id="heading")
                yield Container(
                    Label(id='inputfile'),
                    Label(id='outputdir'),
                )
                # yield Button('Confirm', variant='primary', id='confirm')
        yield Footer()
            
    # @on(Button.Pressed, '#confirm')
    def action_start_conversion(self) -> None:
        global file
        global odir 
        
        good = True 
        if (file is None): 
            self.notify('You need a file')
            good = False
        if (odir is None):
            self.notify('You need an output location')
            good = False
        if (good):
            self.notify(f'{file}\n{odir}')
            self.app.push_screen(RunnerMenu())
    
    @work 
    # @on(Button.Pressed, '#ifile')
    async def action_open_ifile(self) -> None:
        global file 
         
        if opened := await self.app.push_screen_wait(FileOpen(must_exist=True)):
            file = str(opened)
            self.query_one('#inputfile').update(str(opened))
        
    @work
    # @on(Button.Pressed, '#odir')
    async def action_open_output_directory(self):
        global odir 
        
        if opened := await self.app.push_screen_wait(SelectDirectory()):
            odir = str(opened)
            self.query_one("#outputdir").update(str(opened)) 
    

class SummarizerApp(App[None]):
    """
    A Textual app to display a progress bar that fills up over our upload progress.
    NOTE: Currently a mock implementation that fills the bar over time. 
    """

    CSS_PATH = "style.tcss"
    BINDINGS = [
        Binding(key="q", action="exit", description="Quit the app"),
    ]

    progress_timer: Timer
    
    def __init__(self, filee: str, ofilee: str, mrts: int, temp: float, api_keyy: str, *args, **kwargs):
        """
        Instances the global variables.
        """
        super().__init__(*args, **kwargs)
        global file
        global odir
        global api_key
        
        file = filee or None
        odir = ofilee or None
        api_key = api_keyy or None

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        
        global file
        global odir 
        
    def action_exit(self) -> None: 
        self.exit()
        
    def action_back(self) -> None:
        self.notify('Wassup')
        pass
            
    def on_mount(self) -> None:
        self.title = "Summarizerr"
        self.sub_title = "Summarize your lectures"
        self.push_screen(StartMenu())
