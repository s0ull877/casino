document.addEventListener('DOMContentLoaded', function() {
    const divs = document.querySelectorAll('.elemnt');
    const toggleButton = document.getElementById('toggleButton');
    let isExpanded = false;

    if (divs.length > 3) {
        for (let i = 3; i < divs.length; i++) {
            divs[i].classList.add('hidden');
        }
    }

    toggleButton.addEventListener('click', function() {
        isExpanded = !isExpanded;
        divs.forEach((div, index) => {
            if (index >= 3) {
                div.classList.toggle('hidden', !isExpanded);
            }
        });
        toggleButton.textContent = isExpanded ? 'Скрыть полную историю' : 'Полная история';
    });
});
