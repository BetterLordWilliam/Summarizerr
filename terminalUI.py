from art import *
from textual import on, work
from textual_fspicker import FileOpen, SelectDirectory
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Center, Middle, Grid, Container
from textual.screen import Screen, ModalScreen
from textual.binding import Binding
from textual.timer import Timer
from textual.widgets import Header, Footer, MarkdownViewer, Button, Static, ProgressBar, Label, Input, Rule, Markdown
import asyncio
import utility
import time
import obsidianify
import os
import sys
import pathlib
import subprocess
import tempfile

if (sys.platform == 'win32'):
    import win32pipe
    import win32file
    import pywintypes

file: str = None
odir: str = None
api_key: str = None
mrts: int = 4096
temp: float = 0.5
md_content: str = None


APP_DESCRIPTION_MARKDOWN = """
Welcome to Summarizerr!
A tool to summarize your lecture PDFs using Epic Model.

Features
- Convert PDF lectures to Markdown
- Summarize content using Epic Model
- Preview summaries in terminal
- Push summaries to Obsidian vaults

Getting Started
1. Click `i` to select your lecture PDF.
2. Click `d` to choose an output directory.
3. Click `s` to start the summarization process.
4. Preview the summary or push it to your Obsidian vault.

Requirements
- Your Obsidian API key for pushing summaries.

Enjoy summarizing your lectures with Summarizerr! 
"""

class MarkdownViewerScreen(Screen):    
    BINDINGS = [
        Binding(key='escape', action='app.pop_screen()', description='Pop screen'),
        Binding(key='o', action='obsidian', description='Send to Obsidian')
    ]

    def markdown_viewer(self): 
        """
        Returns a MarkdownViewer widget with the provided markdown content.
        """
        global md_content 
        
        markdown_viewer = MarkdownViewer(markdown = md_content, show_table_of_contents=True)
        markdown_viewer.code_indent_guides = False
        return markdown_viewer

    def compose(self) -> ComposeResult: 
        """
        A screen to view markdown content.
        """
        yield Header()
        markdown_viewer = self.markdown_viewer()
        yield markdown_viewer
        yield Footer()
        
    def action_obsidian(self) -> None:
        """
        Handles the 'o' key action to push content to Obsidian.
        """
        self.app.pop_screen()
        self.app.push_screen(ObsidianViewerScreen())
        
class ObsidianViewerScreen(ModalScreen):
    global api_key
    global md_content

    BINDINGS = [
        Binding(key='escape', action='app.pop_screen()', description='Pop screen')
    ]

    def compose(self) -> ComposeResult:
        """
        A screen to input Obsidian API key and filename to push content to Obsidian.
        """
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
        """
        Handles the Confirm button press to push content to Obsidian.
        """
        api_key = self.query_one('#apiBro').value
        file_name = self.query_one('#apiSis').value
        obsidianify.push_to_obsidian(api_key=api_key, content=md_content, filename=file_name)
        self.app.notify(f"Successfully pushed {file_name} to your obsidian vault!")
        self.app.pop_screen()

class CompletionScreen(ModalScreen):    
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
        """
        Handles the Obsidian button press to push content to Obsidian.
        """
        self.app.pop_screen()
        self.app.push_screen(ObsidianViewerScreen())

    @on(Button.Pressed, "#local")
    def handle_local(self) -> None:
        """
        Handles the Preview Local button press to view markdown locally.
        """
        self.app.pop_screen()
        self.app.push_screen(MarkdownViewerScreen())

    @on(Button.Pressed, "#cancel")
    def handle_cancel(self) -> None:
        """
        Handles the Cancel button press to close the completion screen.
        """
        self.app.pop_screen()

class RunnerMenu(Screen):
    BINDINGS = [
        Binding(key='escape', action='app.pop_screen()', description='Pop screen')
    ]
    
    def compose(self) -> ComposeResult:
        """
        A textual component that displays a progress bar that fills up over our upload progress.
        """
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
                    Horizontal(
                        Container(
                            Container(
                                Label("Converting to markdown", id="convertion_label"),
                                ProgressBar(id='converting', show_eta=False),
                                Label(id='finished_converting'),
                                id='converting_container'   
                            ),
                            Container(
                                Label("Sending the converted PDF to Epic Model", id="sending_model_label"),
                                ProgressBar(id='modeling',show_eta=False),
                                Label(id="finished_modeling"),
                                id='modeling_container'
                            ),
                            Container(
                                Label(f"Saving the Model's response", id="saving_model_label"),
                                ProgressBar(id='writing', show_eta=False),
                                Label(id="finished_writing"),
                                id='writing_container'
                            ),
                        ),
                        id="left_column"
                    )
                ),
                id="progress_grid"  
            )
        yield Footer()
    
    async def do_the_thing(self) -> None:
        """
        The main worker function that handles the PDF to markdown conversion, sending to model, and saving the response.
        """
        global file
        global odir 
        global md_content
        
        if (sys.platform == "win32"):
            pipe_name = r'\\.\pipe\fisherman_signals'
            try:
                pipe = win32pipe.CreateNamedPipe(
                    pipe_name,
                    win32pipe.PIPE_ACCESS_DUPLEX,
                    win32pipe.PIPE_TYPE_MESSAGE | win32pipe.PIPE_READMODE_MESSAGE | win32pipe.PIPE_WAIT,
                    1, 65536, 65536, 0, None
                )
            except pywintypes.error as e:
                self.notify(f'we failed to open the pipe, lost control {e}')
                return
            
            cmd = f'start "Fisherman Game" cmd /c ".\\fisherman.exe --pipe {pipe_name}"' 
            subprocess.Popen(cmd, shell=True)
            win32pipe.ConnectNamedPipe(pipe, None)
        else: 
            pipe_path = '/tmp/fisherman_pipe'
            try:
                if os.path.exists(pipe_path):
                    os.remove(pipe_path)
                
                os.mkfifo(pipe_path)
                print(f"Created named pipe: {pipe_path}")
                print()
                
                subprocess.Popen([
                    'x-terminal-emulator', '-e',
                    './fisherman', '--pipe', pipe_path
                ])
                
                pipe = open(pipe_path, 'w')
            except Exception as e:
                self.notify(f'we failed to open the pipe, lost control {e}')
        
        try:
            self.notify(file)
            self.notify(odir)
            
            self.notify('Converting from a pdf') 
            start = time.time()
            md = asyncio.create_task(utility.to_markdown_async(file))
            md_result = await md
            end = time.time()
            self.query_one("#convertion_label").update("Converted the PDF to markdown")
            self.query_one(ProgressBar).update(total=100, progress=100)
            self.notify(f'Finshed converting from pdf, {end - start}s')
            
            self.notify('Sending the converted PDF to Epic Model') 
            start = time.time()
            model_response = asyncio.create_task(utility.send_md_to_model(md_result, mrts, temp))
            model_response_result = await model_response
            md_content = model_response_result['summary']
            end = time.time()
            self.query_one("#sending_model_label").update("Converted PDF sent to the Epic Model")
            self.query_one(ProgressBar).update(total=100, progress=100)
            self.notify(f'Finished getting response from model {end - start}s')
            
            self.notify("Saving the Model's response") 
            start = time.time()
            file_write = asyncio.create_task(utility.write_model_response(file, odir, md_content))
            file_write_result = await file_write
            end = time.time()
            self.query_one("#saving_model_label").update("Saved the Model's response")
            self.query_one(ProgressBar).update(total=100, progress=100)
            self.notify(f'Finished writing the models response to disk {end - start}')
            
            self.app.pop_screen() 
            self.app.push_screen(CompletionScreen())
            
            message = "SUCCESS:Great job! 🔥🔥🔥🔥\n"
            
            try: 
                if (sys.platform == "win32"):
                    win32file.WriteFile(pipe, message.encode())
                    win32file.CloseHandle(pipe)
                else:
                    pipe.write(message)
                    pipe.flush()
            except Exception as e:
                self.notify('oops, handle to the named pipe was lost. Did you close the fishing game?')
            
        except Exception as e:
            self.notify(f'Error occured during pdf processing, {e}')
            self.app.pop_screen()

            message = "FAILURE:Try again! 💀💀💀💀\n"
            
            try: 
                if (sys.platform == "win32"):
                    win32file.WriteFile(pipe, message.encode())
                    win32file.CloseHandle(pipe) 
                else: 
                    pipe.write(message)
                    pipe.flush()
            except Exception as e:
                    self.notify('oops, handle to the named pipe was lost. Did you close the fishing game?')
        
    def on_mount(self):   
        """
        Mounts the input file and output directory on screen.        
        """     
        if (file is not None):
            self.query_one('#inputfile').update(str(file))
        if (odir is not None):
            self.query_one('#outputdir').update(str(odir))

        self.run_worker(self.do_the_thing)

class StartMenu(Screen):
    BINDINGS = [
        Binding(key="i", action="open_ifile", description="Open source file"),
        Binding(key="d", action="open_output_directory", description="Open target"),
        Binding(key="s", action="start_conversion", description="Start conversion")
    ]
    
    def compose(self) -> ComposeResult:
        """
        A textual component that displays a start menu on terminal.
        """
        yield Header()
        with Center():
            with Middle():
                yield Static(f"{text2art('Summarizerr', font='Alligator')}", id="heading")
                yield Label(id='inputfile')
                yield Label(id='outputdir')
                yield Rule()
                yield Container(
                    Markdown(APP_DESCRIPTION_MARKDOWN, id="app_description")
                )
        yield Footer()

    def action_start_conversion(self) -> None:
        """
        Starts the conversion process after checking if file and output directory are set.
        """
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
    async def action_open_ifile(self) -> None:
        """
        Opens a file picker to select the input file.
        """
        global file 
         
        if opened := await self.app.push_screen_wait(FileOpen(must_exist=True)):
            file = str(opened)
            self.query_one('#inputfile').update(str(opened))
        
    @work
    async def action_open_output_directory(self):
        """"
        Opens a directory picker to select the output directory.
        """
        global odir 
        
        if opened := await self.app.push_screen_wait(SelectDirectory()):
            odir = str(opened)
            self.query_one("#outputdir").update(str(opened)) 
            
    def on_mount(self):
        if (file is not None): 
            self.query_one('#inputfile').update(str(file))
        if (odir is not None):
            self.query_one('#outputdir').update(str(odir))


class SummarizerApp(App[None]):
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
        """
        A textual component that displays a header, footer, and main screen on terminal.
         """
        yield Header()
        yield Footer()
        
        global file
        global odir 
        
    def action_exit(self) -> None: 
        """
        Exits the application.
        """
        self.exit()
        
    def action_back(self) -> None:
        """
        Goes back to the start menu.
        """
        self.notify('Wassup')
        pass
            
    def on_mount(self) -> None:
        """
        Mounts the start menu on application start.
        """
        self.title = "Summarizerr"
        self.sub_title = "Summarize your lectures"
        self.push_screen(StartMenu())
