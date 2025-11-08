from textual.app import App, ComposeResult
from textual.containers import Center, Middle
from textual.timer import Timer
from textual.widgets import ProgressBar, Footer

class ProgressBarWidget(App[None]):
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

if __name__ == "__main__":
    ProgressBarWidget().run()

    