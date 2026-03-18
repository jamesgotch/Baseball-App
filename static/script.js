async function loadYears() {
  const select = document.getElementById('year-select');
  const btn = document.getElementById('explore-btn');
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

document.addEventListener('DOMContentLoaded', () => {
  loadYears();

  const select = document.getElementById('year-select');
  const btn = document.getElementById('explore-btn');

  select.addEventListener('change', () => {
    btn.disabled = !select.value;
  });

  btn.addEventListener('click', () => {
    const year = select.value;
    if (year) {
      // Placeholder for future navigation/filtering
      console.log(`Exploring season: ${year}`);
    }
  });
});
