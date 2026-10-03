"""Offline website checks. No Gemini key or Slack connection needed."""
import unittest
from unittest.mock import patch
from streamlit.testing.v1 import AppTest
import core
ORIGINAL_ANSWER = core.answer_question


class WebsiteTests(unittest.TestCase):
    def test_initial_page_and_question(self):
        app = AppTest.from_file(str(core.ROOT / "app.py"), default_timeout=20).run()
        self.assertEqual(len(app.exception), 0)
        with patch.object(core, "answer_question", side_effect=lambda method, question, *args: core_result(method, question)):
            app.button[0].click().run()
        self.assertEqual(len(app.exception), 0)
        self.assertEqual(len(app.session_state["answers"]), 3)

    def test_evaluation_reviews_survive_question_switch(self):
        app = AppTest.from_file(str(core.ROOT / "app.py"), default_timeout=20).run()
        with patch.object(core, "answer_question", side_effect=lambda method, question, *args: core_result(method, question)):
            next(b for b in app.button if b.label == "Run missing methods for this question").click().run()
        self.assertEqual(len(app.exception), 0)
        app.selectbox(key="review_support_Q01rules").select("Supported").run()
        app.selectbox(key="review_correct_Q01rules").select("Correct").run()
        question_box = next(s for s in app.selectbox if s.label == "Test question")
        question_box.select_index(1).run()
        next(s for s in app.selectbox if s.label == "Test question").select_index(0).run()
        self.assertEqual(app.selectbox(key="review_support_Q01rules").value, "Supported")
        self.assertEqual(app.selectbox(key="review_correct_Q01rules").value, "Correct")
        self.assertEqual(len(app.session_state["evaluation"]), 3)
        self.assertEqual(len(app.exception), 0)


def core_result(method, question):
    result = ORIGINAL_ANSWER("rules", question)
    result["method"] = method
    return result


if __name__ == "__main__":
    unittest.main()
