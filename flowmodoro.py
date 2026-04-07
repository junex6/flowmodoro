"""
Flowmodoro - macOS Menu Bar App
--------------------------------
A flowmodoro timer: work freely until you choose to stop,
then earn a proportional break (work time / 5).

Runs as a single rumps Timer with a single morphing MenuItem.
The short-session dialog runs in a background thread so the
timer keeps ticking while the user decides.
"""

import subprocess
import threading

import rumps

MIN_FOCUS = 30  # seconds; below this, ask the user what to do


# ── Helpers ───────────────────────────────────────────────────────────────────

def fmt(seconds: int) -> str:
    """Format seconds as MM:SS, or H:MM:SS for sessions over an hour."""
    m, s = divmod(abs(seconds), 60)
    h, m = divmod(m, 60)
    if h:
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m:02d}:{s:02d}"


def notify(message: str) -> None:
    """Send a notification. Works correctly when running as a .app bundle."""
    rumps.notification(title="Flowmodoro", subtitle="", message=message)


def ask_short_session(on_break, on_continue) -> None:
    """
    Show a dialog asking whether to take a break or keep focusing.
    Runs in a background thread so the timer is not blocked.
    Calls on_break() or on_continue() once the user chooses.
    """
    def _run():
        script = (
            'display dialog "You\'ve only been focusing for a short time. '
            'What would you like to do?" '
            'with title "Flowmodoro" '
            'buttons {"Continue Focus", "Take Break"} '
            'default button "Continue Focus"'
        )
        result = subprocess.run(
            ["osascript", "-e", script],
            capture_output=True, text=True
        )
        # stdout contains e.g. 'button returned:Take Break\n'
        if "Take Break" in result.stdout:
            on_break()
        else:
            on_continue()

    threading.Thread(target=_run, daemon=True).start()


# ── App ───────────────────────────────────────────────────────────────────────

class FlowmodoroApp(rumps.App):

    def __init__(self):
        super().__init__(name="Flowmodoro", title="🌊 Flow", quit_button=None)

        self.state      = "idle"
        self.paused     = False
        self.focus_secs = 0
        self.break_secs = 0
        self._asking    = False  # guard: prevent double-dialogs

        # Primary action toggles between start, pause/resume, and skip break
        self._action = rumps.MenuItem("▶   Start Focus", callback=self._on_action)

        # Stop button only visible during focus sessions
        self._stop = rumps.MenuItem("⏹   Stop & Take Break", callback=self._on_stop)

        self._quit = rumps.MenuItem("Quit Flowmodoro", callback=rumps.quit_application)
        self.menu = [self._action, self._stop, None, self._quit]

        # Hide stop button until a focus session starts
        self._stop.hidden = True

        rumps.Timer(self._on_tick, 1).start()

    # ── Tick ──────────────────────────────────────────────────────────────────

    def _on_tick(self, _):
        if self.state == "focus" and not self.paused:
            self.focus_secs += 1
            self.title = f"⏸ {fmt(self.focus_secs)}"

        elif self.state == "break":
            self.break_secs -= 1
            if self.break_secs <= 0:
                self._to_idle()
                notify("Break's over. Hit Start Focus when ready.")
            else:
                self.title = f"☕ {fmt(self.break_secs)}"

    # ── Action button (start / pause / resume / skip) ────────────────────────

    def _on_action(self, _):
        if self.state == "idle":
            self.state      = "focus"
            self.paused     = False
            self.focus_secs = 0
            self.title      = "⏸ 00:00"
            self._action.title = "⏸   Pause"
            self._stop.hidden = False

        elif self.state == "focus":
            if self.paused:
                # Resume
                self.paused = False
                self.title = f"⏸ {fmt(self.focus_secs)}"
                self._action.title = "⏸   Pause"
            else:
                # Pause
                self.paused = True
                self.title = f"▶ {fmt(self.focus_secs)}"
                self._action.title = "▶   Resume"

        elif self.state == "break":
            self._to_idle()

    # ── Stop button (end focus → take break) ─────────────────────────────────

    def _on_stop(self, _):
        if self.state != "focus":
            return
        if self._asking:
            return  # dialog already open, ignore extra clicks
        if self.focus_secs < MIN_FOCUS:
            self._asking = True
            ask_short_session(
                on_break=self._do_break,
                on_continue=self._do_continue,
            )
        else:
            self._do_break()

    # ── Break / continue callbacks ────────────────────────────────────────────

    def _do_break(self):
        self._asking    = False
        self.break_secs = self.focus_secs // 5
        notify(f"{fmt(self.focus_secs)} of focus. Break: {fmt(self.break_secs)}.")
        self.state = "break"
        self.paused = False
        self.title = f"☕ {fmt(self.break_secs)}"
        self._action.title = "⏭   Skip Break"
        self._stop.hidden = True

    def _do_continue(self):
        self._asking = False
        # Unpause so the timer resumes after the dialog
        self.paused = False
        self.title = f"⏸ {fmt(self.focus_secs)}"
        self._action.title = "⏸   Pause"

    # ── Reset ─────────────────────────────────────────────────────────────────

    def _to_idle(self):
        self.state      = "idle"
        self.paused     = False
        self.focus_secs = 0
        self.break_secs = 0
        self._asking    = False
        self.title      = "🌊 Flow"
        self._action.title = "▶   Start Focus"
        self._stop.hidden = True


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    FlowmodoroApp().run()
