from django.shortcuts import render, get_object_or_404, redirect
from .models import Category, Proverb, Achievement
import random
from django.db.models import Q
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from .models import Profile
from django.contrib.auth import logout
from django.contrib import messages
from .forms import ProfileUpdateForm

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Сразу создаем профиль для нового юзера
            Profile.objects.create(user=user)
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'ProverbsApp/register.html', {'form': form})

@login_required()
def profile_view(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            print("✅ Файлы получены:", request.FILES)
            return redirect('profile')
        else:
            print("❌ Ошибки формы:", form.errors)
    else:
        form = ProfileUpdateForm(instance=profile)

    return render(request, 'ProverbsApp/profile.html', {'profile': profile, 'form': form})


def public_profile_view(request, user_id):
    target_profile = get_object_or_404(Profile, user_id=user_id)

    if request.user.is_authenticated and request.user.id == user_id:
        return redirect('profile')

    return render(request, 'ProverbsApp/public_profile.html', {'target_profile': target_profile})

def logout_view(request):
    logout(request)
    messages.info(request, "Вы успешно вышли из системы. Ждем вас снова!")
    return redirect('login')
def index(request):
    query = request.GET.get('q')
    if query:
        proverbs = Proverb.objects.filter(
            Q(text__icontains=query) | Q(meaning__icontains=query)
        )
    else:
        proverbs = Proverb.objects.all()

    context = {
        'proverbs': proverbs,
        'search_query': query if query else '',
    }
    return render(request, 'ProverbsApp/index.html', context)
def category_detail(request, category_id):
    category = get_object_or_404(Category, pk=category_id)
    proverbs = category.proverbs.all()
    context = {
        'category': category,
        'proverbs': proverbs
    }
    return render(request, 'ProverbsApp/catergory_detail.html', context)

def quiz_view(request):

    # 10 случайных пословиц
    questions = list(Proverb.objects.order_by('?')[:10])

    if not questions:
        return render(request, 'ProverbsApp/quiz_error.html', {
            'error_message': 'В базе данных нет пословиц.'
        })

    step = request.session.get('quiz_step', 0)

    if step >= len(questions):

        final_score = request.session.get('quiz_score', 0)
        total = len(questions)

        if request.user.is_authenticated:
            profile = request.user.profile
            profile.total_score += final_score
            profile.completed_quizzes += 1
            profile.update_streak()
            profile.save()

        request.session['quiz_step'] = 0
        request.session['quiz_score'] = 0

        return render(request, 'ProverbsApp/quiz_final.html', {
            'score': final_score,
            'total': total
        })

    current_question = questions[step]

    correct = current_question.meaning

    wrong_meanings = list(
        Proverb.objects.exclude(id=current_question.id)
        .values_list('meaning', flat=True)
        .distinct()
    )

    wrong_answers = random.sample(wrong_meanings, min(3, len(wrong_meanings)))

    options = [{'meaning': correct, 'is_correct': True}]

    for w in wrong_answers:
        options.append({
            'meaning': w,
            'is_correct': False
        })

    random.shuffle(options)

    progress_percent = int((step / len(questions)) * 100)

    return render(request, 'ProverbsApp/quiz.html', {
        'question': current_question.text,
        'options': options,
        'step_number': step + 1,
        'total_steps': len(questions),
        'progress_percent': progress_percent
    })
def quiz_answer(request):
    if request.method == "POST":
        is_correct = request.POST.get('is_correct') == 'true'
        if is_correct:
            request.session['quiz_score'] = request.session.get('quiz_score', 0) + 1
        request.session['quiz_step'] = request.session.get('quiz_step', 0) + 1
    return redirect('quiz')

def leaderboard(request):
    top_users = Profile.objects.order_by('-total_score')[:10]
    return render(request, 'ProverbsApp/leaderboard.html', {'top_users': top_users})