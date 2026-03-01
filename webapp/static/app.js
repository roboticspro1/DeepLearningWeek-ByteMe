const state = {
  dashboard: null,
  topics: [],
  studentState: [],
  charts: {
    radar: null,
    accuracy: null,
    speed: null,
  },
};

const navButtons = [...document.querySelectorAll('.nav-btn')];
const views = [...document.querySelectorAll('.view')];
const apiKeyInput = document.getElementById('apiKey');

function apiKey() {
  return apiKeyInput.value.trim();
}

function switchView(viewId) {
  views.forEach((view) => view.classList.toggle('active-view', view.id === viewId));
  navButtons.forEach((btn) => btn.classList.toggle('active', btn.dataset.view === viewId));
}

navButtons.forEach((btn) => {
  btn.addEventListener('click', () => switchView(btn.dataset.view));
});

async function getJSON(url) {
  const response = await fetch(url);
  if (!response.ok) throw new Error('Failed API call');
  return response.json();
}

async function postJSON(url, body) {
  const response = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(data.detail || 'Request failed');
  }
  return data;
}

function renderUrgentTopics(urgent) {
  const container = document.getElementById('urgentList');
  container.innerHTML = '';

  if (!urgent.length) {
    container.innerHTML = '<p>No urgent friction detected.</p>';
    return;
  }

  urgent.forEach((item) => {
    const block = document.createElement('div');
    block.className = 'topic-card';
    block.style.borderLeftColor = item.color;
    block.innerHTML = `
      <strong>${item.topic}</strong>
      <p><strong>Diagnosis:</strong> ${item.diagnosis}</p>
      <p><strong>Recent:</strong> ${item.recent_mastery_pct}% | <strong>Overall:</strong> ${item.mastery_pct}%</p>
      <p><strong>Urgency:</strong> ${item.urgency}</p>
    `;
    container.appendChild(block);
  });
}

function createOrUpdateChart(name, canvasId, config) {
  const ctx = document.getElementById(canvasId);
  if (state.charts[name]) {
    state.charts[name].destroy();
  }
  state.charts[name] = new Chart(ctx, config);
}

function renderRadarChart(radar) {
  createOrUpdateChart('radar', 'radarChart', {
    type: 'radar',
    data: {
      labels: radar.labels,
      datasets: [
        {
          label: 'Mastery %',
          data: radar.values,
          fill: true,
          borderColor: '#0d8b8e',
          backgroundColor: 'rgba(13, 139, 142, 0.22)',
          pointBackgroundColor: '#0d8b8e',
        },
      ],
    },
    options: {
      scales: {
        r: { suggestedMin: 0, suggestedMax: 100 },
      },
    },
  });
}

function renderTelemetry(topic) {
  const history = state.dashboard.telemetry[topic] || [];
  const labels = history.map((row) => new Date(row.timestamp).toLocaleString());

  createOrUpdateChart('accuracy', 'accuracyChart', {
    type: 'bar',
    data: {
      labels,
      datasets: [{ label: 'Correct', data: history.map((row) => row.correct), backgroundColor: '#d9426a' }],
    },
    options: {
      scales: {
        y: { min: 0, max: 1, ticks: { stepSize: 1 } },
      },
    },
  });

  createOrUpdateChart('speed', 'speedChart', {
    type: 'line',
    data: {
      labels,
      datasets: [
        {
          label: 'Time Taken (s)',
          data: history.map((row) => row.time_taken),
          borderColor: '#0d8b8e',
          backgroundColor: 'rgba(13, 139, 142, 0.2)',
          tension: 0.35,
          fill: true,
        },
      ],
    },
  });
}

function populateTopicSelectors(topics) {
  const selectors = [document.getElementById('telemetryTopic'), document.getElementById('selfTopic')];
  selectors.forEach((select) => {
    select.innerHTML = '';
    topics.forEach((topic) => {
      const option = document.createElement('option');
      option.value = topic;
      option.textContent = topic;
      select.appendChild(option);
    });
  });
}

function renderTargetedMeta() {
  const target = state.studentState[0];
  const container = document.getElementById('targetedMeta');

  if (!target) {
    container.innerHTML = '<p>No target topic available.</p>';
    return;
  }

  container.innerHTML = `
    <p><strong>System Target Locked:</strong> ${target.topic}</p>
    <p><strong>Diagnosis:</strong> ${target.diagnosis}</p>
    <p><strong>Urgency:</strong> ${target.urgency}</p>
  `;
}

function renderQuiz(containerId, quizData) {
  const container = document.getElementById(containerId);
  container.innerHTML = '';

  const form = document.createElement('form');
  form.className = 'quiz-form';

  quizData.questions.forEach((question, index) => {
    const questionBlock = document.createElement('section');
    questionBlock.className = 'question';

    const optionsHtml = question.options
      .map(
        (option) =>
          `<label><input type="radio" name="q_${index}" value="${option.replace(/"/g, '&quot;')}" required /> ${option}</label>`
      )
      .join('');

    questionBlock.innerHTML = `
      <h4>Question ${index + 1}</h4>
      <p>${question.question}</p>
      ${optionsHtml}
      <div class="feedback" id="feedback_${containerId}_${index}"></div>
    `;

    form.appendChild(questionBlock);
  });

  const submit = document.createElement('button');
  submit.type = 'submit';
  submit.className = 'primary';
  submit.textContent = 'Submit Answers';
  form.appendChild(submit);

  const scoreEl = document.createElement('div');
  scoreEl.className = 'score';
  scoreEl.style.display = 'none';
  form.appendChild(scoreEl);

  form.addEventListener('submit', (event) => {
    event.preventDefault();
    let score = 0;

    quizData.questions.forEach((question, index) => {
      const selected = form.querySelector(`input[name="q_${index}"]:checked`)?.value;
      const feedback = form.querySelector(`#feedback_${containerId}_${index}`);
      if (!feedback) return;

      if (selected === question.correct_answer) {
        score += 1;
        feedback.innerHTML = `<strong>Correct.</strong> ${question.detailed_explanation}`;
      } else {
        feedback.innerHTML = `<strong>Incorrect.</strong> Correct answer: ${question.correct_answer}. ${question.detailed_explanation}`;
      }
    });

    scoreEl.textContent = `Final score: ${score} / ${quizData.questions.length}`;
    scoreEl.style.display = 'block';
  });

  container.appendChild(form);
}

async function generateQuiz({ topic, diagnosis, containerId }) {
  const data = await postJSON('/api/quiz', {
    topic,
    diagnosis,
    num_questions: 4,
    api_key: apiKey() || null,
  });
  renderQuiz(containerId, data);
}

async function generateMicroTask({ topic, diagnosis, outputId }) {
  const output = document.getElementById(outputId);
  output.textContent = 'Generating...';
  try {
    const data = await postJSON('/api/micro-task', {
      topic,
      diagnosis,
      api_key: apiKey() || null,
    });
    output.textContent = data.task;
  } catch (error) {
    output.textContent = error.message;
  }
}

function wireActions() {
  document.getElementById('telemetryTopic').addEventListener('change', (event) => {
    renderTelemetry(event.target.value);
  });

  document.getElementById('generateTargetedQuiz').addEventListener('click', async () => {
    const target = state.studentState[0];
    if (!target) return;
    try {
      await generateQuiz({
        topic: target.topic,
        diagnosis: target.diagnosis,
        containerId: 'targetedQuizContainer',
      });
    } catch (error) {
      document.getElementById('targetedQuizContainer').textContent = error.message;
    }
  });

  document.getElementById('targetedMicroTask').addEventListener('click', async () => {
    const target = state.studentState[0];
    if (!target) return;
    await generateMicroTask({
      topic: target.topic,
      diagnosis: target.diagnosis,
      outputId: 'targetedMicroTaskOutput',
    });
  });

  document.getElementById('generateSelfQuiz').addEventListener('click', async () => {
    const topic = document.getElementById('selfTopic').value;
    try {
      await generateQuiz({
        topic,
        diagnosis: 'Student-initiated deep dive practice.',
        containerId: 'selfQuizContainer',
      });
    } catch (error) {
      document.getElementById('selfQuizContainer').textContent = error.message;
    }
  });

  document.getElementById('selfMicroTask').addEventListener('click', async () => {
    const topic = document.getElementById('selfTopic').value;
    const selected = state.studentState.find((item) => item.topic === topic);
    await generateMicroTask({
      topic,
      diagnosis: selected ? selected.diagnosis : 'Student-initiated deep dive practice.',
      outputId: 'selfMicroTaskOutput',
    });
  });
}

async function bootstrap() {
  const [topicsData, dashboardData] = await Promise.all([getJSON('/api/topics'), getJSON('/api/dashboard')]);

  state.topics = topicsData.topics;
  state.studentState = topicsData.state;
  state.dashboard = dashboardData;

  populateTopicSelectors(state.topics);
  renderUrgentTopics(dashboardData.urgent);
  renderRadarChart(dashboardData.radar);
  renderTargetedMeta();

  const initialTopic = state.topics[0];
  if (initialTopic) {
    document.getElementById('telemetryTopic').value = initialTopic;
    document.getElementById('selfTopic').value = initialTopic;
    renderTelemetry(initialTopic);
  }

  wireActions();
}

bootstrap().catch((error) => {
  document.body.innerHTML = `<main class="layout"><section class="card"><h2>App failed to load</h2><p>${error.message}</p></section></main>`;
});
