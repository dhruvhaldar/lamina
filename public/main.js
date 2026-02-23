// Extracted from public/index.html

function showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.role = type === 'error' ? 'alert' : 'status';
    toast.textContent = message;

    container.appendChild(toast);

    // Remove after 5 seconds
    setTimeout(() => {
        toast.style.opacity = '0';
        setTimeout(() => toast.remove(), 300);
    }, 5000);
}

function setLoading(btn, isLoading) {
    if (isLoading) {
        btn.setAttribute('disabled', 'true');
        btn.setAttribute('aria-busy', 'true');
        btn.dataset.originalText = btn.innerText;
        btn.innerHTML = '<span class="spinner"></span> Processing...';
    } else {
        btn.removeAttribute('disabled');
        btn.setAttribute('aria-busy', 'false');
        btn.innerText = btn.dataset.originalText;
    }
}

async function getLaminateData() {
    const E1 = parseFloat(document.getElementById('E1').value);
    const E2 = parseFloat(document.getElementById('E2').value);
    const G12 = parseFloat(document.getElementById('G12').value);
    const v12 = parseFloat(document.getElementById('v12').value);

    const stackStr = document.getElementById('stack').value;
    const stack = stackStr.split(',').map(s => parseFloat(s.trim()));
    const symmetry = document.getElementById('symmetry').checked;
    const thickness = parseFloat(document.getElementById('thickness').value);

    return {
        material: { E1, E2, G12, v12 },
        stack,
        symmetry,
        thickness
    };
}

async function getLimits() {
     return {
        xt: parseFloat(document.getElementById('Xt').value),
        xc: parseFloat(document.getElementById('Xc').value),
        yt: parseFloat(document.getElementById('Yt').value),
        yc: parseFloat(document.getElementById('Yc').value),
        s: parseFloat(document.getElementById('S').value)
     };
}

async function handleApiError(response) {
    const errData = await response.json().catch(() => ({}));
    let msg = 'Server error';
    if (errData.detail) {
        if (Array.isArray(errData.detail)) {
            msg = errData.detail.map(e => {
                const field = e.loc ? e.loc[e.loc.length - 1] : 'Error';
                return `${field}: ${e.msg.replace('Value error, ', '')}`;
            }).join('\n');
        } else {
            msg = errData.detail;
        }
    }
    throw new Error(msg);
}

function formatEngineeringConstants(props) {
    const items = [
        { label: 'Ex', value: props.Ex, unit: 'Pa', convert: v => (v/1e9).toFixed(2) + ' GPa', title: "Longitudinal Modulus" },
        { label: 'Ey', value: props.Ey, unit: 'Pa', convert: v => (v/1e9).toFixed(2) + ' GPa', title: "Transverse Modulus" },
        { label: 'Gxy', value: props.Gxy, unit: 'Pa', convert: v => (v/1e9).toFixed(2) + ' GPa', title: "Shear Modulus" },
        { label: 'vxy', value: props.vxy, unit: '', convert: v => v.toFixed(3), title: "Poisson's Ratio" }
    ];

    const copyText = items.map(i => `${i.label}: ${i.convert(i.value)}`).join('\n');

    return `
        <div class="result-container">
            <button class="copy-btn" aria-label="Copy Engineering Constants">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M7.5 3.375c0-1.036.84-1.875 1.875-1.875h.375a3.75 3.75 0 013.75 3.75v1.875C13.5 8.161 14.34 9 15.375 9h1.875A3.75 3.75 0 0121 12.75v3.375C21 17.16 20.16 18 19.125 18h-9.75A1.875 1.875 0 017.5 16.125V3.375z" />
                    <path d="M15 5.25a5.23 5.23 0 00-1.279-3.434 9.768 9.768 0 016.963 6.963A5.23 5.23 0 0017.25 5.25h-2.25z" />
                    <path d="M4.5 4.5a2.25 2.25 0 00-2.25 2.25v13.5A2.25 2.25 0 004.5 22.5h11.25a2.25 2.25 0 002.25-2.25V19.5h-9.375A3.375 3.375 0 015.25 16.125V4.5h-.75z" />
                </svg>
                Copy
            </button>
            <div class="clipboard-data" style="display:none; white-space: pre;">${copyText}</div>
            <div class="input-grid" style="grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));">
                ${items.map(item => `
                    <div class="result-item" title="${item.title}">
                        <strong>${item.label}:</strong> ${item.convert(item.value)}
                    </div>
                `).join('')}
            </div>
        </div>
    `;
}

function formatMatrix(matrix) {
    // matrix is 6x6 array (list of lists)
    return matrix.map(row =>
        row.map(val => val.toExponential(2).padStart(11)).join('  ')
    ).join('\n');
}

async function copyToClipboard(btn) {
    const container = btn.closest('.result-container');
    const source = container.querySelector('pre') || container.querySelector('.clipboard-data');
    const text = source ? (source.innerText || source.textContent) : '';

    if (!text) return;

    try {
        await navigator.clipboard.writeText(text);
        const originalContent = btn.innerHTML;

        // Visual feedback
        btn.innerHTML = `
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
            </svg>
            Copied!
        `;
        btn.style.color = '#27ae60';
        btn.style.borderColor = '#27ae60';

        setTimeout(() => {
            btn.innerHTML = originalContent;
            btn.style.color = '';
            btn.style.borderColor = '';
        }, 2000);
    } catch (err) {
        console.error('Failed to copy: ', err);
        showToast('Failed to copy to clipboard', 'error');
    }
}

async function calculate(btn) {
    setLoading(btn, true);
    try {
        const data = await getLaminateData();
        const response = await fetch('/api/calculate', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(data)
        });

        if (!response.ok) {
            await handleApiError(response);
        }

        const result = await response.json();

        const constsOut = document.getElementById('constants-output');
        constsOut.innerHTML = formatEngineeringConstants(result.properties);
        constsOut.classList.remove('empty-state');

        const abdOut = document.getElementById('abd-output');
        abdOut.innerHTML = `
            <div class="result-container">
                <button class="copy-btn" aria-label="Copy ABD Matrix">
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
                        <path d="M7.5 3.375c0-1.036.84-1.875 1.875-1.875h.375a3.75 3.75 0 013.75 3.75v1.875C13.5 8.161 14.34 9 15.375 9h1.875A3.75 3.75 0 0121 12.75v3.375C21 17.16 20.16 18 19.125 18h-9.75A1.875 1.875 0 017.5 16.125V3.375z" />
                        <path d="M15 5.25a5.23 5.23 0 00-1.279-3.434 9.768 9.768 0 016.963 6.963A5.23 5.23 0 0017.25 5.25h-2.25z" />
                        <path d="M4.5 4.5a2.25 2.25 0 00-2.25 2.25v13.5A2.25 2.25 0 004.5 22.5h11.25a2.25 2.25 0 002.25-2.25V19.5h-9.375A3.375 3.375 0 015.25 16.125V4.5h-.75z" />
                    </svg>
                    Copy
                </button>
                <pre>${formatMatrix(result.ABD)}</pre>
            </div>
        `;
        abdOut.classList.remove('empty-state');
        showToast('Calculation complete', 'success');
    } catch (error) {
        console.error('Error:', error);
        showToast(error.message, 'error');
    } finally {
        setLoading(btn, false);
    }
}

async function plotPolar(btn) {
    setLoading(btn, true);
    try {
        const data = await getLaminateData();
        const response = await fetch('/api/polar', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(data)
        });

        if (!response.ok) {
            await handleApiError(response);
        }

        const result = await response.json();
        document.getElementById('polar-plot').classList.remove('empty-state');
        // drawPolar is global from polar_plot.js
        if (typeof drawPolar === 'function') {
            drawPolar(result);
        } else {
             throw new Error('Polar plot library not loaded');
        }
        showToast('Stiffness polar plotted', 'success');
    } catch (error) {
        console.error('Error:', error);
        showToast(error.message, 'error');
    } finally {
        setLoading(btn, false);
    }
}

async function plotEnvelope(btn) {
    setLoading(btn, true);
    try {
        const lamData = await getLaminateData();
        const limits = await getLimits();
        const response = await fetch('/api/failure', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({laminate: lamData, limits})
        });

        if (!response.ok) {
            await handleApiError(response);
        }

        const result = await response.json();
        document.getElementById('envelope-plot').classList.remove('empty-state');
        // drawEnvelope is global from failure_envelope.js
        if (typeof drawEnvelope === 'function') {
            drawEnvelope(result);
        } else {
            throw new Error('Failure envelope library not loaded');
        }
        showToast('Failure envelope plotted', 'success');
    } catch (error) {
        console.error('Error:', error);
        showToast(error.message, 'error');
    } finally {
        setLoading(btn, false);
    }
}

// Initialization and Event Listeners
document.addEventListener('DOMContentLoaded', () => {
    // Attach listeners to buttons
    const btnCalculate = document.getElementById('btn-calculate');
    if (btnCalculate) {
        btnCalculate.addEventListener('click', function() { calculate(this); });
    }

    const btnPolar = document.getElementById('btn-polar');
    if (btnPolar) {
        btnPolar.addEventListener('click', function() { plotPolar(this); });
    }

    const btnEnvelope = document.getElementById('btn-envelope');
    if (btnEnvelope) {
        btnEnvelope.addEventListener('click', function() { plotEnvelope(this); });
    }

    // Delegate copy button clicks
    document.addEventListener('click', function(e) {
        const btn = e.target.closest('.copy-btn');
        if (btn) {
            copyToClipboard(btn);
        }
    });
});
