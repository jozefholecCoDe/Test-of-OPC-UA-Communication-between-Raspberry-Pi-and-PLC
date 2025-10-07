window.onload = function () {
    showTab('register');
};

function showTab(tabId) {
    const tabs = document.querySelectorAll('.tab-content');
    tabs.forEach(tab => {
        tab.style.display = 'none';
    });

    document.getElementById(tabId).style.display = 'block';
}

document.addEventListener('DOMContentLoaded', () => {
    const toggleBtn = document.getElementById('toggle-dark');

    toggleBtn.addEventListener('click', () => {
        document.body.classList.toggle('dark-mode');
        // Save preference in localStorage
        const darkEnabled = document.body.classList.contains('dark-mode');
        localStorage.setItem('darkMode', darkEnabled);
    });

    // Load dark mode preference
    if (localStorage.getItem('darkMode') === 'true') {
        document.body.classList.add('dark-mode');
    }
});