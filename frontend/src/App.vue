<script setup>
import { ref, computed, onMounted } from 'vue'

const API = 'https://systemliga-gkb2gtc6h7grcng8.polandcentral-01.azurewebsites.net/api'

const teams = ref([])
const players = ref([])
const matches = ref([])
const table = ref([])
const bestTeam = ref(null)
const bestPlayer = ref(null)
const loading = ref(true)
const error = ref(null)
const search = ref('')

async function getJson(url) {
  const res = await fetch(url)
  if (!res.ok) throw new Error('API error')
  return res.json()
}

async function loadData() {
  try {
    loading.value = true
    error.value = null

    const [
      teamsData,
      playersData,
      matchesData,
      tableData,
      bestTeamData,
      bestPlayerData
    ] = await Promise.all([
      getJson(`${API}/teams/`),
      getJson(`${API}/players/`),
      getJson(`${API}/matches/`),
      getJson(`${API}/table/`),
      getJson(`${API}/best-team/`),
      getJson(`${API}/best-player/`)
    ])

    teams.value = teamsData
    players.value = playersData
    matches.value = matchesData
    table.value = tableData
    bestTeam.value = bestTeamData
    bestPlayer.value = bestPlayerData
  } catch (e) {
    error.value = 'Nie udało się pobrać danych z backendu.'
  } finally {
    loading.value = false
  }
}

const filteredPlayers = computed(() => {
  return players.value.filter(player =>
    `${player.first_name} ${player.last_name} ${player.team_name}`
      .toLowerCase()
      .includes(search.value.toLowerCase())
  )
})

const finishedMatches = computed(() => matches.value.filter(match => match.finished))

onMounted(loadData)
</script>

<template>
  <div class="app">
    <aside class="sidebar">
      <div class="brand">
        <div class="brand-icon">⚽</div>
        <div>
          <h1>System Liga</h1>
          <p>Panel statystyk</p>
        </div>
      </div>

      <nav>
        <a href="#dashboard">Dashboard</a>
        <a href="#table">Tabela</a>
        <a href="#teams">Drużyny</a>
        <a href="#players">Zawodnicy</a>
        <a href="#matches">Mecze</a>
      </nav>

      <a
        class="admin-link"
        href="https://systemliga-gkb2gtc6h7grcng8.polandcentral-01.azurewebsites.net/admin"
        target="_blank"
      >
        Panel admina
      </a>
    </aside>

    <main class="main">
      <section id="dashboard" class="hero">
        <div>
          <span class="badge">Aplikacja SaaS — Azure + Django + Vue</span>
          <h2>System zarządzania ligą piłkarską</h2>
          <p>
            Przeglądaj tabelę ligową, najlepszych zawodników, wyniki meczów
            i statystyki drużyn w jednym miejscu.
          </p>
        </div>

        <button @click="loadData">
          {{ loading ? 'Ładowanie...' : 'Odśwież dane' }}
        </button>
      </section>

      <div v-if="error" class="alert">
        {{ error }}
      </div>

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
        <div class="card-header">
          <div>
            <h2>Tabela ligowa</h2>
            <p>Ranking drużyn według punktów, bilansu bramek i zdobytych goli.</p>
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
                <td>
                  <span class="place">{{ index + 1 }}</span>
                </td>
                <td class="strong">{{ row.team }}</td>
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

      <section class="grid">
        <div id="teams" class="card">
          <div class="card-header">
            <div>
              <h2>Drużyny</h2>
              <p>Lista zespołów dodanych w panelu administratora.</p>
            </div>
          </div>

          <div class="team-list">
            <div v-for="team in teams" :key="team.id" class="team-item">
              <div class="team-avatar">
                {{ team.name?.charAt(0) }}
              </div>
              <div>
                <strong>{{ team.name }}</strong>
                <p>{{ team.city || 'Brak miasta' }}</p>
              </div>
            </div>
          </div>
        </div>

        <div id="players" class="card">
          <div class="card-header">
            <div>
              <h2>Zawodnicy</h2>
              <p>Wyszukaj zawodnika po nazwisku lub drużynie.</p>
            </div>
          </div>

          <input
            v-model="search"
            class="search"
            type="text"
            placeholder="Szukaj zawodnika..."
          >

          <div class="player-list">
            <div v-for="player in filteredPlayers" :key="player.id" class="player-item">
              <div>
                <strong>{{ player.first_name }} {{ player.last_name }}</strong>
                <p>{{ player.team_name }}</p>
              </div>
              <span>#{{ player.shirt_number || '-' }}</span>
            </div>
          </div>
        </div>
      </section>

      <section id="matches" class="card">
        <div class="card-header">
          <div>
            <h2>Mecze</h2>
            <p>Wyniki spotkań pobierane z backendu Django API.</p>
          </div>
        </div>

        <div class="matches">
          <div v-for="match in matches" :key="match.id" class="match-card">
            <div class="club left">
              {{ match.home_team_name }}
            </div>

            <div class="score">
              {{ match.home_score }} : {{ match.away_score }}
            </div>

            <div class="club right">
              {{ match.away_team_name }}
            </div>
          </div>
        </div>
      </section>
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
  font-family: Inter, Arial, sans-serif;
  display: flex;
}

.sidebar {
  width: 280px;
  min-height: 100vh;
  background: #020617;
  color: white;
  padding: 28px;
  position: sticky;
  top: 0;
}

.brand {
  display: flex;
  gap: 14px;
  align-items: center;
  margin-bottom: 34px;
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
  font-size: 22px;
  margin: 0;
}

.brand p {
  margin: 4px 0 0;
  color: #94a3b8;
}

nav {
  display: grid;
  gap: 10px;
}

nav a,
.admin-link {
  color: #cbd5e1;
  text-decoration: none;
  padding: 13px 14px;
  border-radius: 12px;
  font-weight: 700;
  transition: 0.2s;
}

nav a:hover,
.admin-link:hover {
  background: #1e293b;
  color: white;
}

.admin-link {
  display: block;
  margin-top: 30px;
  background: #16a34a;
  color: white;
  text-align: center;
}

.main {
  flex: 1;
  padding: 34px;
  max-width: 1400px;
}

.hero {
  background: linear-gradient(135deg, #0f172a, #14532d);
  color: white;
  padding: 38px;
  border-radius: 26px;
  display: flex;
  justify-content: space-between;
  gap: 30px;
  align-items: center;
  margin-bottom: 26px;
}

.badge {
  display: inline-block;
  background: rgba(255, 255, 255, 0.12);
  padding: 8px 14px;
  border-radius: 999px;
  font-size: 13px;
  font-weight: 800;
  margin-bottom: 16px;
}

.hero h2 {
  font-size: 38px;
  margin: 0 0 12px;
}

.hero p {
  color: #d1fae5;
  max-width: 720px;
  margin: 0;
  line-height: 1.6;
}

button {
  background: white;
  color: #14532d;
  border: none;
  padding: 13px 20px;
  border-radius: 14px;
  font-weight: 900;
  cursor: pointer;
  white-space: nowrap;
}

.alert {
  background: #fee2e2;
  color: #991b1b;
  padding: 16px;
  border-radius: 16px;
  margin-bottom: 24px;
  font-weight: 700;
}

.stats {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 18px;
  margin-bottom: 26px;
}

.stat-card,
.card {
  background: white;
  border-radius: 24px;
  padding: 24px;
  box-shadow: 0 18px 45px rgba(15, 23, 42, 0.08);
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
  font-size: 28px;
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
  font-size: 24px;
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

th {
  background: #f8fafc;
  color: #475569;
  font-size: 13px;
  text-transform: uppercase;
}

th,
td {
  padding: 16px;
  border-bottom: 1px solid #e5e7eb;
  text-align: left;
}

.place {
  width: 34px;
  height: 34px;
  background: #dcfce7;
  color: #166534;
  display: grid;
  place-items: center;
  border-radius: 10px;
  font-weight: 900;
}

.strong,
.points {
  font-weight: 900;
}

.grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 26px;
}

.team-list,
.player-list {
  display: grid;
  gap: 12px;
}

.team-item,
.player-item {
  background: #f8fafc;
  border: 1px solid #e5e7eb;
  padding: 16px;
  border-radius: 18px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.team-item {
  justify-content: flex-start;
  gap: 14px;
}

.team-avatar {
  width: 44px;
  height: 44px;
  background: #dcfce7;
  color: #166534;
  display: grid;
  place-items: center;
  border-radius: 14px;
  font-weight: 900;
}

.team-item p,
.player-item p {
  margin: 4px 0 0;
  color: #64748b;
}

.player-item span {
  background: #e0f2fe;
  color: #075985;
  padding: 8px 11px;
  border-radius: 999px;
  font-weight: 900;
}

.search {
  width: 100%;
  padding: 14px 16px;
  border-radius: 14px;
  border: 1px solid #cbd5e1;
  margin-bottom: 16px;
  font-size: 15px;
}

.matches {
  display: grid;
  gap: 14px;
}

.match-card {
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  align-items: center;
  background: #f8fafc;
  border-radius: 18px;
  padding: 18px;
  border: 1px solid #e5e7eb;
}

.club {
  font-weight: 900;
}

.club.right {
  text-align: right;
}

.score {
  background: #020617;
  color: white;
  padding: 12px 22px;
  border-radius: 14px;
  font-weight: 900;
  font-size: 18px;
}

@media (max-width: 1000px) {
  .app {
    flex-direction: column;
  }

  .sidebar {
    width: 100%;
    min-height: auto;
    position: static;
  }

  nav {
    grid-template-columns: repeat(2, 1fr);
  }

  .hero,
  .grid,
  .stats {
    grid-template-columns: 1fr;
  }

  .hero {
    flex-direction: column;
    align-items: flex-start;
  }
}

@media (max-width: 700px) {
  .main {
    padding: 18px;
  }

  .hero h2 {
    font-size: 28px;
  }

  .stats {
    grid-template-columns: 1fr;
  }

  .match-card {
    grid-template-columns: 1fr;
    gap: 12px;
    text-align: center;
  }

  .club.right {
    text-align: center;
  }
}
</style>
