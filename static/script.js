function escapeHtml(value) {
  return String(value)
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#39;');
}

const STAT_LABELS = {
  G: 'Games Played',
  AB: 'At Bats',
  R: 'Runs',
  H: 'Hits',
  '2B': 'Doubles',
  '3B': 'Triples',
  HR: 'Home Runs',
  RBI: 'Runs Batted In',
  SB: 'Stolen Bases',
  CS: 'Caught Stealing',
  BB: 'Walks',
  SO: 'Strikeouts',
  IBB: 'Intentional Walks',
  HBP: 'Hit By Pitch',
  SH: 'Sacrifice Hits',
  SF: 'Sacrifice Flies',
  GIDP: 'Grounded Into Double Play'
};

async function loadYears() {
  const select = document.getElementById('year-select');
  const statSeasons = document.getElementById('stat-seasons');

  try {
    const response = await fetch('/years');
    if (!response.ok) throw new Error(`Server error: ${response.status}`);

    const years = await response.json();

    select.innerHTML = '<option value="">— Select a season —</option>';
    years.forEach(year => {
      const option = document.createElement('option');
      option.value = year;
      option.textContent = year;
      select.appendChild(option);
    });

    select.disabled = false;
    statSeasons.textContent = years.length;
  } catch (err) {
    console.error('Failed to load years:', err);
    select.innerHTML = '<option value="">Failed to load seasons</option>';
  }
}

async function loadTeams(year) {
  const teamsList = document.getElementById('teams-list');
  const teamsMeta = document.getElementById('teams-meta');
  const playersList = document.getElementById('players-list');
  const playerStats = document.getElementById('player-stats');

  teamsMeta.textContent = `Loading ${year}...`;
  teamsList.innerHTML = '<div class="teams-placeholder">Loading teams...</div>';
  playersList.innerHTML = '<div class="teams-placeholder">Select a team to load players.</div>';
  playerStats.innerHTML = '<div class="teams-placeholder">Select a player to view batting stats.</div>';

  try {
    const response = await fetch(`/teams?year=${encodeURIComponent(year)}`);
    if (!response.ok) throw new Error(`Server error: ${response.status}`);

    const teams = await response.json();

    if (!Array.isArray(teams) || teams.length === 0) {
      teamsMeta.textContent = `${year} - 0 teams`;
      teamsList.innerHTML = '<div class="teams-placeholder">No teams found for this season.</div>';
      return;
    }

    const grouped = {};
    teams.forEach(team => {
      const lead = team.lead || 'Unknown';
      const division = team.division || 'Unknown';
      const name = team.name;

      if (!name) {
        return;
      }

      if (!grouped[lead]) {
        grouped[lead] = {};
      }

      if (!grouped[lead][division]) {
        grouped[lead][division] = [];
      }

      grouped[lead][division].push(team);
    });

    const leagueOrder = Object.keys(grouped).sort();

    let html = '';
    leagueOrder.forEach(lead => {
      const divisionOrder = Object.keys(grouped[lead]).sort();

      html += `<section class="league-group"><h3 class="league-title">${escapeHtml(lead)}</h3>`;

      divisionOrder.forEach(division => {
        const teamItems = grouped[lead][division]
          .sort((a, b) => {
            const winsA = Number(a.wins || 0);
            const winsB = Number(b.wins || 0);

            if (winsA !== winsB) {
              return winsB - winsA;
            }

            return (a.name || '').localeCompare(b.name || '');
          })
          .map(team => {
            const name = escapeHtml(team.name);
            const teamID = escapeHtml(team.teamID);
            const teamLead = escapeHtml(team.lead);
            const teamDivision = escapeHtml(team.division);
            const wins = Number(team.wins || 0);
            return `<li><button class="team-btn" data-team-id="${teamID}" data-team-name="${name}" data-lead="${teamLead}" data-division="${teamDivision}" type="button">${name} (${wins} wins)</button></li>`;
          })
          .join('');

        html += `<div class="division-group"><h4 class="division-title">${escapeHtml(division)}</h4><ul class="division-teams">${teamItems}</ul></div>`;
      });

      html += '</section>';
    });

    teamsMeta.textContent = `${year} - ${teams.length} teams`;
    teamsList.innerHTML = html;
  } catch (err) {
    console.error('Failed to load teams:', err);
    teamsMeta.textContent = `${year} - unavailable`;
    const message = err && err.message ? escapeHtml(err.message) : 'Unknown client error';
    teamsList.innerHTML = `<div class="teams-placeholder">Failed to load teams: ${message}</div>`;
  }
}

async function loadPlayers(year, teamID, teamName, lead, division) {
  const playersList = document.getElementById('players-list');
  const playerStats = document.getElementById('player-stats');

  playersList.innerHTML = `<div class="teams-placeholder">Loading players for ${escapeHtml(teamName)}...</div>`;
  playerStats.innerHTML = '<div class="teams-placeholder">Select a player to view batting stats.</div>';

  try {
    const response = await fetch(
      `/players?year=${encodeURIComponent(year)}&teamID=${encodeURIComponent(teamID)}`
    );
    if (!response.ok) throw new Error(`Server error: ${response.status}`);

    const players = await response.json();

    if (!Array.isArray(players) || players.length === 0) {
      playersList.innerHTML = '<div class="teams-placeholder">No players found for this team in this year.</div>';
      return;
    }

    const title = `<p class="context-line">${escapeHtml(lead)} · ${escapeHtml(division)} Division · ${escapeHtml(teamName)}</p>`;
    const playerButtons = players
      .map(player => {
        const name = escapeHtml(player.name);
        const playerID = escapeHtml(player.playerID);
        return `<button class="player-btn" data-player-id="${playerID}" data-player-name="${name}" data-team-id="${escapeHtml(teamID)}" data-team-name="${escapeHtml(teamName)}" type="button">${name}</button>`;
      })
      .join('');

    playersList.innerHTML = `${title}<div class="players-grid">${playerButtons}</div>`;
  } catch (err) {
    console.error('Failed to load players:', err);
    playersList.innerHTML = '<div class="teams-placeholder">Failed to load players.</div>';
  }
}

async function loadPlayerStats(year, teamID, teamName, playerID, playerName) {
  const playerStats = document.getElementById('player-stats');
  playerStats.innerHTML = `<div class="teams-placeholder">Loading stats for ${escapeHtml(playerName)}...</div>`;

  try {
    const response = await fetch(
      `/player-stats?year=${encodeURIComponent(year)}&teamID=${encodeURIComponent(teamID)}&playerID=${encodeURIComponent(playerID)}`
    );
    if (!response.ok) throw new Error(`Server error: ${response.status}`);

    const payload = await response.json();
    const stats = payload.stats || {};

    const statCards = Object.entries(stats)
      .map(([key, value]) => {
        const label = STAT_LABELS[key] || key;
        return `<div class="stat-card"><span class="stat-key">${escapeHtml(label)}</span><span class="stat-number">${escapeHtml(value)}</span></div>`;
      })
      .join('');

    playerStats.innerHTML = `
      <p class="context-line">${escapeHtml(teamName)} · ${escapeHtml(payload.year)}</p>
      <h4 class="player-name">${escapeHtml(payload.name || playerName)}</h4>
      <p class="avg-line">Batting Average: <strong>${escapeHtml(payload.batting_average)}</strong></p>
      <div class="stats-grid">${statCards}</div>
    `;
  } catch (err) {
    console.error('Failed to load player stats:', err);
    playerStats.innerHTML = '<div class="teams-placeholder">Failed to load player stats.</div>';
  }
}

document.addEventListener('DOMContentLoaded', () => {
  loadYears();

  const select = document.getElementById('year-select');
  const teamsList = document.getElementById('teams-list');
  const playersList = document.getElementById('players-list');
  const teamsMeta = document.getElementById('teams-meta');
  const playerStats = document.getElementById('player-stats');

  select.addEventListener('change', async () => {
    if (select.value) {
      await loadTeams(select.value);
    } else {
      teamsMeta.textContent = 'Select a season to view teams';
      teamsList.innerHTML = '<div class="teams-placeholder">No teams loaded yet.</div>';
      playersList.innerHTML = '<div class="teams-placeholder">Select a team to load players.</div>';
      playerStats.innerHTML = '<div class="teams-placeholder">Select a player to view batting stats.</div>';
    }
  });

  teamsList.addEventListener('click', async event => {
    const button = event.target.closest('.team-btn');
    if (!button || !select.value) {
      return;
    }

    const teamID = button.dataset.teamId;
    const teamName = button.dataset.teamName;
    const lead = button.dataset.lead;
    const division = button.dataset.division;

    if (!teamID || !teamName) {
      return;
    }

    await loadPlayers(select.value, teamID, teamName, lead || '', division || '');
  });

  playersList.addEventListener('click', async event => {
    const button = event.target.closest('.player-btn');
    if (!button || !select.value) {
      return;
    }

    const playerID = button.dataset.playerId;
    const playerName = button.dataset.playerName;
    const teamID = button.dataset.teamId;
    const teamName = button.dataset.teamName;

    if (!playerID || !teamID || !playerName || !teamName) {
      return;
    }

    await loadPlayerStats(select.value, teamID, teamName, playerID, playerName);
  });
});
