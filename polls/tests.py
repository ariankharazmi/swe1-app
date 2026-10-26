import datetime

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Choice, Question


def create_question(question_text, days):
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)


class QuestionModelTests(TestCase):
    def test_was_published_recently_with_old_question(self):
        q = Question(pub_date=timezone.now() - datetime.timedelta(days=2))
        self.assertIs(q.was_published_recently(), False)

    def test_was_published_recently_with_recent_question(self):
        q = Question(pub_date=timezone.now() - datetime.timedelta(hours=1))
        self.assertIs(q.was_published_recently(), True)

    def test_str(self):
        q = create_question("What's up?", days=0)
        c = Choice.objects.create(question=q, choice_text="Not much")
        self.assertEqual(str(q), "What's up?")
        self.assertEqual(str(c), "Not much")


class PollsViewTests(TestCase):
    def test_index_no_questions(self):
        response = self.client.get(reverse("polls:index"))
        self.assertEqual(response.status_code, 200)
        self.assertQuerySetEqual(response.context["latest_question_list"], [])

    def test_index_with_question(self):
        q = create_question("Past question.", days=-1)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerySetEqual(response.context["latest_question_list"], [q])

    def test_detail_and_results(self):
        q = create_question("Detail question.", days=-1)
        self.assertContains(
            self.client.get(reverse("polls:detail", args=(q.id,))), q.question_text
        )
        self.assertContains(
            self.client.get(reverse("polls:results", args=(q.id,))), q.question_text
        )

    def test_vote_without_choice(self):
        q = create_question("Vote question.", days=-1)
        response = self.client.post(reverse("polls:vote", args=(q.id,)))
        self.assertContains(response, "You didn")

    def test_vote_with_choice(self):
        q = create_question("Vote question.", days=-1)
        c = Choice.objects.create(question=q, choice_text="Yes")
        response = self.client.post(
            reverse("polls:vote", args=(q.id,)), {"choice": c.id}
        )
        self.assertRedirects(response, reverse("polls:results", args=(q.id,)))
        c.refresh_from_db()
        self.assertEqual(c.votes, 1)
