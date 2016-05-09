import subprocess
import json
import threading
import tempfile

import sublime_plugin
import sublime


def get_settings():
    settings_file = "How2.sublime-settings"
    return sublime.load_settings(settings_file)


class How2Runner(threading.Thread):
    def __init__(self, on_complete, **kwargs):
        self.query = kwargs.get("query")
        self.binary = kwargs.get("binary")
        self.max_answers = kwargs.get("max_answers")

        self.on_complete = on_complete

        super().__init__()

    def run(self):
        p = subprocess.Popen(
            [
                self.binary,
                "--max-answers",
                str(self.max_answers),
                "--json",
                self.query
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=False
        )

        answers, errors = p.communicate()
        answers = answers.decode("utf-8")
        errors = errors.decode("utf-8")

        self.on_complete(answers, errors)


class How2Command(sublime_plugin.WindowCommand):
    last_query = ""

    def run(self):
        self.view_panel = self.window.show_input_panel(
            "How2", self.last_query,
            self.after_input, self.on_input_change, None
        )
        self.view_panel.set_name("how2_query_bar")

    def after_input(self, query):
        query = query.strip()

        if not query:
            self.last_query = ""
            sublime.status_message("No query was entered")
            return
        else:
            self.how2(query)

    def on_input_change(self, query):
        query = query.strip()

        if not query:
            return

        self.last_query = query

    def how2(self, query):
        settings = get_settings()
        binary = settings.get("how2_binary")
        max_answers = settings.get("how2_max_answers")

        runner = How2Runner(self.how2_completed,
                            query=query,
                            binary=binary,
                            max_answers=max_answers)
        runner.start()

    def how2_completed(self, answers, errors):
        if errors:
            sublime.status_message("How2 responded with an error")
            return
        if not answers:
            sublime.status_message("No answers for query")
            return

        answers = json.loads(answers)

        if len(answers) == 0:
            sublime.status_message("No answers for query")
            return

        self.window.run_command("how2_show_answers", {"answers": answers})


class How2ShowAnswers(sublime_plugin.WindowCommand):
    last_answers = None

    def run(self, **kwargs):
        answers = kwargs.get("answers") or self.last_answers

        if answers is None:
            sublime.status_message("Make query to retrieve answers")
            return

        self.last_answers = answers

        pretty_answers = [self.for_quick_panel(a) for a in answers]

        self.window.show_quick_panel(
            pretty_answers, self.answer_selected,
            sublime.MONOSPACE_FONT | sublime.KEEP_OPEN_ON_FOCUS_LOST
        )

    def for_quick_panel(self, answer):
        is_accepted = answer.get("is_accepted")
        score = answer.get("score")

        owner = answer.get("owner")
        owner_reputation = owner.get("reputation")

        meta_info = "{} Score: {} Owner reputation: {}".format(
            '\u2713' if is_accepted else '\u2717',
            score,
            owner_reputation
        )

        short_answer = answer.get("body")[:60]

        return [meta_info, short_answer]

    def answer_selected(self, idx):
        if idx == -1:
            return

        answer = self.last_answers[idx]
        body = answer.get("body")
        answer_id = answer.get("answer_id")

        f = tempfile.NamedTemporaryFile(prefix="answer-{} ".format(answer_id),
                                        delete=False)
        f.write(body.encode())
        f.close()

        v = self.window.open_file(f.name)
        v.set_read_only(True)
        v.set_scratch(True)
