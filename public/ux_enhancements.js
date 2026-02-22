// Palette: UX Enhancements
// Adds helpful previews and formatted values to inputs

function formatMetric(value, unit) {
    if (!value || isNaN(value)) return '';

    const num = parseFloat(value);
    if (num === 0) return `0 ${unit}`;

    const absNum = Math.abs(num);
    const sign = num < 0 ? '-' : '';

    let formattedNum = absNum;
    let prefix = '';

    if (absNum >= 1e9) {
        formattedNum = absNum / 1e9;
        prefix = 'G';
    } else if (absNum >= 1e6) {
        formattedNum = absNum / 1e6;
        prefix = 'M';
    } else if (absNum >= 1e3) {
        formattedNum = absNum / 1e3;
        prefix = 'k';
    } else if (absNum < 1e-6) {
        formattedNum = absNum * 1e9;
        prefix = 'n';
    } else if (absNum < 1e-3) {
        formattedNum = absNum * 1e6;
        prefix = 'µ';
    } else if (absNum < 1) {
        formattedNum = absNum * 1e3;
        prefix = 'm';
    }

    // Format to max 3 decimal places, remove trailing zeros
    const numStr = parseFloat(formattedNum.toFixed(3)).toString();
    return `${sign}${numStr} ${prefix}${unit}`;
}

function initStackPreview() {
    const stackInput = document.getElementById('stack');
    const symInput = document.getElementById('symmetry');
    const thickInput = document.getElementById('thickness');

    if (!stackInput || !symInput || !thickInput) return;

    const label = stackInput.parentElement;
    const preview = document.createElement('span');
    preview.className = 'input-preview';
    label.insertBefore(preview, stackInput);

    const update = () => {
        const stackStr = stackInput.value;
        const symmetric = symInput.checked;
        const plyThick = parseFloat(thickInput.value) || 0;

        const plies = stackStr.split(',').filter(s => s.trim() !== '');
        if (plies.length === 0) {
            preview.textContent = '';
            return;
        }

        const count = plies.length * (symmetric ? 2 : 1);
        const totalThick = count * plyThick;
        const code = `[${plies.map(s => s.trim()).join('/')}]${symmetric ? 's' : 'T'}`;

        preview.textContent = `${code} • ${formatMetric(totalThick, 'm')}`;
    };

    stackInput.addEventListener('input', update);
    symInput.addEventListener('change', update);
    thickInput.addEventListener('input', update);

    // Initial update
    update();
}

function initInputPreviews() {
    // Select all numeric inputs, not just those in the grid
    const inputs = document.querySelectorAll('input[type="number"]');

    inputs.forEach(input => {
        // Skip Poisson's ratio (v12) as it's dimensionless
        if (input.id === 'v12') return;

        const unit = input.id === 'thickness' ? 'm' : 'Pa';
        const label = input.parentElement;

        // Create preview element
        const preview = document.createElement('span');
        preview.className = 'input-preview';
        preview.textContent = formatMetric(input.value, unit);
        preview.setAttribute('aria-hidden', 'true'); // Visual helper only

        // Insert before input
        label.insertBefore(preview, input);

        // Update on input
        input.addEventListener('input', (e) => {
            preview.textContent = formatMetric(e.target.value, unit);
        });
    });
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        initInputPreviews();
        initStackPreview();
    });
} else {
    initInputPreviews();
    initStackPreview();
}
