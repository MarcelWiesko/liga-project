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

const playersLimit = ref(5)

async function getJson(url, auth = false) {
  const headers = {}

  if (auth && token.value) {
    headers.Authorization = `Token ${token.value}`
  }

  const res = await fetch(url, { headers })

  if (!res.ok) {
    const text = await res.text()
    console.error('Błąd API:', url, res.status, text)
    throw new Error(`Błąd API ${res.status}: ${url}`)
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

    const leagueParam = selectedLeague.value ? `?league_id=${selectedLeague.value}` : ''

    teams.value = await getJson(`${API}/teams/${leagueParam}`)
    players.value = await getJson(`${API}/players/${leagueParam}`)
    matches.value = await getJson(`${API}/matches/${leagueParam}`)
    schedulers.value = await getJson(`${API}/schedulers/`)

    table.value = await getJson(`${API}/table/?league_id=${selectedLeague.value}`)
    bestTeam.value = await getJson(`${API}/best-team/?league_id=${selectedLeague.value}`)
    bestPlayer.value = await getJson(`${API}/best-player/?league_id=${selectedLeague.value}`)
  } catch (e) {
    console.error(e)
    error.value = e.message || 'Nie udało się pobrać danych z backendu.'
  } finally {
    loading.value = false
  }
}

async function login() {
  loginError.value = null
  registerMessage.value = null

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
      password: registerPassword.value
    })
  })

  const data = await response.json()

  if (!response.ok || !data.success) {
    loginError.value = data.message || 'Nie udało się utworzyć konta'
    return
  }

  registerMessage.value = 'Konto zostało utworzone. Możesz się zalogować.'
  registerUsername.value = ''
  registerPassword.value = ''
  showRegister.value = false
}

function logout() {
  localStorage.removeItem('token')
  localStorage.removeItem('role')

  token.value = null
  role.value = null
  isLoggedIn.value = false
  username.value = ''
  password.value = ''
}

async function changeLeague() {
  bestAgainstTeam.value = null
  successMessage.value = null
  search.value = ''
  playersLimit.value = 5
  await loadData()
}

async function addGoal() {
  successMessage.value = null
  error.value = null

  if (!selectedMatch.value || !selectedPlayer.value || !minute.value) {
    error.value = 'Uzupełnij mecz, zawodnika i minutę gola.'
    return
  }

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

const activeLeague = computed(() =>
  leagues.value.find(league => String(league.id) === String(selectedLeague.value))
)

const filteredPlayers = computed(() =>
  players.value.filter(player =>
    `${player.first_name} ${player.last_name} ${player.team_name}`
      .toLowerCase()
      .includes(search.value.toLowerCase())
  )
)

const visiblePlayers = computed(() =>
  filteredPlayers.value.slice(0, playersLimit.value)
)

const filteredSchedulers = computed(() =>
  schedulers.value.filter(item => String(item.league) === String(selectedLeague.value))
)

const finishedMatches = computed(() =>
  matches.value.filter(match => match.finished)
)

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
          <p>SaaS Azure</p>
        </div>
      </div>

      <nav v-if="isLoggedIn">
        <a href="#dashboard">Dashboard</a>
        <a href="#league">Liga</a>
        <a href="#table">Tabela</a>
        <a href="#scheduler">Terminarz</a>
        <a href="#teams">Drużyny</a>
        <a href="#players">Zawodnicy</a>
        <a href="#matches">Mecze</a>
        <a v-if="role === 'referee'" href="#referee">Panel sędziego</a>
        <a v-if="role === 'manager'" href="#manager">Panel menadżera</a>
      </nav>

      <div v-if="isLoggedIn" class="user-box">
        <span>Zalogowano jako</span>
        <strong>{{ role }}</strong>

        <button class="logout" @click="logout">
          Wyloguj
        </button>
      </div>
    </aside>

    <main class="main">
      <section v-if="!isLoggedIn" class="auth-wrapper">
        <div class="login-card">
          <div class="login-header">
            <div class="login-logo">⚽</div>
            <h2>Logowanie</h2>
            <p>Zaloguj się lub utwórz nowe konto.</p>
          </div>

          <input v-model="username" type="text" placeholder="Login">
          <input v-model="password" type="password" placeholder="Hasło">

          <div class="button-row">
            <button @click="login">Zaloguj</button>

            <button class="secondary" @click="showRegister = !showRegister">
              {{ showRegister ? 'Ukryj' : 'Utwórz konto' }}
            </button>
          </div>

          <div v-if="showRegister" class="register-box">
            <h3>Rejestracja</h3>

            <input v-model="registerUsername" type="text" placeholder="Nowy login">
            <input v-model="registerPassword" type="password" placeholder="Nowe hasło">

            <button @click="register">Zarejestruj</button>
          </div>

          <div v-if="registerMessage" class="success">
            {{ registerMessage }}
          </div>

          <div v-if="loginError" class="alert">
            {{ loginError }}
          </div>
        </div>
      </section>

      <template v-else>
        <section id="dashboard" class="hero">
          <div>
            <span class="badge">Rola: {{ role }}</span>
            <h2>System zarządzania ligą piłkarską</h2>
            <p>
              Wybieraj ligę, sprawdzaj tabelę, terminarz, wyniki oraz statystyki zawodników.
            </p>
          </div>

          <button @click="loadData">
            {{ loading ? 'Ładowanie...' : 'Odśwież dane' }}
          </button>
        </section>

        <div v-if="error" class="alert">{{ error }}</div>
        <div v-if="successMessage" class="success">{{ successMessage }}</div>

        <section id="league" class="league-select-card">
          <div class="league-info">
            <div class="league-logo">
              <img
                v-if="activeLeague?.logo_url"
                :src="activeLeague.logo_url"
                :alt="activeLeague.name"
              >
              <span v-else>🏆</span>
            </div>

            <div>
              <span class="section-label">Aktywna liga</span>
              <h2>
                {{ activeLeague ? `${activeLeague.name} — ${activeLeague.season}` : 'Wybierz ligę' }}
              </h2>
              <p>
                Po zmianie ligi tabela, drużyny, zawodnicy, mecze i terminarz zostaną odświeżone.
              </p>
            </div>
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
            <span>Drużyny w lidze</span>
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
          <div class="card-header">
            <div>
              <h2>Tabela ligowa</h2>
              <p>Ranking drużyn w aktualnie wybranej lidze.</p>
            </div>
          </div>

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
                  <td><span class="place">{{ index + 1 }}</span></td>
                  <td><strong>{{ row.team }}</strong></td>
                  <td class="points">{{ row.points }}</td>
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
          <div class="card-header">
            <div>
              <h2>Terminarz ligi</h2>
              <p>Mecze przypisane do wybranej ligi.</p>
            </div>
          </div>

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
            <div class="card-header">
              <div>
                <h2>Drużyny</h2>
                <p>Drużyny z aktualnej ligi.</p>
              </div>
            </div>

            <div v-if="teams.length === 0" class="empty">
              Brak drużyn w tej lidze.
            </div>

            <div v-for="team in teams" :key="team.id" class="item team-item">
              <div class="team-avatar">
                <img
                  v-if="team.logo_url"
                  :src="team.logo_url"
                  :alt="team.name"
                >
                <span v-else>{{ team.name?.charAt(0) }}</span>
              </div>

              <div>
                <strong>{{ team.name }}</strong>
                <span>{{ team.city || 'Brak miasta' }}</span>
              </div>
            </div>
          </div>

          <div id="players" class="card">
            <div class="card-header">
              <div>
                <h2>Zawodnicy</h2>
                <p>Zawodnicy przypisani do drużyn z wybranej ligi.</p>
              </div>
            </div>

            <input v-model="search" class="search" type="text" placeholder="Szukaj zawodnika...">

            <div v-if="filteredPlayers.length === 0" class="empty">
              Brak zawodników do wyświetlenia.
            </div>

            <div v-for="player in visiblePlayers" :key="player.id" class="item">
              <strong>{{ player.first_name }} {{ player.last_name }}</strong>
              <span>{{ player.team_name }}</span>
            </div>

            <div v-if="filteredPlayers.length > playersLimit" class="list-info">
              Wyświetlono {{ visiblePlayers.length }} z {{ filteredPlayers.length }} zawodników.
            </div>

            <div class="players-buttons">
            <button
              v-if="filteredPlayers.length > playersLimit"
              class="secondary show-more"
              @click="playersLimit += 5"
            >
              Pokaż więcej
            </button>

            <button
              v-if="playersLimit > 5"
              class="show-less"
              @click="playersLimit = 5"
            >
              Pokaż mniej
            </button>
          </div>
         </div>
        </section>

        <section id="matches" class="card">
          <div class="card-header">
            <div>
              <h2>Mecze</h2>
              <p>Mecze tylko z wybranej ligi.</p>
            </div>
          </div>

          <div v-if="matches.length === 0" class="empty">
            Brak meczów w tej lidze.
          </div>

          <div v-for="match in matches" :key="match.id" class="match-card">
            <strong>{{ match.home_team_name }}</strong>
            <span>{{ match.home_score }} : {{ match.away_score }}</span>
            <strong>{{ match.away_team_name }}</strong>
          </div>
        </section>

        <section v-if="role === 'referee'" id="referee" class="card role-card">
          <div class="card-header">
            <div>
              <h2>Panel sędziego</h2>
              <p>Dodaj gola do wybranego meczu.</p>
            </div>
          </div>

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

        <section v-if="role === 'manager'" id="manager" class="card role-card">
          <div class="card-header">
            <div>
              <h2>Panel menadżera</h2>
              <p>Sprawdź najlepszego zawodnika przeciwko wybranej drużynie.</p>
            </div>
          </div>

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
* {
  box-sizing: border-box;
}

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

.brand-icon,
.login-logo {
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

.user-box {
  margin-top: 28px;
  padding: 16px;
  border-radius: 16px;
  background: #0f172a;
}

.user-box span {
  color: #94a3b8;
  display: block;
  font-size: 13px;
}

.user-box strong {
  display: block;
  margin-top: 5px;
  font-size: 18px;
}

.logout {
  margin-top: 16px;
  width: 100%;
  background: #ef4444;
}

.main {
  flex: 1;
  padding: 34px;
}

.auth-wrapper {
  min-height: 100vh;
  display: grid;
  place-items: center;
}

.login-card,
.card,
.stat-card,
.league-select-card {
  background: white;
  border-radius: 24px;
  padding: 26px;
  box-shadow: 0 18px 45px rgba(15, 23, 42, 0.08);
}

.login-card {
  width: 100%;
  max-width: 460px;
}

.login-header {
  margin-bottom: 24px;
}

.login-header h2 {
  margin-bottom: 8px;
}

.login-card input,
select,
.search,
input {
  width: 100%;
  padding: 14px;
  margin: 10px 0;
  border: 1px solid #cbd5e1;
  border-radius: 14px;
  font-size: 15px;
}

.button-row {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
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

.players-buttons {
  display: flex;
  gap: 10px;
  margin-top: 12px;
}

.players-buttons button {
  flex: 1;
}

.show-less {
  background: #64748b;
  margin-top: 12px;
  width: 100%;
}

.secondary {
  background: #0f172a;
}

.register-box {
  margin-top: 20px;
  padding: 18px;
  background: #f8fafc;
  border-radius: 18px;
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
  gap: 24px;
}

.badge {
  background: rgba(255, 255, 255, 0.15);
  padding: 8px 14px;
  border-radius: 999px;
}

.hero h2 {
  font-size: 36px;
  margin: 16px 0 10px;
}

.hero p {
  color: #d1fae5;
  margin: 0;
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

.league-select-card {
  background: linear-gradient(135deg, #ffffff, #ecfdf5);
  border: 1px solid #bbf7d0;
  margin-bottom: 26px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 24px;
}

.league-info {
  display: flex;
  align-items: center;
  gap: 18px;
}

.league-logo {
  width: 76px;
  height: 76px;
  background: white;
  border: 1px solid #bbf7d0;
  border-radius: 22px;
  display: grid;
  place-items: center;
  padding: 10px;
  box-shadow: 0 10px 25px rgba(15, 23, 42, 0.08);
}

.league-logo img {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
}

.league-logo span {
  font-size: 32px;
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
  border: 2px solid #22c55e;
  font-weight: 800;
  cursor: pointer;
}

.stats {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 18px;
  margin-bottom: 26px;
}

.stat-card {
  border-left: 6px solid #22c55e;
}

.stat-card.blue {
  border-left-color: #3b82f6;
}

.stat-card.orange {
  border-left-color: #f97316;
}

.stat-card.purple {
  border-left-color: #8b5cf6;
}

.stat-card span {
  color: #64748b;
  font-size: 13px;
  font-weight: 900;
  text-transform: uppercase;
}

.stat-card h3 {
  font-size: 26px;
  margin: 12px 0 6px;
}

.stat-card p {
  margin: 0;
  color: #16a34a;
  font-weight: 900;
}

.card {
  margin-bottom: 26px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 18px;
}

.card-header h2 {
  margin: 0;
}

.card-header p {
  margin: 6px 0 0;
  color: #64748b;
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
  color: #475569;
}

.place {
  width: 32px;
  height: 32px;
  display: grid;
  place-items: center;
  background: #dcfce7;
  color: #166534;
  border-radius: 10px;
  font-weight: 900;
}

.points {
  font-weight: 900;
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
  gap: 14px;
}

.team-item {
  justify-content: flex-start;
  align-items: center;
}

.team-avatar {
  width: 42px;
  height: 42px;
  background: #dcfce7;
  color: #166534;
  border-radius: 14px;
  display: grid;
  place-items: center;
  font-weight: 900;
  flex-shrink: 0;
  overflow: hidden;
}

.team-avatar img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.item span {
  color: #64748b;
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

.role-card {
  border: 2px solid #dcfce7;
}

.list-info {
  margin-top: 12px;
  padding: 12px;
  background: #f1f5f9;
  color: #475569;
  border-radius: 12px;
  font-weight: 700;
  text-align: center;
}

.show-more {
  margin-top: 12px;
  width: 100%;
}

@media (max-width: 1000px) {
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

  .hero,
  .league-select-card {
    flex-direction: column;
    align-items: flex-start;
  }

  .league-info {
    flex-direction: column;
    align-items: flex-start;
  }

  .league-control {
    min-width: 100%;
  }
}

@media (max-width: 600px) {
  .main {
    padding: 18px;
  }

  .hero h2 {
    font-size: 28px;
  }

  .match-card,
  .schedule-item {
    grid-template-columns: 1fr;
    text-align: center;
  }
}
</style>
