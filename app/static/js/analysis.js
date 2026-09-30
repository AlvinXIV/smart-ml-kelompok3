/**
 * AI Predictive Maintenance - Analysis Form & Pipeline Animation
 */

document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('machineAnalysisForm');
  const overlay = document.getElementById('analysisScanningOverlay');
  const presetNormalBtn = document.getElementById('presetNormal');
  const presetHighRiskBtn = document.getElementById('presetHighRisk');

  // Load Presets for quick evaluation and demonstration
  if (presetNormalBtn) {
    presetNormalBtn.addEventListener('click', () => {
      document.getElementById('machine_type').value = 'L';
      document.getElementById('air_temp').value = '298.1';
      document.getElementById('process_temp').value = '308.6';
      document.getElementById('rotational_speed').value = '1551';
      document.getElementById('torque').value = '42.8';
      document.getElementById('tool_wear').value = '120';
    });
  }

  if (presetHighRiskBtn) {
    presetHighRiskBtn.addEventListener('click', () => {
      document.getElementById('machine_type').value = 'M';
      document.getElementById('air_temp').value = '301.2';
      document.getElementById('process_temp').value = '310.8';
      document.getElementById('rotational_speed').value = '1320';
      document.getElementById('torque').value = '68.5';
      document.getElementById('tool_wear').value = '210';
    });
  }

  // Handle Form Submission with Pipeline Scanning Animation
  if (form && overlay) {
    form.addEventListener('submit', (e) => {
      e.preventDefault();
      overlay.style.display = 'flex';

      const steps = [
        document.getElementById('scanStep1'),
        document.getElementById('scanStep2'),
        document.getElementById('scanStep3'),
        document.getElementById('scanStep4'),
        document.getElementById('scanStep5')
      ];

      let currentStep = 0;

      const advanceStep = () => {
        if (currentStep < steps.length) {
          if (currentStep > 0) {
            steps[currentStep - 1].classList.remove('active');
            steps[currentStep - 1].classList.add('done');
            steps[currentStep - 1].querySelector('.step-status-icon').innerHTML = '✓';
          }
          steps[currentStep].classList.add('active');
          currentStep++;
          setTimeout(advanceStep, 350);
        } else {
          // Finalize and submit form
          setTimeout(() => {
            form.submit();
          }, 300);
        }
      };

      advanceStep();
    });
  }
});
