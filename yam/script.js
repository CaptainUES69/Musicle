// ======================
// API CONFIGURATION
// ======================
const API_BASE_URL = 'http://localhost:8000';   // адрес вашего FastAPI сервера
let currentAudioUrl = null;                      // для освобождения памяти
let isLoading = false;

// Глобальные переменные
let selectedDifficulty = '';
let selectedArtist = '';
let totalScore = 0;               // общее количество очков
let currentTimer = null;          // идентификатор таймера
let startTime = null;             // время начала ответа (в миллисекундах)
const MIN_SCORE = 10;             // минимальное количество очков за ответ
let scoreShareSent = false;   // флаг: был ли результат уже отправлен
// Названия сложностей
const difficultyNames = {
    'easy': 'Легкий',
    'medium': 'Средний', 
    'hard': 'Сложный'
};
// Цвета сложностей
const difficultyColors = {
    'easy': 'difficulty-easy',
    'medium': 'difficulty-medium',
    'hard': 'difficulty-hard'
};

window.addEventListener('beforeunload', function() {
    console.log('>>> Страница перезагружается!');
    console.trace(); // покажет стек вызовов
    debugger;
});

window.addEventListener('error', (e) => {
    console.error('Глобальная ошибка:', e.error);
    debugger;
});


window.addEventListener('unhandledrejection', (e) => {
    console.error('Необработанный промис:', e.reason);
    debugger;
});

const DEFAULT_ROUNDS = 5;   // количество треков в квизе (можно будет менять)

function getLengthMsForDifficulty(difficulty) {
    switch (difficulty) {
        case 'easy': return 10000;   // 10 секунд
        case 'medium': return 6000;  // 6 секунд
        case 'hard': return 2000;    // 2 секунды
        default: return 10000;
    }
}

// Функция выбора исполнителя (без проверки на сервере)
function selectArtist() {
    const artistInput = document.getElementById('artistInput');
    const artistMessage = document.getElementById('artistMessage');
    const artistName = artistInput.value.trim();
    
    if (artistName === '') {
        artistMessage.textContent = 'Пожалуйста, введите имя исполнителя';
        artistMessage.style.color = 'red';
        return;
    }
    
    // Сохраняем выбранного исполнителя
    selectedArtist = artistName;
    
    // Переходим к выбору сложности
    document.getElementById('artistScreen').style.display = 'none';
    document.getElementById('difficultyScreen').style.display = 'flex';
    
    // Очищаем сообщения
    artistMessage.textContent = '';
}

// Обработка клавиши Enter в поле исполнителя
document.getElementById('artistInput').addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        selectArtist();
    }
});

async function checkArtistOnServer(artistName) {
    const url = `${API_BASE_URL}/check-artist/${encodeURIComponent(artistName)}`;
    const response = await fetch(url);
    if (!response.ok) {
        if (response.status === 404) {
            throw new Error('Исполнитель не найден');
        }
        throw new Error(`Ошибка сервера: ${response.status}`);
    }
    // Можно вернуть данные, если нужно
    return await response.json(); // например, { artistId: 123, name: "The Beatles" }
}

// Функция возврата к выбору исполнителя
function backToArtist() {
    sessionStorage.removeItem('continueIds');
    document.getElementById('difficultyScreen').style.display = 'none';
    document.getElementById('artistScreen').style.display = 'flex';
}

async function startQuiz(difficulty) {
    selectedDifficulty = difficulty;

    // Если есть сохранённые ID для continue – используем их
    const continueIds = sessionStorage.getItem('continueIds');
    let usedIds = null;
    if (continueIds) {
        usedIds = JSON.parse(continueIds);
        sessionStorage.removeItem('continueIds');
    }

    try {
        await fetchTracks(selectedArtist, difficulty, usedIds);
    } catch (error) {
        return;
    }

    // Переключение экранов, обновление счёта, загрузка первого трека...
    document.getElementById('difficultyScreen').style.display = 'none';
    document.getElementById('quizScreen').style.display = 'block';
    updateDifficultyDisplay(difficulty);
    totalScore = 0;
    updateScoreDisplay();
    scoreShareSent = false;
    await loadTrack(0);
}

// Обновление отображения сложности
function updateDifficultyDisplay(difficulty) {
    const displayElement = document.getElementById('selectedDifficultyDisplay');
    
    if (displayElement) {
        // Устанавливаем текст
        displayElement.textContent = difficultyNames[difficulty] || 'Неизвестно';
        
        // Устанавливаем класс для цвета
        displayElement.className = ''; // Очищаем предыдущие классы
        displayElement.classList.add(difficultyColors[difficulty] || '');
    }
}

// Функция получения сложности с сервера
function getMetadataEndpoint(artist, difficulty) {
    const lengthMs = getLengthMsForDifficulty(difficulty);
    // Используем encodeURIComponent для artist
    return `${API_BASE_URL}/tracks/get_tracks/${encodeURIComponent(artist)}?rounds=${DEFAULT_ROUNDS}&length_ms=${lengthMs}`;
}

// Список треков (будет заполнен с сервера)
let trackList = [];

// Текущий индекс трека
let currentTrackIndex = 0;

// Функция загрузки метаданных треков с сервера
async function fetchTracks(artist, difficulty, usedIds = null) {
    try {
        let response;
        if (usedIds && usedIds.length > 0) {
            const lengthMs = getLengthMsForDifficulty(difficulty);
            const body = {
                repeats: usedIds,
                rounds: DEFAULT_ROUNDS,
                length_ms: lengthMs
            };
            response = await fetch(`${API_BASE_URL}/tracks/continue/${encodeURIComponent(artist)}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(body)
            });
        } else {
            const url = getMetadataEndpoint(artist, difficulty);
            response = await fetch(url);
        }

        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);

        const tracksData = await response.json();
        trackList = tracksData.map(item => ({
            id: item.track_id,           // сохраняем track_id
            name: item.title,
            snippetUrl: item.snippet_url,
            correctAnswer: item.title
        }));
        console.log('Загружено треков:', trackList.length);
    } catch (error) {
        // обработка ошибок (оставляем как было)
    }
}

// Функция загрузки аудиофайла
async function loadAudioFromServer(snippetUrl) {
    console.log('🔹 loadAudioFromServer start');
    const fullUrl = `${API_BASE_URL}${snippetUrl}`;
    const response = await fetch(fullUrl);
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const blob = await response.blob();
    return URL.createObjectURL(blob);
}

// Получаем доступ к элементам
const audio = document.getElementById("myAudio");
const progressBar = document.getElementById("audioProgress");
const volumeSlider = document.getElementById("volumeSlider");
const volumeValue = document.getElementById("volumeValue");
const answerInput = document.getElementById("answer");
const answerMessage = document.getElementById("answerMessage");
const loadingIndicator = document.getElementById('loadingIndicator');
const timerElement = document.getElementById('timerValue');
const scoreElement = document.getElementById('scoreValue');
const resultScreen = document.getElementById('resultScreen');
const finalScoreSpan = document.getElementById('finalScore');
const finalDifficultySpan = document.getElementById('finalDifficulty');
const finalArtistSpan = document.getElementById('finalArtist');

audio.addEventListener('loadstart', () => console.log('🎵 loadstart'));
audio.addEventListener('loadedmetadata', () => console.log('🎵 loadedmetadata'));
audio.addEventListener('loadeddata', () => console.log('🎵 loadeddata'));
audio.addEventListener('canplay', () => console.log('🎵 canplay'));
audio.addEventListener('error', (e) => console.error('🎵 error', e));
audio.addEventListener('stalled', () => console.log('🎵 stalled'));
audio.addEventListener('suspend', () => console.log('🎵 suspend'));

audio.addEventListener('error', (e) => {
    console.error('Audio element error:', e);
    console.error('Audio error code:', audio.error ? audio.error.code : 'unknown');
});
audio.addEventListener('timeupdate', function() {
    if (audio.duration) {
        const progress = (audio.currentTime / audio.duration) * 100;
        if (progressBar) progressBar.value = progress;
    }
});

// Функция загрузки трека
async function loadTrack(trackIndex) {
    console.log('🔸 loadTrack start, index:', trackIndex);
    isLoading = true;
    if (loadingIndicator) loadingIndicator.classList.remove('hidden'); // показать индикатор

    const track = trackList[trackIndex];
    if (!track) {
        console.error('track not found');
        if (loadingIndicator) loadingIndicator.classList.add('hidden');
        isLoading = false;
        return;
    }

    audio.pause();
    audio.removeAttribute('src');
    audio.load();

    if (currentAudioUrl) {
        URL.revokeObjectURL(currentAudioUrl);
        currentAudioUrl = null;
    }

    if (progressBar) progressBar.value = 0;

    try {
        const audioUrl = await loadAudioFromServer(track.snippetUrl);
        currentAudioUrl = audioUrl;
        audio.src = audioUrl;

        // Ждём canplay
        await new Promise((resolve, reject) => {
            const onCanPlay = () => {
                audio.removeEventListener('canplay', onCanPlay);
                audio.removeEventListener('error', onError);
                resolve();
            };
            const onError = (e) => {
                audio.removeEventListener('canplay', onCanPlay);
                audio.removeEventListener('error', onError);
                reject(new Error('Audio failed to load'));
            };
            audio.addEventListener('canplay', onCanPlay);
            audio.addEventListener('error', onError);
        });

        console.log('loadTrack finished, ready to play');
    } catch (error) {
        console.error('loadTrack error:', error);
    } finally {
        isLoading = false;
        if (loadingIndicator) loadingIndicator.classList.add('hidden'); // скрыть индикатор
    }
}



// Функция для обновления счёта на экране
function updateScoreDisplay() {
    if (scoreElement) scoreElement.textContent = totalScore;
}

// Функция остановки таймера
function stopTimer() {
    if (currentTimer) {
        clearInterval(currentTimer);
        currentTimer = null;
    }
    startTime = null;
}

// Функция начала таймера
function startTimer(maxTime) {
    stopTimer(); // останавливаем предыдущий таймер, если был
    startTime = Date.now();

    currentTimer = setInterval(() => {
        if (startTime) {
            const elapsed = (Date.now() - startTime) / 1000; // прошедшие секунды
            // Ограничиваем отображение максимальным временем (чтобы не уходило в минус)
            const displayTime = Math.min(elapsed, maxTime).toFixed(1);
            if (timerElement) timerElement.textContent = displayTime;
        }
    }, 100); // обновляем 10 раз в секунду
}

// Функция вычисления очков от времени
function calculateScore(elapsedSeconds, maxTime) {
    if (elapsedSeconds > maxTime) return MIN_SCORE; // если время вышло, даём минимум
    // Линейная шкала: 100 баллов за 0 сек, 10 баллов за maxTime сек
    // Формула: баллы = max(10, 100 * (1 - elapsed / maxTime))
    let score = Math.round(100 * Math.pow(1 - elapsedSeconds / maxTime, 0.5));
    return Math.max(MIN_SCORE, score);
}

// Функция получения максимального времени для сложности
function getMaxTimeForDifficulty(difficulty) {
    return 15;
}

// Функция регулировки громкости
function changeVolume(value) {
    audio.volume = value;
    volumeValue.textContent = Math.round(value * 100) + '%';
}

// Функция воспроизведения
function playAudio() {
    if (isLoading) {
        console.log('Аудио ещё загружается, подождите');
        return;
    }
    audio.play().catch(e => console.error('play error:', e));
    // Запускаем таймер, если ещё не запущен
    if (!currentTimer && !isLoading && audio.src) {
        startTimer(getMaxTimeForDifficulty(selectedDifficulty));
    }
}


// Функция скипа
function skipTrack() {
    if (isLoading) {
        console.log('Аудио ещё загружается, подождите');
        return;
    }

    // Останавливаем таймер (без начисления очков)
    stopTimer();

    // Проверяем, последний ли трек
    if (currentTrackIndex === trackList.length - 1) {
        // Завершаем квиз, показываем финальный экран
        showResultScreen();
    } else {
        // Переход к следующему треку
        currentTrackIndex++;
        answerMessage.textContent = "Трек пропущен";
        answerMessage.style.color = "orange";
        setTimeout(() => answerMessage.textContent = "", 1500);

        // Загружаем новый трек (поле ввода автоматически заблокируется в loadTrack)
        loadTrack(currentTrackIndex).then(() => {
            // Не запускаем воспроизведение автоматически – ждём нажатия "Старт"
            // Таймер не запускается до нажатия "Старт"
        });
    }
    answerInput.value = "";
}

// Функция перезапуска текущего трека
function restartAudio() {
    if (isLoading) return;
    audio.currentTime = 0;
    audio.play().catch(e => console.error('play error:', e));
}

// Функция проверки кода и перехода к следующему треку
async function checkAnswer() {
    const userInput = answerInput.value.trim();
    const currentTrack = trackList[currentTrackIndex];
    const correctAnswer = currentTrack.correctAnswer;

    // Нормализация
    const normalize = (s) => {
        return s
            .toLowerCase()
            .replace(/[^a-zа-яё0-9]/gi, '')
            .replace(/ё/g, 'е');
    };

    const normalizedInput = normalize(userInput);
    const normalizedCorrect = normalize(correctAnswer);

    const minInputLength = (normalizedCorrect.length === 1) ? 1 : 2;
    if (normalizedCorrect.includes(normalizedInput) && normalizedInput.length >= minInputLength) {
        // 1. Сначала вычисляем прошедшее время, используя текущий startTime
        let elapsed = 0;
        if (startTime) {
            elapsed = (Date.now() - startTime) / 1000;
        }

        // 2. Останавливаем таймер (после того, как считали время)
        stopTimer();

        const maxTime = getMaxTimeForDifficulty(selectedDifficulty);
        if (elapsed > maxTime) elapsed = maxTime;

        const earnedScore = calculateScore(elapsed, maxTime);
        totalScore += earnedScore;
        updateScoreDisplay();

        console.log(`Время: ${elapsed.toFixed(1)} сек, заработано: ${earnedScore} баллов`);

        // Проверяем, последний ли трек
        if (currentTrackIndex === trackList.length - 1) {
            // Показываем финальный экран с результатами
            showResultScreen();
        }
        else {
            // Переход к следующему треку
            currentTrackIndex++;
            answerMessage.textContent = `Ответ верный! +${earnedScore} очков. Следующий..`;
            answerMessage.style.color = "green";
            await loadTrack(currentTrackIndex);
            if (!isLoading) {
                playAudio(); // запускаем воспроизведение и таймер
            }
        }
        answerInput.value = "";
    } else {
        answerMessage.textContent = "Неверный ответ! Попробуйте снова.";
        answerMessage.style.color = "red";
        // Таймер продолжает идти
    }

    if (currentTrackIndex !== trackList.length - 1) {
        setTimeout(() => answerMessage.textContent = "", 2000);
    }
}

// обработка Enter для поля ответа
document.getElementById('answer').addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        checkAnswer();
    }
});

function simpleConfetti() {
    const colors = ['#d88f06', '#eeaf3b', '#4CAF50', '#ff9800', '#ffcc00'];
    for (let i = 0; i < 100; i++) {
        const conf = document.createElement('div');
        conf.style.position = 'fixed';
        conf.style.width = Math.random() * 8 + 4 + 'px';
        conf.style.height = conf.style.width;
        conf.style.backgroundColor = colors[Math.floor(Math.random() * colors.length)];
        conf.style.borderRadius = '50%';
        conf.style.left = Math.random() * window.innerWidth + 'px';
        conf.style.top = '-20px';
        conf.style.zIndex = '10000';
        conf.style.pointerEvents = 'none';
        conf.style.opacity = '0.8';
        document.body.appendChild(conf);

        const duration = Math.random() * 2000 + 1500;
        const startTime = performance.now();
        const startLeft = parseFloat(conf.style.left);
        const drift = (Math.random() - 0.5) * 100;

        function animate(now) {
            const elapsed = now - startTime;
            const progress = Math.min(elapsed / duration, 1);
            const top = -20 + progress * (window.innerHeight + 20);
            const left = startLeft + drift * progress;
            conf.style.top = top + 'px';
            conf.style.left = left + 'px';
            conf.style.opacity = 1 - progress;
            if (progress < 1) {
                requestAnimationFrame(animate);
            } else {
                conf.remove();
            }
        }
        requestAnimationFrame(animate);
    }
}

// функция для показа экрана с результатом
function showResultScreen() {
    stopTimer();
    audio.pause();

    finalScoreSpan.textContent = totalScore;
    finalDifficultySpan.textContent = difficultyNames[selectedDifficulty] || selectedDifficulty;
    finalArtistSpan.textContent = selectedArtist || 'Неизвестно';

    document.getElementById('quizScreen').style.display = 'none';
    resultScreen.style.display = 'flex';

    simpleConfetti();
}

// перезапуск с экрана результата
function restartFromResult() {
    // Сохраняем ID всех треков текущего раунда
    const ids = trackList.map(track => track.id);
    sessionStorage.setItem('continueIds', JSON.stringify(ids));

    // Скрываем результат и показываем экран сложности
    resultScreen.style.display = 'none';
    document.getElementById('difficultyScreen').style.display = 'flex';

    // Сбрасываем состояние плеера и переменные
    if (currentAudioUrl) {
        URL.revokeObjectURL(currentAudioUrl);
        currentAudioUrl = null;
    }
    currentTrackIndex = 0;
    answerInput.value = "";
    answerMessage.textContent = "";
    answerInput.disabled = false;
    audio.pause();
    audio.currentTime = 0;
    totalScore = 0;
    updateScoreDisplay();
    if (timerElement) timerElement.textContent = '0.0';
    stopTimer();
    scoreShareSent = false;
}

function backToArtistFromResult() {
    // Возврат к выбору исполнителя
    resultScreen.style.display = 'none';
    document.getElementById('artistScreen').style.display = 'flex';
    
    // Сбрасываем состояние
    if (currentAudioUrl) {
        sessionStorage.removeItem('continueIds');
        resultScreen.style.display = 'none';
        document.getElementById('artistScreen').style.display = 'flex';
        URL.revokeObjectURL(currentAudioUrl);
        currentAudioUrl = null;
    }
    currentTrackIndex = 0;
    answerInput.value = "";
    answerMessage.textContent = "";
    answerInput.disabled = false;
    audio.pause();
    audio.currentTime = 0;
    totalScore = 0;
    updateScoreDisplay();
    if (timerElement) timerElement.textContent = '0.0';
}

// === Функции для модальных окон и лидерборда ===

function openShareModal() {
    if (scoreShareSent) {
        alert('Вы уже поделились этим результатом!');
        return;
    }
    document.getElementById('shareModal').style.display = 'flex';
    document.getElementById('playerAlias').value = '';
    document.getElementById('aliasError').style.display = 'none';
}

function closeShareModal() {
    document.getElementById('shareModal').style.display = 'none';
}

function closeLeaderboardModal() {
    document.getElementById('leaderboardModal').style.display = 'none';
}

async function submitScore() {
    if (scoreShareSent) {
        alert('Результат уже был отправлен.');
        closeShareModal();
        return;
    }

    const aliasInput = document.getElementById('playerAlias');
    let alias = aliasInput.value.trim().toUpperCase();
    const aliasError = document.getElementById('aliasError');

    const regex = /^[A-Z0-9]{4}$/;
    if (!regex.test(alias)) {
        aliasError.style.display = 'block';
        return;
    }
    aliasError.style.display = 'none';

    const difficultyMap = {
        'easy': 'Easy',
        'medium': 'Medium',
        'hard': 'Hard'
    };
    const formattedDifficulty = difficultyMap[selectedDifficulty] || 'Unknown';

    const scoreData = {
        nickname: alias,
        artist: selectedArtist,
        difficulty: formattedDifficulty,
        score: totalScore
    };

    try {
        const response = await fetch(`${API_BASE_URL}/leaderboard/user`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(scoreData)
        });

        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`Ошибка ${response.status}: ${errorText}`);
        }

        const result = await response.json();
        console.log('Результат сохранён:', result);
        scoreShareSent = true;
        alert(`Спасибо, ${alias}! Ваш результат сохранён.`);
    } catch (error) {
        console.error('Ошибка при отправке результата:', error);
        alert('Не удалось сохранить результат. Попробуйте позже.');
    } finally {
        closeShareModal();
    }
}

async function showLeaderboard() {
    const leaderboardList = document.getElementById('leaderboardList');
    leaderboardList.innerHTML = '<div style="text-align:center">Загрузка...</div>';
    document.getElementById('leaderboardModal').style.display = 'flex';

    try {
        const url = `${API_BASE_URL}/leaderboard/top_artist/${encodeURIComponent(selectedArtist)}?limit=10`;
        const response = await fetch(url);

        if (!response.ok) {
            throw new Error(`Ошибка ${response.status}`);
        }

        const data = await response.json();

        // Поддерживаем два возможных формата: прямой массив или объект с полем leaderboard
        let items = Array.isArray(data) ? data : (data.leaderboard || []);

        if (items.length === 0) {
            leaderboardList.innerHTML = '<div>Нет результатов для этого исполнителя</div>';
            return;
        }

        const leaderboardHtml = items.slice(0, 10).map((item, idx) => {
            const rank = item.rank || (idx + 1);
            const alias = item.nickname || item.alias || '???';
            const score = item.score || 0;
            return `<div class="leaderboard-item">
                        <span>${rank}. ${alias}</span>
                        <span>${score} 🏆</span>
                    </div>`;
        }).join('');

        leaderboardList.innerHTML = leaderboardHtml;
    } catch (error) {
        console.error('Ошибка загрузки лидерборда:', error);
        leaderboardList.innerHTML = '<div>Ошибка загрузки таблицы лидеров</div>';
    }
}
// инициализация квиза после загрузки страницы
document.addEventListener('DOMContentLoaded', function() {
    audio.volume = volumeSlider.value;
    volumeSlider.style.setProperty('--fill-percent', volumeSlider.value * 100 + '%');
    console.log('Приложение готово');
});

volumeSlider.addEventListener('input', (e) => {
    const val = e.target.value;
    audio.volume = val;
    volumeValue.textContent = Math.round(val * 100) + '%';
    // Обновляем CSS-переменную для прогресса
    volumeSlider.style.setProperty('--fill-percent', val * 100 + '%');
});