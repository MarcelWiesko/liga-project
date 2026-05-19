<script setup>
import { ref, onMounted } from 'vue'

const teams = ref([])
const players = ref([])
const matches = ref([])
const table = ref([])
const bestTeam = ref(null)
const bestPlayer = ref(null)

const API = 'http://127.0.0.1:8000/api'

onMounted(async () => {
  teams.value = await fetch(`${API}/teams/`).then(res => res.json())

  players.value = await fetch(`${API}/players/`).then(res => res.json())

  matches.value = await fetch(`${API}/matches/`).then(res => res.json())

  table.value = await fetch(`${API}/table/`).then(res => res.json())

  bestTeam.value = await fetch(`${API}/best-team/`).then(res => res.json())

  bestPlayer.value = await fetch(`${API}/best-player/`).then(res => res.json())
})
</script>

<template>
  <main class="container">
    <h1>⚽ System Liga</h1>

    <section class="card">
      <h2>Najlepsza drużyna</h2>

      <div v-if="bestTeam">
        <p>
          <strong>{{ bestTeam.team }}</strong>
        </p>

        <p>Punkty: {{ bestTeam.points }}</p>
      </div>
    </section>

    <section class="card">
      <h2>Najlepszy zawodnik</h2>

      <div v-if="bestPlayer">
        <p>
          <strong>{{ bestPlayer.player }}</strong>
        </p>

        <p>Drużyna: {{ bestPlayer.team }}</p>

        <p>Gole: {{ bestPlayer.goals }}</p>
      </div>
    </section>

    <section class="card">
      <h2>Tabela ligowa</h2>

      <table>
        <thead>
          <tr>
            <th>#</th>
            <th>Drużyna</th>
            <th>Punkty</th>
            <th>Wygrane</th>
            <th>Remisy</th>
            <th>Porażki</th>
            <th>Bramki</th>
            <th>Bilans</th>
          </tr>
        </thead>

        <tbody>
          <tr
            v-for="(row, index) in table"
            :key="row.team_id"
          >
            <td>{{ index + 1 }}</td>
            <td>{{ row.team }}</td>
            <td>{{ row.points }}</td>
            <td>{{ row.wins }}</td>
            <td>{{ row.draws }}</td>
            <td>{{ row.losses }}</td>
            <td>{{ row.goals_for }} : {{ row.goals_against }}</td>
            <td>{{ row.goal_difference }}</td>
          </tr>
        </tbody>
      </table>
    </section>

    <section class="card">
      <h2>Drużyny</h2>

      <ul>
        <li
          v-for="team in teams"
          :key="team.id"
        >
          {{ team.name }} — {{ team.city }}
        </li>
      </ul>
    </section>

    <section class="card">
      <h2>Zawodnicy</h2>

      <ul>
        <li
          v-for="player in players"
          :key="player.id"
        >
          {{ player.first_name }}
          {{ player.last_name }}
          — {{ player.team_name }}
        </li>
      </ul>
    </section>

    <section class="card">
      <h2>Mecze</h2>

      <ul>
        <li
          v-for="match in matches"
          :key="match.id"
        >
          {{ match.home_team_name }}
          {{ match.home_score }}
          :
          {{ match.away_score }}
          {{ match.away_team_name }}
        </li>
      </ul>
    </section>
  </main>
</template>

<style scoped>
body {
  margin: 0;
  padding: 0;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 30px;
  font-family: Arial, sans-serif;
  background: #f5f5f5;
  min-height: 100vh;
}

h1 {
  text-align: center;
  margin-bottom: 30px;
}

.card {
  background: white;
  padding: 20px;
  margin-bottom: 25px;
  border-radius: 14px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

table {
  width: 100%;
  border-collapse: collapse;
}

th {
  background: #eeeeee;
}

th,
td {
  padding: 12px;
  border-bottom: 1px solid #ddd;
  text-align: left;
}

ul {
  padding-left: 20px;
}

li {
  margin-bottom: 8px;
}
</style>
