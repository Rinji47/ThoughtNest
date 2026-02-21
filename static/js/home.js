// ========================================
// Home Page JavaScript
// ========================================

document.addEventListener('DOMContentLoaded', function() {
    // Search and filter functionality
    const searchInput = document.getElementById('searchInput');
    const categoryFilter = document.getElementById('categoryFilter');
    const postsContainer = document.getElementById('postsContainer');
    const noResults = document.getElementById('noResults');

    if (searchInput && categoryFilter) {
        searchInput.addEventListener('keyup', filterPosts);
        categoryFilter.addEventListener('change', filterPosts);
    }

    // Subscribe form
    const subscribeForm = document.getElementById('subscribeForm');
    if (subscribeForm) {
        subscribeForm.addEventListener('submit', handleSubscribe);
    }

    // Like button functionality (simple toggle without backend)
    const postLikeButtons = document.querySelectorAll('.post-likes');
    postLikeButtons.forEach(button => {
        button.style.cursor = 'pointer';
        button.addEventListener('click', function(e) {
            e.preventDefault();
            toggleLike(this);
        });
    });
});

function filterPosts() {
    const searchTerm = document.getElementById('searchInput')?.value.toLowerCase() || '';
    const selectedCategory = document.getElementById('categoryFilter')?.value || '';
    const posts = document.querySelectorAll('.post-card');
    let visibleCount = 0;

    posts.forEach(post => {
        const title = post.querySelector('.post-title')?.textContent.toLowerCase() || '';
        const excerpt = post.querySelector('.post-excerpt')?.textContent.toLowerCase() || '';
        const postCategoryId = post.getAttribute('data-category') || '';

        const matchesSearch = title.includes(searchTerm) || excerpt.includes(searchTerm);
        const matchesCategory = !selectedCategory || postCategoryId === selectedCategory;

        if (matchesSearch && matchesCategory) {
            post.style.display = 'flex';
            visibleCount++;
        } else {
            post.style.display = 'none';
        }
    });

    const noResults = document.getElementById('noResults');
    if (visibleCount === 0 && noResults) {
        noResults.style.display = 'block';
    } else if (noResults) {
        noResults.style.display = 'none';
    }
}

function handleSubscribe(e) {
    e.preventDefault();
    const email = e.target.querySelector('input[type="email"]').value;
    const message = document.getElementById('subscribeMessage');

    if (email) {
        // Simulate backend submission
        message.textContent = 'Thank you for subscribing! Check your email for confirmation.';
        message.style.color = '#27ae60';
        e.target.reset();

        setTimeout(() => {
            message.textContent = '';
        }, 3000);
    }
}

function toggleLike(element) {
    const likesText = element.textContent;
    const currentLikes = parseInt(likesText.match(/\d+/)[0]);
    const isLiked = element.classList.contains('liked');

    if (isLiked) {
        element.textContent = `❤️ ${currentLikes - 1} likes`;
        element.classList.remove('liked');
    } else {
        element.textContent = `❤️ ${currentLikes + 1} likes`;
        element.classList.add('liked');
    }
}
