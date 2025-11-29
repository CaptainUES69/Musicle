// Глобальные переменные
let selectedDifficulty = '';
let selectedArtist = '';

// Функция выбора исполнителя
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

// Функция возврата к выбору исполнителя
function backToArtist() {
    // Скрываем экран выбора сложности
    document.getElementById('difficultyScreen').style.display = 'none';
    
    // Показываем экран выбора исполнителя
    document.getElementById('artistScreen').style.display = 'flex';
    
    // Очищаем поле ввода исполнителя (опционально)
    // document.getElementById('artistInput').value = '';
    // document.getElementById('artistMessage').textContent = '';
}

// Функция начала квиза
function startQuiz(difficulty) {
    selectedDifficulty = difficulty;
    
    // Отправляем сложность на сервер 
    sendDifficultyToServer(difficulty);
    
    // Скрываем экран выбора сложности
    document.getElementById('difficultyScreen').style.display = 'none';
    
    // Показываем основной интерфейс квиза
    document.getElementById('quizScreen').style.display = 'block';
    
    // Инициализируем квиз
    initializeQuiz();
}

// Функция отправки сложности на сервер
function sendDifficultyToServer(difficulty) {

    console.log('Начат взлом пентагона...', difficulty);
    
}

// Функция инициализации квиза (переносим сюда код из предыдущей инициализации)
function initializeQuiz() {
    // Загружаем первый трек
    loadTrack(currentTrackIndex);
    
    // Устанавливаем начальную громкость
    audio.volume = volumeSlider.value;
}


// Список всех треков
const trackList = [
    { name: "Трек 1", file: "example.mp3", correctAnswer: "ты че" },
    { name: "Трек 2", file: "example2.mp3", correctAnswer: "i love"  },
    { name: "Трек 3", file: "example3.mp3", correctAnswer: "травма"  },
    { name: "Трек 4", file: "example4.mp3", correctAnswer: "new"  },
    { name: "Трек 5", file: "example5.mp3", correctAnswer: "mashup"  }
];

// Текущий индекс трека
let currentTrackIndex = 0;

// Получаем доступ к элементам
const audio = document.getElementById("myAudio");
const progressBar = document.getElementById("audioProgress");
const trackNameElement = document.getElementById("currentTrackName");
const volumeSlider = document.getElementById("volumeSlider");
const volumeValue = document.getElementById("volumeValue");
const answerInput = document.getElementById("answer");
const answerMessage = document.getElementById("answerMessage");

// Функция загрузки трека
function loadTrack(trackIndex) {
    const track = trackList[trackIndex];
    audio.src = track.file;
    
    if (trackNameElement) {
        trackNameElement.textContent = track.name;
    }
    
    // Сбрасываем прогресс-бар
    if (progressBar) {
        progressBar.value = 0;
    }
    
    // Загружаем новый трек
    audio.load();
}

// Функция показа/скрытия кнопки "Начать заново"
function toggleRestartButton(show) {
    const restartBtn = document.getElementById("restartButton");
    if (restartBtn) {
        restartBtn.style.display = show ? "block" : "none";
    }
}

// Функция начала квиза заново (возврат к выбору сложности)
function restartQuiz() {
    // Скрываем интерфейс квиза
    document.getElementById('quizScreen').style.display = 'none';
    
    // Показываем экран выбора сложности
    document.getElementById('difficultyScreen').style.display = 'flex';
    
    // Сбрасываем состояние квиза
    currentTrackIndex = 0;
    answerInput.value = "";
    answerMessage.textContent = "";
    answerInput.disabled = false;
    
    // Останавливаем воспроизведение
    audio.pause();
    audio.currentTime = 0;
    
    // Скрываем кнопку рестарт
    toggleRestartButton(false);
}

// Инициализация - загружаем первый трек
loadTrack(currentTrackIndex);

// Установка начальной громкости
audio.volume = volumeSlider.value;

// Функция регулировки громкости
function changeVolume(value) {
    audio.volume = value;
    volumeValue.textContent = Math.round(value * 100) + '%';
}

// Функция воспроизведения
function playAudio() {
    audio.play();
}

// Функция паузы
function pauseAudio() {
    audio.pause();
}

// Функция перезапуска текущего трека
function restartAudio() {
    audio.currentTime = 0;
    audio.play();
}

// Функция проверки кода и перехода к следующему треку
function checkAnswer() {
    const userInput = answerInput.value.trim().toLowerCase().replace(/\s+/g, ' ');
    const currentTrack = trackList[currentTrackIndex];
    const correctAnswer = currentTrack.correctAnswer.toLowerCase().trim();
    
    if (userInput === correctAnswer) {
        // Ответ правильный
        
        // Проверяем, не последний ли это трек
        if (currentTrackIndex === trackList.length - 1) {
            // Это последний трек - показываем кнопку "Начать заново"
            answerMessage.textContent = "Поздравляем! Вы угадали все треки!";
            answerMessage.style.color = "green";
            toggleRestartButton(true); // Показываем кнопку
            answerInput.disabled = true; // Блокируем поле ввода
            
            // Останавливаем воспроизведение
            audio.pause();
        } else {
            // Не последний трек - переходим к следующему
            currentTrackIndex++;
            loadTrack(currentTrackIndex);
            audio.play();
            
            answerMessage.textContent = "Ответ верный! Следующий..";
            answerMessage.style.color = "green";
        }
        
        // Очищаем поле ввода
        answerInput.value = "";
        
    } else {
        // Ответ неправильный
        answerMessage.textContent = "Неверный ответ! Попробуйте снова.";
        answerMessage.style.color = "red";
    }
    
    // Очищаем сообщение через 2 секунды (кроме финального)
    if (currentTrackIndex !== trackList.length - 1) {
        setTimeout(() => {
            answerMessage.textContent = "";
        }, 2000);
    }
}