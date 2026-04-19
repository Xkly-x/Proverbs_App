let score = 0;
let step = 0;
let total = 10;
let timer;
let timeLeft = 10;

function loadQuestion() {
    fetch('/quiz/question/')
    .then(res => res.json())
    .then(data => {
        document.getElementById('questionText').textContent = `«${data.question}»`;

        const answersDiv = document.getElementById('answers');
        answersDiv.innerHTML = '';

        data.options.forEach(opt => {
            const btn = document.createElement('button');
            btn.className = 'btn btn-outline-primary btn-lg';
            btn.textContent = opt.text;

            btn.onclick = () => handleAnswer(btn, opt.is_correct);

            answersDiv.appendChild(btn);
        });

        startTimer();
        updateProgress();
    });
}

function handleAnswer(btn, isCorrect) {
    clearInterval(timer);

    if (isCorrect) {
        btn.classList.add('btn-success');
        score++;
    } else {
        btn.classList.add('btn-danger');
    }

    setTimeout(() => {
        step++;

        if (step >= total) {
            showResult();
        } else {
            loadQuestion();
        }
    }, 700);
}

function startTimer() {
    timeLeft = 10;
    document.getElementById('timer').textContent = `⏱ ${timeLeft}`;

    timer = setInterval(() => {
        timeLeft--;
        document.getElementById('timer').textContent = `⏱ ${timeLeft}`;

        if (timeLeft <= 0) {
            clearInterval(timer);
            step++;

            if (step >= total) {
                showResult();
            } else {
                loadQuestion();
            }
        }
    }, 1000);
}

function updateProgress() {
    const percent = (step / total) * 100;
    document.getElementById('progressBar').style.width = percent + '%';
}

function showResult() {
    document.querySelector('.quiz-card').innerHTML = `
        <h1>🎉 Результат</h1>
        <h2>${score} / ${total}</h2>
        <button class="btn btn-primary mt-3" onclick="location.reload()">Ещё раз</button>
    `;
}

document.addEventListener('DOMContentLoaded', loadQuestion);
if (localStorage.getItem('theme') === 'dark') {
    document.documentElement.classList.add('dark-mode');
}
document.addEventListener('DOMContentLoaded', () => {
    const themeToggle = document.getElementById('theme-toggle');
    const body = document.body;
    const html = document.documentElement;

    if (localStorage.getItem('theme') === 'dark') {
        body.classList.add('dark-mode');
        html.classList.add('dark-mode');
    }

    if (themeToggle) {
        themeToggle.addEventListener('click', (e) => {
            e.preventDefault();
            body.classList.toggle('dark-mode');
            html.classList.toggle('dark-mode');

            if (body.classList.contains('dark-mode')) {
                localStorage.setItem('theme', 'dark');
            } else {
                localStorage.setItem('theme', 'light');
            }
        });
    }

    // Bootstrap tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Авто-сабмит аватарки
    const avatarInput = document.querySelector('input[type="file"]');
    if (avatarInput) {
        avatarInput.onchange = function() {
            this.closest('form').submit();
        };
    }

    // LIVE SEARCH
    const searchInput = document.getElementById('liveSearchInput');
    const categorySelect = document.getElementById('categorySelect');
    const searchForm = document.getElementById('searchForm');
    const proverbsContainer = document.getElementById('proverbsContainer');

    let searchTimeout;

    function loadFilteredProverbs() {
        if (!searchForm || !proverbsContainer) return;

        const formData = new FormData(searchForm);
        const params = new URLSearchParams(formData).toString();

        fetch(`/?${params}`, {
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.text())
        .then(html => {
            proverbsContainer.innerHTML = html;
            attachLikeHandlers();
        })
        .catch(error => console.error('Ошибка live search:', error));
    }

    if (searchInput) {
        searchInput.addEventListener('input', () => {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(loadFilteredProverbs, 300);
        });
    }

    if (categorySelect) {
        categorySelect.addEventListener('change', loadFilteredProverbs);
    }

    // AJAX лайки
    function attachLikeHandlers() {
    document.querySelectorAll('.like-btn').forEach(btn => {
        btn.onclick = function(e) {
            e.preventDefault();

            const proverbId = this.dataset.id;
            const likeButton = this;

            fetch(`/like/${proverbId}/`, {   // 🔥 ВАЖНО: единый URL
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCSRFToken(),
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => {
                if (response.status === 403) {
                    showAuthPopup();   // 🔥 если не авторизован
                    return;
                }

                if (!response.ok) {
                    throw new Error('Ошибка лайка');
                }

                return response.json();
            })
            .then(data => {
                if (!data) return;

                const likesCount = document.getElementById(`likes-count-${proverbId}`);
                const icon = likeButton.querySelector('.like-icon');

                if (likesCount) likesCount.textContent = data.count;
                if (icon) icon.textContent = data.liked ? '❤️' : '🤍';

                likeButton.classList.toggle('active', data.liked);
                })
            .catch(error => console.error('Ошибка лайка:', error));
            };
        });
    }

    // AJAX комментарии (на странице proverb_detail)
    function attachCommentHandlers() {
        document.querySelectorAll('.comment-form').forEach(form => {
            form.onsubmit = function(e) {
                e.preventDefault();

                const proverbId = this.dataset.id;
                const textarea = this.querySelector('textarea[name="text"]');
                const text = textarea.value.trim();

                if (!text) return;

                const formData = new FormData();
                formData.append('text', text);

                fetch(`/proverb/${proverbId}/comment/`, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': getCSRFToken(),
                        'X-Requested-With': 'XMLHttpRequest'
                    },
                    body: formData
                })
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Ошибка комментария');
                    }
                    return response.json();
                })
                .then(data => {
                    if (data.success) {
                        const commentsList = document.getElementById(`comments-list-${proverbId}`);
                        const commentsCount = document.getElementById(`comments-count-${proverbId}`);
                        const emptyComments = document.getElementById(`empty-comments-${proverbId}`);

                        if (commentsCount) commentsCount.textContent = `💬 ${data.comments_count}`;
                        if (emptyComments) emptyComments.remove();

                        const newComment = document.createElement('div');
                        newComment.className = 'border rounded p-3 mb-3 comment-item';
                        newComment.innerHTML = `
                            <div class="d-flex justify-content-between">
                                <strong>${data.username}</strong>
                                <small class="text-muted">${data.created_at}</small>
                            </div>
                            <p class="mb-0 mt-2">${data.text}</p>
                        `;

                        if (commentsList) {
                            commentsList.prepend(newComment);
                        }

                        textarea.value = '';
                    }
                })
                .catch(error => console.error('Ошибка комментария:', error));
            };
        });
    }

    function getCSRFToken() {
        const cookieValue = document.cookie
            .split('; ')
            .find(row => row.startsWith('csrftoken='));
        return cookieValue ? cookieValue.split('=')[1] : '';
    }

    attachLikeHandlers();
    attachCommentHandlers();
});

function animateQuestionChange(callback) {
    const quizCard = document.querySelector('.quiz-card');

    quizCard.classList.add('fade-out');

    setTimeout(() => {
        callback(); // меняем вопрос
        quizCard.classList.remove('fade-out');
        quizCard.classList.add('fade-in');

        setTimeout(() => {
            quizCard.classList.remove('fade-in');
        }, 400);
    }, 300);
}

function showAuthPopup() {
    document.getElementById('authPopup').classList.add('show');
}