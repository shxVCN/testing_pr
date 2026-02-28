"""
Представления приложения голосования.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count

from .models import Poll, Choice, Vote
from .forms import PollCreateForm, VoteForm


def poll_list(request):
    """Список всех опросов."""
    polls = Poll.objects.all().prefetch_related('choices')
    return render(request, 'polls/poll_list.html', {'polls': polls})


def poll_detail(request, pk):
    """Детальный просмотр опроса с возможностью голосования."""
    poll = get_object_or_404(Poll.objects.prefetch_related('choices', 'choices__votes'), pk=pk)
    user_has_voted = poll.user_has_voted(request.user) if request.user.is_authenticated else False

    if request.method == 'POST' and request.user.is_authenticated:
        form = VoteForm(request.POST, poll=poll)
        if form.is_valid():
            choice = form.cleaned_data['choice']
            # Удаляем предыдущий голос пользователя в этом опросе (один голос на опрос)
            Vote.objects.filter(choice__poll=poll, user=request.user).delete()
            Vote.objects.create(choice=choice, user=request.user)
            messages.success(request, 'Ваш голос учтён!')
            return redirect('polls:poll_results', pk=poll.pk)
    else:
        form = VoteForm(poll=poll) if not user_has_voted else None

    return render(request, 'polls/poll_detail.html', {
        'poll': poll,
        'form': form,
        'user_has_voted': user_has_voted,
    })


def poll_results(request, pk):
    """Результаты голосования по опросу."""
    poll = get_object_or_404(Poll.objects.prefetch_related('choices'), pk=pk)
    choices_with_votes = poll.choices.all().annotate(votes_count=Count('votes'))
    total_votes = sum(c.votes_count for c in choices_with_votes)

    return render(request, 'polls/poll_results.html', {
        'poll': poll,
        'choices_with_votes': choices_with_votes,
        'total_votes': total_votes,
    })


@login_required
def poll_create(request):
    """Создание нового опроса."""
    if request.method == 'POST':
        form = PollCreateForm(request.POST)
        if form.is_valid():
            poll = form.save(user=request.user)
            messages.success(request, f'Опрос "{poll.question}" создан!')
            return redirect('polls:poll_detail', pk=poll.pk)
    else:
        form = PollCreateForm()

    return render(request, 'polls/poll_create.html', {'form': form})
