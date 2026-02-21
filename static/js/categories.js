// ========================================
// Categories Page JavaScript
// ========================================

document.addEventListener('DOMContentLoaded', function() {
    // Add smooth scroll to category cards
    const categoryCards = document.querySelectorAll('.category-card');
    categoryCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.cursor = 'pointer';
        });
    });

    // Tag filtering removed to allow default link behavior
});
