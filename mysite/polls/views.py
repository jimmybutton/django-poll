from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.db.models import F
from django.views import generic
from django.utils import timezone

from .models import Question, Choice


class IndexView(generic.ListView):
    template_name = "polls/index.html"
    # context_object_name = "latest_question_list"
    paginate_by = 3

    def get_queryset(self):
        """Return the last five published quesions."""
        return Question.objects.filter(pub_date__lte=timezone.now()).order_by("-pub_date")  # [:5]


class DetailView(generic.DetailView):
    model = Question
    template_name = "polls/detail.html"

    def get_queryset(self):
        """
        Excludes any questions that aren't published yet.
        """
        return Question.objects.filter(pub_date__lte=timezone.now())


class ResultsView(generic.DetailView):
    model = Question
    template_name = "polls/results.html"

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        question = get_object_or_404(Question, pk=self.kwargs['pk'])
        choices = question.choice_set.all()
        context['chartdata'] = {
            'data': [c.votes for c in choices], 
            'labels': [c.choice_text for c in choices],
            }
        return context


def vote(request, question_id: int) -> HttpResponse:
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST["choice"])
    except (KeyError, Choice.DoesNotExist):
        return render(
            request,
            "polls/detail.html",
            {"question": question, "error_message": "You didn't select a choice.",},
        )
    else:
        selected_choice.votes = F("votes") + 1  # use F to avoid race condition
        selected_choice.save()
        return HttpResponseRedirect(reverse("polls:results", args=(question.id,)))
