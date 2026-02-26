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
    const preview = document.createElement('div');
    preview.className = 'input-preview';
    preview.style.float = 'none'; // Override float for stack preview
    preview.style.marginTop = '8px';
    label.appendChild(preview);

    const update = () => {
        const stackStr = stackInput.value;
        const symmetric = symInput.checked;
        const plyThick = parseFloat(thickInput.value) || 0;

        // Split by comma or space for better UX
        const rawPlies = stackStr.split(/[\s,]+/).filter(s => s !== '');

        if (rawPlies.length === 0) {
            preview.innerHTML = '';
            stackInput.removeAttribute('aria-invalid');
            return;
        }

        // Validate
        for (const ply of rawPlies) {
            if (isNaN(ply)) {
                preview.textContent = `Invalid angle: "${ply}"`;
                preview.style.color = '#c0392b'; // Error red
                stackInput.setAttribute('aria-invalid', 'true');
                return;
            }
        }

        // Generate visual badges
        const badges = rawPlies.map(angle => {
            // Composite angle (CCW) vs CSS rotation (CW)
            // 0 deg = horizontal. 90 deg = vertical.
            return `<span class="ply-badge">
                <span class="ply-icon" style="transform: rotate(-${angle}deg)"></span>${angle}°
            </span>`;
        }).join('');

        const count = rawPlies.length * (symmetric ? 2 : 1);
        const totalThick = count * plyThick;
        const thicknessText = `<span style="margin-left: 8px; font-weight: bold; color: #555;">Total: ${formatMetric(totalThick, 'm')} (${symmetric ? 'Sym' : 'Total'})</span>`;

        preview.innerHTML = badges + thicknessText;
        preview.style.color = '';
        stackInput.removeAttribute('aria-invalid');
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

function initKeyboardShortcuts() {
    // Check for Mac for appropriate symbol
    const isMac = navigator.userAgent.toUpperCase().indexOf('MAC') >= 0;
    const shortcutText = isMac ? '⌘↵' : 'Ctrl+Enter';

    // Add visual hint to the button
    const btn = document.getElementById('btn-calculate');
    if (btn) {
        const hint = document.createElement('span');
        hint.className = 'shortcut-hint';
        hint.textContent = shortcutText;
        hint.title = `Press ${shortcutText} to calculate`;
        hint.setAttribute('aria-hidden', 'true');
        btn.appendChild(document.createTextNode(' '));
        btn.appendChild(hint);
    }

    // Add global listener
    document.addEventListener('keydown', (e) => {
        // Trigger calculation on Ctrl+Enter (or Cmd+Enter on Mac)
        if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
            const btn = document.getElementById('btn-calculate');
            if (btn && !btn.disabled) {
                e.preventDefault();
                btn.click();

                // Visual feedback
                btn.style.transform = 'scale(0.98)';
                setTimeout(() => btn.style.transform = '', 100);
            }
        }
    });
}

function initMaterialLibrary() {
    const select = document.getElementById('material-select');
    if (!select) return;

    const materials = {
        'carbon': {
            E1: 140e9, E2: 10e9, G12: 5e9, v12: 0.3,
            Xt: 1500e6, Xc: 1200e6, Yt: 50e6, Yc: 250e6, S: 70e6
        },
        'glass': {
            E1: 43e9, E2: 10e9, G12: 4.5e9, v12: 0.29,
            Xt: 1000e6, Xc: 600e6, Yt: 30e6, Yc: 120e6, S: 40e6
        }
    };

    const materialInputs = [
        'E1', 'E2', 'G12', 'v12',
        'Xt', 'Xc', 'Yt', 'Yc', 'S'
    ];

    // Handle selection change
    select.addEventListener('change', (e) => {
        const mat = materials[e.target.value];
        if (mat) {
            Object.entries(mat).forEach(([key, val]) => {
                const input = document.getElementById(key);
                if (input) {
                    // Format large/small numbers to scientific notation for cleaner input
                    if (Math.abs(val) >= 1e4 || (Math.abs(val) < 1e-3 && val !== 0)) {
                        input.value = val.toExponential().replace('+', '');
                    } else {
                        input.value = val;
                    }

                    // Trigger input event to update previews
                    input.dispatchEvent(new Event('input', { bubbles: true }));

                    // Add a brief highlight effect
                    input.style.transition = 'background-color 0.3s';
                    input.style.backgroundColor = '#e8f4fc';
                    setTimeout(() => {
                        input.style.backgroundColor = '';
                    }, 500);
                }
            });
            showToast(`Loaded ${e.target.options[e.target.selectedIndex].text}`, 'success');
        }
    });

    // Handle manual edits -> switch to Custom
    materialInputs.forEach(id => {
        const input = document.getElementById(id);
        if (input) {
            input.addEventListener('input', (e) => {
                // If the user manually changes a value (and it's trusted, meaning user interaction), set to Custom
                if (e.isTrusted && select.value !== 'custom') {
                    select.value = 'custom';
                }
            });
        }
    });
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        initInputPreviews();
        initStackPreview();
        initMaterialLibrary();
        initKeyboardShortcuts();
    });
} else {
    initInputPreviews();
    initStackPreview();
    initMaterialLibrary();
    initKeyboardShortcuts();
}
