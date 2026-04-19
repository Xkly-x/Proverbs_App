from django.shortcuts import render, get_object_or_404, redirect
from .models import Category, Proverb, Achievement, Profile, Comment
import random
from django.db.models import Q, Count
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .forms import ProfileUpdateForm, ProverbSubmitForm, CommentForm


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            Profile.objects.create(user=user)
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'ProverbsApp/register.html', {'form': form})


@login_required()
def profile_view(request):
    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST' and 'avatar' in request.FILES:
        form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = ProfileUpdateForm(instance=profile)

    my_proverbs = request.user.user_proverbs.all().prefetch_related('categories')

    approved_proverbs = my_proverbs.filter(status='approved')
    pending_proverbs = my_proverbs.filter(status='pending')
    rejected_proverbs = my_proverbs.filter(status='rejected')

    context = {
        'profile': profile,
        'form': form,
        'approved_proverbs': approved_proverbs,
        'pending_proverbs': pending_proverbs,
        'rejected_proverbs': rejected_proverbs,
    }
    return render(request, 'ProverbsApp/profile.html', context)


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
    query = request.GET.get('q', '')
    category_id = request.GET.get('category', '')
    tab = request.GET.get('tab', 'main')

    base_queryset = Proverb.objects.filter(status='approved').prefetch_related(
        'categories', 'likes'
    ).annotate(
        comments_count=Count('comments', distinct=True),
        num_likes=Count('likes', distinct=True)
    )

    if tab == 'users':
        proverbs = base_queryset.filter(author__isnull=False)
    elif tab == 'liked':
        if request.user.is_authenticated:
            proverbs = base_queryset.filter(likes=request.user)
        else:
            proverbs = Proverb.objects.none()
    elif tab == 'day':
        proverbs = base_queryset.filter(is_featured=True)
        if not proverbs.exists():
            first = base_queryset.order_by('?').first()
            proverbs = base_queryset.filter(id=first.id) if first else Proverb.objects.none()
    elif tab == 'popular':
        proverbs = base_queryset.order_by('-num_likes', '-created_at')
    else:
        proverbs = base_queryset

    if query:
        proverbs = proverbs.filter(
            Q(text__icontains=query) | Q(meaning__icontains=query)
        )

    if category_id:
        proverbs = proverbs.filter(categories__id=category_id)

    proverbs = proverbs.distinct()

    daily_proverb = base_queryset.filter(is_featured=True).first()
    if not daily_proverb:
        daily_proverb = base_queryset.order_by('?').first()

    categories = Category.objects.all()

    context = {
        'proverbs': proverbs,
        'query': query,
        'selected_category': category_id,
        'daily_proverb': daily_proverb,
        'categories': categories,
        'active_tab': tab,
    }

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render(request, 'ProverbsApp/partials/proverbs_list.html', context)

    return render(request, 'ProverbsApp/index.html', context)


def proverb_detail(request, proverb_id):
    proverb = get_object_or_404(Proverb.objects.annotate(
        comments_count=Count('comments', distinct=True)
    ), id=proverb_id, status='approved')

    comments = proverb.comments.select_related('user').all()
    comment_form = CommentForm()

    return render(request, 'ProverbsApp/proverb_detail.html', {
        'proverb': proverb,
        'comments': comments,
        'comment_form': comment_form,
    })


@login_required
def submit_proverb(request):
    if request.method == 'POST':
        form = ProverbSubmitForm(request.POST)
        if form.is_valid():
            proverb = form.save(commit=False)
            proverb.author = request.user
            proverb.status = 'pending'
            proverb.save()
            form.save_m2m()
            messages.success(request, "Пословица отправлена на модерацию.")
            return redirect('index')
    else:
        form = ProverbSubmitForm()

    return render(request, 'ProverbsApp/submit_proverb.html', {'form': form})

def toggle_like(request, pk):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "auth"}, status=403)

    proverb = Proverb.objects.get(pk=pk)

    if request.user in proverb.likes.all():
        proverb.likes.remove(request.user)
        liked = False
    else:
        proverb.likes.add(request.user)
        liked = True

    return JsonResponse({
        "liked": liked,
        "count": proverb.likes.count()
    })


@login_required
@require_POST
def add_comment(request, proverb_id):
    proverb = get_object_or_404(Proverb, id=proverb_id, status='approved')

    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.user = request.user
        comment.proverb = proverb
        comment.save()

        # Если AJAX — возвращаем JSON
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'username': comment.user.username,
                'text': comment.text,
                'created_at': comment.created_at.strftime('%d.%m.%Y %H:%M'),
                'comments_count': proverb.comments.count(),
            })

        messages.success(request, "Комментарий добавлен.")
    else:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'errors': form.errors
            }, status=400)

    return redirect('proverb_detail', proverb_id=proverb.id)


def category_detail(request, category_id):
    category = get_object_or_404(Category, pk=category_id)
    proverbs = category.proverbs.filter(status='approved')
    context = {
        'category': category,
        'proverbs': proverbs
    }
    return render(request, 'ProverbsApp/catergory_detail.html', context)


def quiz_view(request):
    questions = list(Proverb.objects.filter(status='approved').order_by('?')[:10])

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
        Proverb.objects.filter(status='approved').exclude(id=current_question.id)
        .values_list('meaning', flat=True)
        .distinct()
    )

    wrong_answers = random.sample(wrong_meanings, min(3, len(wrong_meanings)))

    options = [{'meaning': correct, 'is_correct': True}]
    for w in wrong_answers:
        options.append({'meaning': w, 'is_correct': False})

    random.shuffle(options)
    progress_percent = int((step / len(questions)) * 100)

    return render(request, 'ProverbsApp/quiz.html', {
        'question': current_question.text,
        'options': options,
        'step_number': step + 1,
        'total_steps': len(questions),
        'progress_percent': progress_percent
    })

def get_question(request):
    questions = list(Proverb.objects.all())
    proverb = random.choice(questions)

    options = list(proverb.options.all())
    random.shuffle(options)

    return JsonResponse({
        "id": proverb.id,
        "question": proverb.text,
        "options": [
            {"id": o.id, "text": o.meaning, "is_correct": o.is_correct}
            for o in options
        ]
    })

def check_answer(request):
    if request.method == "POST":
        is_correct = request.POST.get("is_correct") == "true"

        return JsonResponse({
            "correct": is_correct
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