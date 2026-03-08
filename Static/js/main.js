document.addEventListener("DOMContentLoaded", function() {
    const themeBtn = document.getElementById("theme-toggle");
    const body = document.body;

    // Проверка темы при загрузке
    if (localStorage.getItem("theme") === "dark") {
        body.classList.add("dark-mode");
        if (themeBtn) themeBtn.innerHTML = "☀️";
    }

    // Переключение темы
    if (themeBtn) {
        themeBtn.addEventListener("click", function() {
            body.classList.toggle("dark-mode");
            const isDark = body.classList.contains("dark-mode");
            localStorage.setItem("theme", isDark ? "dark" : "light");
            themeBtn.innerHTML = isDark ? "☀️" : "🌙";
        });
    }

    // Анимация нажатия на кнопки викторины
    const form = document.querySelector('form');
    if (form) {
        form.addEventListener('submit', function() {
            // Можно добавить какой-нибудь индикатор загрузки, если интернет медленный
            const buttons = form.querySelectorAll('button');
            buttons.forEach(btn => btn.classList.add('disabled'));
        });
    }
});

document.getElementById('avatar-input').onchange = function () {
    const label = document.querySelector('label[for="avatar-input"]');
    if (this.files && this.files.length > 0) {
        label.innerText = "📄 Файл выбран";
        label.classList.replace('btn-outline-primary', 'btn-primary');
    }
};

