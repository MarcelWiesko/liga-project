<script setup>
import { ref, onMounted } from 'vue'

const API = 'https://systemliga-gkb2gtc6h7grcng8.polandcentral-01.azurewebsites.net/api'

const teams = ref([])
const players = ref([])
const matches = ref([])
const table = ref([])
const bestTeam = ref(null)
const bestPlayer = ref(null)
const loading = ref(true)
const error = ref(null)

async function loadData() {
  try {
    loading.value = true

    teams.value = await fetch(`${API}/teams/`).then(res => res.json())
    players.value = await fetch(`${API}/players/`).then(res => res.json())
    matches.value = await fetch(`${API}/matches/`).then(res => res.json())
    table.value = await fetch(`${API}/table/`).then(res => res.json())
    bestTeam.value = await fetch(`${API}/best-team/`).then(res => res.json())
    bestPlayer.value = await fetch(`${API}/best-player/`).then(res => res.json())
  } catch (e) {
    error.value = 'Nie udało się pobrać danych z backendu.'
  } finally {
    loading.value = false
  }
}

onMounted(loadData)
</script>

<template>
  <div class="app">
    <nav class="navbar">
      <div class="logo">⚽ System Liga</div>

      <div class="nav-links">
        <a href="#table">Tabela</a>
        <a href="#teams">Drużyny</a>
        <a href="#players">Zawodnicy</a>
        <a href="#matches">Mecze</a>
      </div>
    </nav>

    <header class="hero">
      <h1>System zarządzania ligą piłkarską</h1>
      <p>
        Aplikacja prezentuje tabelę ligową, najlepszą drużynę,
        najlepszego zawodnika oraz wyniki meczów.
      </p>
    </header>

    <main class="container">
      <div v-if="loading" class="info">Ładowanie danych...</div>
      <div v-if="error" class="error">{{ error }}</div>

      <section class="stats">
        <div class="stat-card">
          <span>Najlepsza drużyna</span>
          <h2>{{ bestTeam?.team || 'Brak danych' }}</h2>
          <p>{{ bestTeam?.points ?? 0 }} pkt</p>
        </div>

        <div class="stat-card">
          <span>Najlepszy zawodnik</span>
          <h2>{{ bestPlayer?.player || 'Brak danych' }}</h2>
          <p>{{ bestPlayer?.goals ?? 0 }} goli</p>
        </div>

        <div class="stat-card">
          <span>Liczba drużyn</span>
          <h2>{{ teams.length }}</h2>
          <p>w systemie</p>
        </div>
      </section>

      <section id="table" class="card">
        <div class="section-header">
          <h2>Tabela ligowa</h2>
          <button @click="loadData">Odśwież</button>
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
                <td>{{ index + 1 }}</td>
                <td class="team-name">{{ row.team }}</td>
                <td><strong>{{ row.points }}</strong></td>
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
          <h2>Drużyny</h2>

          <ul class="list">
            <li v-for="team in teams" :key="team.id">
              <strong>{{ team.name }}</strong>
              <span>{{ team.city || 'Brak miasta' }}</span>
            </li>
          </ul>
        </div>

        <div id="players" class="card">
          <h2>Zawodnicy</h2>

          <ul class="list">
            <li v-for="player in players" :key="player.id">
              <strong>{{ player.first_name }} {{ player.last_name }}</strong>
              <span>{{ player.team_name }}</span>
            </li>
          </ul>
        </div>
      </section>

      <section id="matches" class="card">
        <h2>Mecze</h2>

        <div class="matches">
          <div v-for="match in matches" :key="match.id" class="match-card">
            <div class="club">{{ match.home_team_name }}</div>
            <div class="score">
              {{ match.home_score }} : {{ match.away_score }}
            </div>
            <div class="club">{{ match.away_team_name }}</div>
          </div>
        </div>
      </section>
    </main>
  </div>
</template>

<style scoped>
.app {
  min-height: 100vh;
  background: #f3f6fb;
  color: #1f2937;
  font-family: Arial, sans-serif;
}

.navbar {
  background: #0f172a;
  color: white;
  padding: 18px 40px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.logo {
  font-weight: 800;
  font-size: 22px;
}

.nav-links {
  display: flex;
  gap: 22px;
}

.nav-links a {
  color: white;
  text-decoration: none;
  font-weight: 600;
}

.hero {
  background: linear-gradient(135deg, #16a34a, #0f766e);
  color: white;
  padding: 60px 30px;
  text-align: center;
}

.hero h1 {
  font-size: 42px;
  margin-bottom: 12px;
}

.hero p {
  max-width: 760px;
  margin: 0 auto;
  font-size: 18px;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 30px;
}

.stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 22px;
  margin-bottom: 30px;
}

.stat-card,
.card {
  background: white;
  border-radius: 18px;
  padding: 24px;
  box-shadow: 0 8px 24px rgba(15, 23, 42, 0.08);
}

.stat-card span {
  color: #64748b;
  font-size: 14px;
  font-weight: 700;
  text-transform: uppercase;
}

.stat-card h2 {
  margin: 12px 0 6px;
  font-size: 26px;
}

.stat-card p {
  margin: 0;
  color: #16a34a;
  font-weight: 700;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

button {
  background: #16a34a;
  color: white;
  border: none;
  padding: 10px 18px;
  border-radius: 10px;
  font-weight: 700;
  cursor: pointer;
}

.table-wrapper {
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 18px;
}

th {
  background: #f1f5f9;
  color: #475569;
}

th,
td {
  padding: 14px;
  border-bottom: 1px solid #e2e8f0;
  text-align: left;
}

.team-name {
  font-weight: 700;
}

.grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 22px;
  margin: 30px 0;
}

.list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.list li {
  padding: 14px 0;
  border-bottom: 1px solid #e5e7eb;
  display: flex;
  justify-content: space-between;
  gap: 15px;
}

.list span {
  color: #64748b;
}

.matches {
  display: grid;
  gap: 16px;
}

.match-card {
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  align-items: center;
  background: #f8fafc;
  padding: 18px;
  border-radius: 14px;
}

.club {
  font-weight: 700;
}

.club:last-child {
  text-align: right;
}

.score {
  background: #0f172a;
  color: white;
  padding: 10px 18px;
  border-radius: 12px;
  font-weight: 800;
}

.info {
  background: #e0f2fe;
  padding: 14px;
  border-radius: 10px;
  margin-bottom: 20px;
}

.error {
  background: #fee2e2;
  color: #991b1b;
  padding: 14px;
  border-radius: 10px;
  margin-bottom: 20px;
}

@media (max-width: 800px) {
  .navbar {
    flex-direction: column;
    gap: 15px;
  }

  .nav-links {
    flex-wrap: wrap;
    justify-content: center;
  }

  .hero h1 {
    font-size: 30px;
  }

  .stats,
  .grid {
    grid-template-columns: 1fr;
  }

  .match-card {
    grid-template-columns: 1fr;
    text-align: center;
    gap: 10px;
  }

  .club:last-child {
    text-align: center;
  }
}
</style>
