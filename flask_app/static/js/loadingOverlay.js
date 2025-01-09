function showLoadingOverlay() {
    const overlay = document.getElementById('loading-overlay');
    overlay.classList.add('visible');
}

function hideLoadingOverlay() {
    const overlay = document.getElementById('loading-overlay');
    overlay.classList.remove('visible');
}