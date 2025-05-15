document.addEventListener("DOMContentLoaded", () => {
  const apiElement = document.getElementById('api-url');
  const apiUrl = apiElement.dataset.url;
  const topicSlug = apiElement.dataset.topicSlug;
  const subtopicId = apiElement.dataset.subtopicId;

  const subtopicTitle = document.getElementById("subtopic-title");
  const exerciseContent = document.getElementById("exercise-content");
  const exerciseIndex = document.getElementById("exercise-index");
  const exerciseTotal = document.getElementById("exercise-total");
  const prevBtn = document.getElementById("prev-btn");
  const nextBtn = document.getElementById("next-btn");

  const transcriptList = document.getElementById("transcript-list");
  const fullAudio = document.getElementById("full-audio");
  const autoScroll = document.getElementById("auto-scroll");

  const slideText = document.getElementById("slide-text");
  const slideTrans = document.getElementById("slide-translation");
  const slideIndex = document.getElementById("slide-index");
  const slideTotal = document.getElementById("slide-total");
  const slidePrev = document.getElementById("slide-prev");
  const slideNext = document.getElementById("slide-next");

  let currentIndex = 0;
  let exercises = [];
  let currentTab = 'dictation';  // 👉 Mặc định khi load trang là Dictation

  const dictationTab = document.getElementById('dictation-tab');
  const transcriptTab = document.getElementById('transcript-tab');

  dictationTab.addEventListener('click', () => {
    currentTab = 'dictation';
  });

  transcriptTab.addEventListener('click', () => {
    currentTab = 'transcript';
  });

  fetch(apiUrl)
    .then((res) => res.json())
    .then((data) => {
      subtopicTitle.textContent = data.subtopic.title;
      exercises = data.exercises;

      exercises.unshift({
        is_intro: true,
        correct_text: data.subtopic.title,
        translation: "",
        timeStart: 0,
        timeEnd: 0,
        audioSrc: data.subtopic.full_audioSrc,
      });

      fullAudio.src = data.subtopic.full_audioSrc;
      currentIndex = 1;

      exerciseTotal.textContent = exercises.length - 1;
      slideTotal.textContent = exercises.length - 1;

      renderDictation();
      renderSlide();
      renderTranscript();

      prevBtn.onclick = () => {
        if (currentIndex > 1) currentIndex--;
        updateAll();
      };
      nextBtn.onclick = () => {
        if (currentIndex < exercises.length - 1) currentIndex++;
        updateAll();
      };
      slidePrev.onclick = prevBtn.onclick;
      slideNext.onclick = nextBtn.onclick;
    });

  function updateAll() {
    renderDictation();
    renderSlide();
    scrollToActiveTranscript();
  }

  function renderDictation() {
    const ex = exercises[currentIndex];
    exerciseIndex.textContent = currentIndex;

    if (ex.is_intro) {
      exerciseContent.innerHTML = `
        <div class="text-center mb-3">
          <h5 class="fw-bold">${ex.correct_text}</h5>
        </div>
        <audio controls class="w-50 mb-3">
          <source src="${ex.audioSrc}" type="audio/mp3">
        </audio>
      `;
    } else {
      exerciseContent.innerHTML = `
        <audio controls class="w-50 mb-3">
          <source src="${ex.audioSrc}" type="audio/mp3">
        </audio>
        <input type="text" id="user-answer" class="form-control mb-3 w-50" style="height: 60px; font-size: 20px;" placeholder="Type what you hear">
        <div id="answer-result" class="mt-2"></div>
        <div class="d-flex gap-2">
          <button class="btn btn-primary" id="check-answer-btn">Check</button>
          <button class="btn btn-outline-secondary" id="skip-btn">Skip</button>
        </div>
      `;

      document.getElementById("check-answer-btn").onclick = () => {
        const input = document.getElementById("user-answer");
        const userInputRaw = input.value.trim();
        const correctTextRaw = exercises[currentIndex].correct_text.trim();
      
        // Hàm normalize: bỏ dấu câu + thường hóa
        const normalize = (str) => str
          .replace(/[.,\/#!$%\^&\*;:{}=\-_`~()?"']/g, '')
          .replace(/\s+/g, ' ')
          .toLowerCase();
      
        const normalizedUser = normalize(userInputRaw);
        const normalizedCorrect = normalize(correctTextRaw);
      
        const userWords = normalizedUser.split(' ');
        const correctWords = normalizedCorrect.split(' ');
      
        const correctOriginalWords = correctTextRaw.split(/\s+/); // Phân tách bản gốc có dấu câu
      
        const resultDiv = document.getElementById("answer-result");
      
        let displayPartial = "";
        let allCorrect = true;
      
        for (let i = 0; i < correctWords.length; i++) {
          if (i < userWords.length && correctWords[i].startsWith(userWords[i])) {
            displayPartial += `<span style="color: green; font-weight: bold;">${correctOriginalWords[i]}</span> `;
          } else {
            displayPartial += "*".repeat(correctOriginalWords[i].length) + " ";
            allCorrect = false;
          }
        }
      
        displayPartial = displayPartial.trim();
      
        if (normalizedUser === normalizedCorrect) {
          // ✅ User nhập đúng hoàn toàn
          input.value = correctTextRaw; // Gán lại chính xác câu gốc
          input.classList.remove("is-invalid");
          input.classList.add("is-valid");
      
          resultDiv.innerHTML = `<span class="text-success fw-bold">✅ You are correct!</span>`;
      
          document.getElementById("check-answer-btn").classList.add("d-none");
          document.getElementById("skip-btn").classList.add("d-none");
      
          if (!document.getElementById("next-after-correct")) {
            const nextBtn = document.createElement("button");
            nextBtn.id = "next-after-correct";
            nextBtn.className = "btn btn-success";
            nextBtn.innerText = "Next";
            nextBtn.onclick = handleNextExercise;
            slidePrev.onclick = prevBtn.onclick;
            slideNext.onclick = handleNextExercise;
        
            const nextWrapper = document.createElement("div");
            nextWrapper.className = "d-flex mt-2";
            nextWrapper.appendChild(nextBtn);
        
            resultDiv.appendChild(nextWrapper);
          }
        } else {
          // ❌ User nhập chưa đúng hoàn toàn
          input.classList.remove("is-valid");
          input.classList.add("is-invalid");
      
          resultDiv.innerHTML = `
            <div class="text-warning fw-bold mb-2">⚠️ Incorrect</div>
            <div><small class="text-muted">Correct answer: <strong>${displayPartial}</strong></small></div>
          `;
        }
      };            
    }
  }

  function renderSlide() {
    const ex = exercises[currentIndex];
    slideIndex.textContent = currentIndex;
    slideText.textContent = ex.correct_text;
    slideTrans.textContent = ex.translation || "Bản dịch tiếng Việt";
  }

  function renderTranscript() {
    transcriptList.innerHTML = "";
    exercises.forEach((ex, idx) => {
      if (idx === 0) return;
      const li = document.createElement("li");
      li.classList.add("list-group-item");
      li.dataset.index = idx;
      li.innerHTML = `
        <div class="d-flex align-items-center mb-1">
          <button class="btn btn-sm btn-outline-primary me-2 play-btn">
            <i class="bi bi-play-fill"></i>
          </button>
          <strong>${ex.correct_text}</strong>
        </div>
        <small class="text-muted">${ex.translation || "Bản dịch tiếng Việt"}</small>
      `;
      const btn = li.querySelector(".play-btn");
      btn.onclick = () => {
        fullAudio.currentTime = ex.timeStart;
        fullAudio.play();
        currentIndex = idx;
        updateAll();
      };
      transcriptList.appendChild(li);
    });
  }

  function scrollToActiveTranscript() {
    if (currentIndex === 0) return;
    const el = transcriptList.children[currentIndex - 1];
    if (el && autoScroll.checked) {
      transcriptList.scrollTo({
        top: el.offsetTop - transcriptList.clientHeight / 2 + el.clientHeight / 2,
        behavior: "smooth",
      });
    }
  }

  function handleNextExercise() {
    if (currentIndex < exercises.length - 1) {
      currentIndex++;
      updateAll();
    } else {
      // Câu cuối ➔ Show completion screen
      fetch(`/api/topics/listen/${topicSlug}/subtopics/${subtopicId}/next-prev/`)
        .then(res => res.json())
        .then(data => {
          renderCompletionScreen(data.previous, data.next);
        })
        .catch(error => {
          console.error('Error fetching next subtopic:', error);
        });
    }
  }  
  
  function renderCompletionScreen(previousSubtopic, nextSubtopic) {
    exerciseContent.innerHTML = `
      <div class="text-center p-5">
        <h2 class="mb-3">You have completed this exercise,<br>good job!</h2>
        <div class="mb-4">
          <i class="bi bi-check-circle-fill" style="font-size: 4rem; color: green;"></i>
        </div>
        <div class="d-flex justify-content-center gap-3 mb-4">
          ${previousSubtopic ? `<button id="prev-exercise" class="btn btn-outline-primary">Previous Exercise</button>` : ''}
          ${nextSubtopic ? `<button id="next-exercise" class="btn btn-primary">Next Exercise</button>` : ''}
          <button id="repeat-exercise" class="btn btn-outline-secondary">Repeat this exercise</button>
        </div>
        <div>
          <a href="/topics/listen/${topicSlug}/" class="text-decoration-underline">View all exercises</a>
        </div>
      </div>
    `;
  
    if (previousSubtopic) {
      document.getElementById("prev-exercise").onclick = () => {
        window.location.href = previousSubtopic.url;
      };
    }
  
    if (nextSubtopic) {
      document.getElementById("next-exercise").onclick = () => {
        window.location.href = nextSubtopic.url;
      };
    }
  
    document.getElementById("repeat-exercise").onclick = () => {
      currentIndex = 1;
      updateAll();
    };
  }
  
  

  fullAudio.ontimeupdate = () => {
    const currentTime = fullAudio.currentTime;
    exercises.forEach((ex, idx) => {
      if (idx === 0) return;
      const item = transcriptList.children[idx - 1];
      if (currentTime >= ex.timeStart && currentTime <= ex.timeEnd) {
        item.classList.add("active");
        if (currentIndex !== idx) {
          currentIndex = idx;
          renderSlide();
          exerciseIndex.textContent = idx;
          if (autoScroll.checked) scrollToActiveTranscript();
        }
      } else {
        item.classList.remove("active");
      }
    });
  };

  document.addEventListener("keydown", (e) => {
    if (e.code === "Space") {
      if (currentTab === 'transcript') {
        e.preventDefault();
        fullAudio.paused ? fullAudio.play() : fullAudio.pause();
      }
    } else if (e.code === "ArrowLeft") {
      slidePrev.click();
    } else if (e.code === "ArrowRight") {
      slideNext.click();
    }
  });
});
