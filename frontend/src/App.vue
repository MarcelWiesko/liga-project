<script setup>
import { ref, computed, onMounted } from 'vue'

const API = 'https://systemliga-gkb2gtc6h7grcng8.polandcentral-01.azurewebsites.net/api'

const username = ref('')
const password = ref('')
const role = ref(localStorage.getItem('role'))
const token = ref(localStorage.getItem('token'))
const isLoggedIn = ref(!!token.value)

const registerUsername = ref('')
const registerPassword = ref('')
const registerRole = ref('user')
const registerMessage = ref(null)
const showRegister = ref(false)

const leagues = ref([])
const selectedLeague = ref('')
const schedulers = ref([])

const teams = ref([])
const players = ref([])
const matches = ref([])
const table = ref([])
const bestTeam = ref(null)
const bestPlayer = ref(null)
const selectedTeam = ref('')
const bestAgainstTeam = ref(null)

const selectedMatch = ref('')
const selectedPlayer = ref('')
const minute = ref('')

const loading = ref(false)
const error = ref(null)
const loginError = ref(null)
const successMessage = ref(null)
const search = ref('')

async function getJson(url, auth = false) {
  const headers = {}

  if (auth && token.value) {
    headers.Authorization = `Token ${token.value}`
  }

  const res = await fetch(url, { headers })

  if (!res.ok) {
    throw new Error('API error')
  }

  return res.json()
}

async function loadData() {
  try {
    loading.value = true
    error.value = null

    leagues.value = await getJson(`${API}/leagues/`)

    if (!selectedLeague.value && leagues.value.length > 0) {
      selectedLeague.value = leagues.value[0].id
    }

    teams.value = await getJson(
    `${API}/teams/?league_id=${selectedLeague.value}`
    )
    players.value = await getJson(
    `${API}/players/?league_id=${selectedLeague.value}`
    )
    matches.value = await getJson(`${API}/matches/?league_id=${selectedLeague.value}`)
    schedulers.value = await getJson(
    `${API}/schedulers/?league=${selectedLeague.value}`
    )

    table.value = await getJson(`${API}/table/?league_id=${selectedLeague.value}`)
    bestTeam.value = await getJson(`${API}/best-team/?league_id=${selectedLeague.value}`)
    bestPlayer.value = await getJson(`${API}/best-player/`)
  } catch (e) {
    error.value = 'Nie udało się pobrać danych z backendu.'
  } finally {
    loading.value = false
  }
}

async function register() {
  registerMessage.value = null
  loginError.value = null

  const response = await fetch(`${API}/register/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      username: registerUsername.value,
      password: registerPassword.value,
      role: registerRole.value
    })
  })

  const data = await response.json()

  if (!response.ok || !data.success) {
    loginError.value = data.message || 'Nie udało się utworzyć konta'
    return
  }

  registerMessage.value = 'Konto utworzone. Możesz się zalogować.'
  registerUsername.value = ''
  registerPassword.value = ''
  registerRole.value = 'user'
  showRegister.value = false
}

async function login() {
  loginError.value = null

  const response = await fetch(`${API}/login/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      username: username.value,
      password: password.value
    })
  })

  const data = await response.json()

  if (!response.ok || !data.success) {
    loginError.value = data.message || 'Nieprawidłowy login lub hasło'
    return
  }

  localStorage.setItem('token', data.token)
  localStorage.setItem('role', data.role)

  token.value = data.token
  role.value = data.role
  isLoggedIn.value = true

  await loadData()
}

function logout() {
  localStorage.removeItem('token')
  localStorage.removeItem('role')

  token.value = null
  role.value = null
  isLoggedIn.value = false
}

async function changeLeague() {
  bestAgainstTeam.value = null
  await loadData()
}

async function addGoal() {
  successMessage.value = null
  error.value = null

  const response = await fetch(`${API}/add-goal/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Token ${token.value}`
    },
    body: JSON.stringify({
      match: selectedMatch.value,
      player: selectedPlayer.value,
      minute: minute.value
    })
  })

  const data = await response.json()

  if (!response.ok) {
    error.value = data.message || 'Nie udało się dodać gola.'
    return
  }

  successMessage.value = 'Gol został dodany.'
  selectedMatch.value = ''
  selectedPlayer.value = ''
  minute.value = ''

  await loadData()
}

async function getBestAgainstTeam() {
  bestAgainstTeam.value = null
  error.value = null

  if (!selectedTeam.value) {
    error.value = 'Wybierz drużynę.'
    return
  }

  const response = await fetch(`${API}/best-player-against-team/${selectedTeam.value}/`, {
    headers: {
      Authorization: `Token ${token.value}`
    }
  })

  const data = await response.json()

  if (!response.ok) {
    error.value = data.message || 'Brak danych.'
    return
  }

  bestAgainstTeam.value = data
}

const filteredPlayers = computed(() =>
  players.value.filter(player =>
    `${player.first_name} ${player.last_name} ${player.team_name}`
      .toLowerCase()
      .includes(search.value.toLowerCase())
  )
)

const filteredSchedulers = computed(() =>
  schedulers.value.filter(item => String(item.league) === String(selectedLeague.value))
)

const finishedMatches = computed(() => matches.value.filter(match => match.finished))

onMounted(() => {
  if (isLoggedIn.value) {
    loadData()
  }
})
</script>

<template>
  <div class="app">
    <aside class="sidebar">
      <div class="brand">
        <div class="brand-icon">⚽</div>
        <div>
          <h1>System Liga</h1>
          <p>Panel użytkownika</p>
        </div>
      </div>

      <nav v-if="isLoggedIn">
        <a href="#dashboard">Dashboard</a>
        <a href="#table">Tabela</a>
        <a href="#scheduler">Terminarz</a>
        <a href="#teams">Drużyny</a>
        <a href="#players">Zawodnicy</a>
        <a href="#matches">Mecze</a>
        <a v-if="role === 'referee'" href="#referee">Dodaj gola</a>
        <a v-if="role === 'manager'" href="#manager">Analiza</a>
      </nav>

      <button v-if="isLoggedIn" class="logout" @click="logout">
        Wyloguj
      </button>
    </aside>

    <main class="main">
      <section v-if="!isLoggedIn" class="login-card">
        <h2>Logowanie</h2>
        <p>Zaloguj się jako user, sędzia albo menadżer.</p>

        <input v-model="username" type="text" placeholder="Login">
        <input v-model="password" type="password" placeholder="Hasło">

        <button @click="login">Zaloguj</button>
        <input v-model="username" type="text" placeholder="Login">
        <input v-model="password" type="password" placeholder="Hasło">

        <button @click="login">Zaloguj</button>

        <button class="secondary" @click="showRegister = !showRegister">
          {{ showRegister ? 'Ukryj rejestrację' : 'Utwórz konto' }}
        </button>

        <div v-if="showRegister" class="register-box">
          <h3>Rejestracja</h3>

          <input v-model="registerUsername" type="text" placeholder="Nowy login">

          <input v-model="registerPassword" type="password" placeholder="Nowe hasło">

          <select v-model="registerRole">
            <option value="user">Użytkownik</option>
            <option value="referee">Sędzia</option>
            <option value="manager">Menadżer</option>
          </select>

          <button @click="register">Zarejestruj</button>
        </div>

        <div v-if="registerMessage" class="success">
          {{ registerMessage }}
        </div>

        <div v-if="loginError" class="alert">
          {{ loginError }}
        </div>
        <div v-if="loginError" class="alert">
          {{ loginError }}
        </div>
      </section>

      <template v-else>
        <section id="dashboard" class="hero">
          <div>
            <span class="badge">Rola: {{ role }}</span>
            <h2>System zarządzania ligą piłkarską</h2>
            <p>
              Wybieraj ligę, sprawdzaj tabelę, terminarz, mecze oraz statystyki zawodników.
            </p>
          </div>

          <button @click="loadData">
            {{ loading ? 'Ładowanie...' : 'Odśwież dane' }}
          </button>
        </section>

        <div v-if="error" class="alert">{{ error }}</div>
        <div v-if="successMessage" class="success">{{ successMessage }}</div>

      <section class="league-select-card">
        <div>
          <span class="section-label">Aktywna liga</span>
          <h2>Wybierz rozgrywki</h2>
          <p>Po zmianie ligi tabela, terminarz i drużyny zostaną automatycznie odświeżone.</p>
        </div>

        <div class="league-control">
          <select v-model="selectedLeague" @change="changeLeague">
            <option value="">Wybierz ligę</option>
            <option v-for="league in leagues" :key="league.id" :value="league.id">
              {{ league.name }} — {{ league.season }}
            </option>
          </select>
        </div>
      </section>

        <section class="stats">
          <div class="stat-card green">
            <span>Najlepsza drużyna</span>
            <h3>{{ bestTeam?.team || 'Brak danych' }}</h3>
            <p>{{ bestTeam?.points ?? 0 }} pkt</p>
          </div>

          <div class="stat-card blue">
            <span>Najlepszy zawodnik</span>
            <h3>{{ bestPlayer?.player || 'Brak danych' }}</h3>
            <p>{{ bestPlayer?.goals ?? 0 }} goli</p>
          </div>

          <div class="stat-card orange">
            <span>Drużyny</span>
            <h3>{{ teams.length }}</h3>
            <p>w systemie</p>
          </div>

          <div class="stat-card purple">
            <span>Mecze zakończone</span>
            <h3>{{ finishedMatches.length }}</h3>
            <p>rozegranych</p>
          </div>
        </section>

        <section id="table" class="card">
          <h2>Tabela ligowa</h2>

          <div class="table-wrapper">
            <table>
              <thead>
                <tr>
                  <th>#</th>
                  <th>Drużyna</th>
                  <th>PKT</th>
                  <th>W</th>
                  <th>R</th>
                  <th>P</th>
                  <th>Bramki</th>
                  <th>Bilans</th>
                </tr>
              </thead>

              <tbody>
                <tr v-for="(row, index) in table" :key="row.team_id">
                  <td>{{ index + 1 }}</td>
                  <td><strong>{{ row.team }}</strong></td>
                  <td>{{ row.points }}</td>
                  <td>{{ row.wins }}</td>
                  <td>{{ row.draws }}</td>
                  <td>{{ row.losses }}</td>
                  <td>{{ row.goals_for }} : {{ row.goals_against }}</td>
                  <td>{{ row.goal_difference }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>

        <section id="scheduler" class="card">
          <h2>Terminarz ligi</h2>

          <div v-if="filteredSchedulers.length === 0" class="empty">
            Brak terminarza dla wybranej ligi.
          </div>

          <div v-for="item in filteredSchedulers" :key="item.id" class="schedule-item">
            <div>
              <strong>Kolejka {{ item.round_number }}</strong>
              <p>{{ new Date(item.planned_date).toLocaleString() }}</p>
            </div>

            <div class="schedule-match">
              {{ item.home_team_name }}
              <span>{{ item.home_score }} : {{ item.away_score }}</span>
              {{ item.away_team_name }}
            </div>
          </div>
        </section>

        <section class="grid">
          <div id="teams" class="card">
            <h2>Drużyny</h2>

            <div v-for="team in teams" :key="team.id" class="item">
              <strong>{{ team.name }}</strong>
              <span>{{ team.city || 'Brak miasta' }}</span>
            </div>
          </div>

          <div id="players" class="card">
            <h2>Zawodnicy</h2>

            <input v-model="search" class="search" type="text" placeholder="Szukaj zawodnika...">

            <div v-for="player in filteredPlayers" :key="player.id" class="item">
              <strong>{{ player.first_name }} {{ player.last_name }}</strong>
              <span>{{ player.team_name }}</span>
            </div>
          </div>
        </section>

        <section id="matches" class="card">
          <h2>Mecze</h2>

          <div v-for="match in matches" :key="match.id" class="match-card">
            <strong>{{ match.home_team_name }}</strong>
            <span>{{ match.home_score }} : {{ match.away_score }}</span>
            <strong>{{ match.away_team_name }}</strong>
          </div>
        </section>

        <section v-if="role === 'referee'" id="referee" class="card">
          <h2>Panel sędziego — dodaj gola</h2>

          <select v-model="selectedMatch">
            <option value="">Wybierz mecz</option>
            <option v-for="match in matches" :key="match.id" :value="match.id">
              {{ match.home_team_name }} - {{ match.away_team_name }}
            </option>
          </select>

          <select v-model="selectedPlayer">
            <option value="">Wybierz zawodnika</option>
            <option v-for="player in players" :key="player.id" :value="player.id">
              {{ player.first_name }} {{ player.last_name }} — {{ player.team_name }}
            </option>
          </select>

          <input v-model="minute" type="number" placeholder="Minuta gola">

          <button @click="addGoal">Dodaj gola</button>
        </section>

        <section v-if="role === 'manager'" id="manager" class="card">
          <h2>Panel menadżera</h2>
          <p>Sprawdź najlepszego zawodnika przeciw wybranej drużynie.</p>

          <select v-model="selectedTeam">
            <option value="">Wybierz drużynę</option>
            <option v-for="team in teams" :key="team.id" :value="team.id">
              {{ team.name }}
            </option>
          </select>

          <button @click="getBestAgainstTeam">Sprawdź</button>

          <div v-if="bestAgainstTeam" class="result">
            <h3>{{ bestAgainstTeam.player }}</h3>
            <p>Drużyna: {{ bestAgainstTeam.team }}</p>
            <p>Przeciwko: {{ bestAgainstTeam.against_team }}</p>
            <p>Gole: {{ bestAgainstTeam.goals_against_team }}</p>
          </div>
        </section>
      </template>
    </main>
  </div>
</template>

<style scoped>
.app {
  min-height: 100vh;
  background: #eef2f7;
  color: #0f172a;
  font-family: Arial, sans-serif;
  display: flex;
}

.sidebar {
  width: 280px;
  background: #020617;
  color: white;
  padding: 28px;
  position: sticky;
  top: 0;
  height: 100vh;
  overflow-y: auto;
}
.brand {
  display: flex;
  gap: 14px;
  align-items: center;
  margin-bottom: 30px;
}

.brand-icon {
  width: 48px;
  height: 48px;
  background: linear-gradient(135deg, #22c55e, #14b8a6);
  display: grid;
  place-items: center;
  border-radius: 16px;
  font-size: 24px;
}

.brand h1 {
  margin: 0;
  font-size: 22px;
}

.brand p {
  margin: 4px 0 0;
  color: #94a3b8;
}

nav {
  display: grid;
  gap: 10px;
}

nav a {
  color: #cbd5e1;
  text-decoration: none;
  padding: 13px;
  border-radius: 12px;
  font-weight: 700;
}

nav a:hover {
  background: #1e293b;
  color: white;
}

.logout {
  margin-top: 30px;
  width: 100%;
  background: #ef4444;
}

.main {
  flex: 1;
  padding: 34px;
}
.secondary {
  background: #0f172a;
  margin-top: 10px;
}

.register-box {
  margin-top: 20px;
  padding: 18px;
  background: #f8fafc;
  border-radius: 16px;
}

.login-card,
.card,
.stat-card {
  background: white;
  border-radius: 22px;
  padding: 24px;
  box-shadow: 0 18px 45px rgba(15, 23, 42, 0.08);
}

.login-card {
  max-width: 420px;
  margin: 100px auto;
}

.login-card input,
select,
.search,
input {
  width: 100%;
  padding: 14px;
  margin: 10px 0;
  border: 1px solid #cbd5e1;
  border-radius: 12px;
}

.hero {
  background: linear-gradient(135deg, #0f172a, #14532d);
  color: white;
  padding: 38px;
  border-radius: 26px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 26px;
}

.badge {
  background: rgba(255, 255, 255, 0.15);
  padding: 8px 14px;
  border-radius: 999px;
}

.hero h2 {
  font-size: 36px;
}

button {
  background: #16a34a;
  color: white;
  border: none;
  padding: 13px 20px;
  border-radius: 14px;
  font-weight: 800;
  cursor: pointer;
}

.alert {
  background: #fee2e2;
  color: #991b1b;
  padding: 14px;
  border-radius: 14px;
  margin: 15px 0;
}

.success {
  background: #dcfce7;
  color: #166534;
  padding: 14px;
  border-radius: 14px;
  margin: 15px 0;
}

.stats {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 18px;
  margin-bottom: 26px;
}

.stat-card span {
  color: #64748b;
  font-size: 13px;
  font-weight: 900;
  text-transform: uppercase;
}

.stat-card h3 {
  font-size: 26px;
}

.card {
  margin-bottom: 26px;
}

.table-wrapper {
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
}

th,
td {
  padding: 15px;
  border-bottom: 1px solid #e5e7eb;
  text-align: left;
}

th {
  background: #f8fafc;
}

.grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 26px;
}

.item {
  background: #f8fafc;
  padding: 15px;
  border-radius: 14px;
  margin-bottom: 10px;
  display: flex;
  justify-content: space-between;
}

.match-card,
.schedule-item {
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 20px;
  background: #f8fafc;
  padding: 16px;
  border-radius: 14px;
  margin-bottom: 12px;
  align-items: center;
}

.match-card {
  grid-template-columns: 1fr auto 1fr;
}

.match-card span,
.schedule-match span {
  background: #020617;
  color: white;
  padding: 10px 18px;
  border-radius: 12px;
  font-weight: 900;
}

.schedule-match {
  font-weight: 700;
}

.empty {
  background: #f8fafc;
  padding: 16px;
  border-radius: 14px;
  color: #64748b;
}

.result {
  background: #f8fafc;
  margin-top: 16px;
  padding: 16px;
  border-radius: 14px;
}

.league-select-card {
  background: linear-gradient(135deg, #ffffff, #ecfdf5);
  border: 1px solid #bbf7d0;
  border-radius: 24px;
  padding: 26px;
  margin-bottom: 26px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 24px;
  box-shadow: 0 18px 45px rgba(15, 23, 42, 0.08);
}

.section-label {
  display: inline-block;
  background: #dcfce7;
  color: #166534;
  padding: 7px 12px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 900;
  text-transform: uppercase;
  margin-bottom: 10px;
}

.league-select-card h2 {
  margin: 0;
  font-size: 26px;
}

.league-select-card p {
  margin: 8px 0 0;
  color: #64748b;
}

.league-control {
  min-width: 320px;
}

.league-control select {
  width: 100%;
  padding: 15px 18px;
  border: 2px solid #22c55e;
  border-radius: 16px;
  background: white;
  color: #0f172a;
  font-weight: 800;
  font-size: 15px;
  cursor: pointer;
}

.league-control select:focus {
  outline: none;
  box-shadow: 0 0 0 4px rgba(34, 197, 94, 0.18);
}

@media (max-width: 900px) {
  .league-select-card {
    flex-direction: column;
    align-items: stretch;
  }

  .league-control {
    min-width: 100%;
  }
}

@media (max-width: 900px) {
  .app {
    flex-direction: column;
  }

.sidebar {
  width: 100%;
  height: auto;
  position: static;
}

  .stats,
  .grid {
    grid-template-columns: 1fr;
  }

  .hero {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
