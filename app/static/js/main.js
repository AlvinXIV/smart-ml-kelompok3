/**
 * AI Predictive Maintenance - Main Application JavaScript
 */

document.addEventListener('DOMContentLoaded', () => {
  // Mobile sidebar drawer toggle
  const mobileToggle = document.getElementById('mobileMenuToggle');
  const sidebar = document.getElementById('appSidebar');

  if (mobileToggle && sidebar) {
    mobileToggle.addEventListener('click', (e) => {
      e.stopPropagation();
      sidebar.classList.toggle('show-mobile');
    });

    document.addEventListener('click', (e) => {
      if (!sidebar.contains(e.target) && !mobileToggle.contains(e.target)) {
        sidebar.classList.remove('show-mobile');
      }
    });
  }

  // Generic Modal Close Handlers
  document.querySelectorAll('.modal-close-trigger').forEach((btn) => {
    btn.addEventListener('click', () => {
      const modal = btn.closest('.modal-backdrop-wrap');
      if (modal) modal.style.display = 'none';
    });
  });

  // Table row search & filter in History page
  const historySearch = document.getElementById('historySearch');
  const actionFilter = document.getElementById('actionFilter');
  const historyTable = document.getElementById('historyTable');

  if (historySearch && historyTable) {
    const filterTable = () => {
      const query = historySearch.value.toLowerCase();
      const action = actionFilter ? actionFilter.value.toLowerCase() : 'all';
      const rows = historyTable.querySelectorAll('tbody tr');

      rows.forEach((row) => {
        const text = row.innerText.toLowerCase();
        const actionBadge = row.querySelector('.action-col');
        const actionText = actionBadge ? actionBadge.innerText.toLowerCase() : '';

        const matchesQuery = text.includes(query);
        const matchesAction = action === 'all' || actionText.includes(action);

        if (matchesQuery && matchesAction) {
          row.style.display = '';
        } else {
          row.style.display = 'none';
        }
      });
    };

    historySearch.addEventListener('input', filterTable);
    if (actionFilter) actionFilter.addEventListener('change', filterTable);
  }
});

// Helper function to view history record details
function openRecordDetails(record) {
  const modal = document.getElementById('recordDetailModal');
  if (!modal) return;

  document.getElementById('modalRecordId').innerText = record.id || 'AN-XXXX';
  document.getElementById('modalDate').innerText = record.date || 'N/A';
  document.getElementById('modalMachineType').innerText = record.machine_type || 'N/A';
  document.getElementById('modalAirTemp').innerText = record.air_temp + ' K';
  document.getElementById('modalProcessTemp').innerText = record.process_temp + ' K';
  document.getElementById('modalSpeed').innerText = record.rotational_speed + ' rpm';
  document.getElementById('modalTorque').innerText = record.torque + ' Nm';
  document.getElementById('modalToolWear').innerText = record.tool_wear + ' min';

  document.getElementById('modalPred').innerText = record.failure_pred;
  document.getElementById('modalProb').innerText = record.failure_prob + '%';
  document.getElementById('modalCluster').innerText = 'Cluster ' + record.cluster + ' (' + (record.cluster_condition || '') + ')';
  document.getElementById('modalAction').innerText = record.action + ' (Q: ' + record.q_value + ')';

  modal.style.display = 'flex';
}
