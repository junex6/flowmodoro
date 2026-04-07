"""
Flowmodoro - macOS Menu Bar App
--------------------------------
A flowmodoro timer: work freely until you choose to stop,
then earn a proportional break (work time / 5).

Runs as a single rumps Timer with a single morphing MenuItem.
The short-session dialog runs in a background thread so the
timer keeps ticking while the user decides.
"""

import rumps
import subprocess
import threading

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


# ── Menu labels ───────────────────────────────────────────────────────────────

ACTION_LABEL = {
    "idle":  "▶   Start Focus",
    "focus": "⏹   Stop & Take Break",
    "break": "⏭   Skip Break",
}


# ── App ───────────────────────────────────────────────────────────────────────

class FlowmodoroApp(rumps.App):

    def __init__(self):
        super().__init__(name="Flowmodoro", title="🌊 Flow", quit_button=None)

        self.state      = "idle"
        self.focus_secs = 0
        self.break_secs = 0
        self._asking    = False  # guard: prevent double-dialogs

        self._action = rumps.MenuItem(ACTION_LABEL["idle"], callback=self._on_action)
        self._quit   = rumps.MenuItem("Quit Flowmodoro",    callback=rumps.quit_application)
        self.menu    = [self._action, None, self._quit]

        rumps.Timer(self._on_tick, 1).start()

    # ── Tick ──────────────────────────────────────────────────────────────────

    def _on_tick(self, _):
        if self.state == "focus":
            self.focus_secs += 1
            self.title = f"▶ {fmt(self.focus_secs)}"

        elif self.state == "break":
            self.break_secs -= 1
            if self.break_secs <= 0:
                self._to_idle()
                notify("Break's over. Hit Start Focus when ready.")
            else:
                self.title = f"☕ {fmt(self.break_secs)}"

    # ── Action button ─────────────────────────────────────────────────────────

    def _on_action(self, _):
        if self.state == "idle":
            self.state      = "focus"
            self.focus_secs = 0
            self.title      = "▶ 00:00"
            self._action.title = ACTION_LABEL["focus"]

        elif self.state == "focus":
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

        elif self.state == "break":
            self._to_idle()

    # ── Break / continue callbacks ────────────────────────────────────────────

    def _do_break(self):
        self._asking    = False
        self.break_secs = self.focus_secs // 5
        notify(f"{fmt(self.focus_secs)} of focus. Break: {fmt(self.break_secs)}.")
        self.state = "break"
        self.title = f"☕ {fmt(self.break_secs)}"
        self._action.title = ACTION_LABEL["break"]

    def _do_continue(self):
        self._asking = False
        # Timer is already running; nothing else needed.

    # ── Reset ─────────────────────────────────────────────────────────────────

    def _to_idle(self):
        self.state      = "idle"
        self.focus_secs = 0
        self.break_secs = 0
        self._asking    = False
        self.title      = "🌊 Flow"
        self._action.title = ACTION_LABEL["idle"]


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    FlowmodoroApp().run()