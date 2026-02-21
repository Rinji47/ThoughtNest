(() => {
  const input = document.getElementById('postTags');
  const suggestionsEl = document.getElementById('tagSuggestions');
  const popularTags = document.querySelectorAll('.tag-chip');
  const dataEl = document.getElementById('allTagsData');

  if (!input || !suggestionsEl || !dataEl) {
    return;
  }

  let allTags = [];
  try {
    allTags = JSON.parse(dataEl.textContent || '[]');
  } catch (err) {
    allTags = [];
  }

  const normalize = (value) => value.trim().toLowerCase();

  const getCurrentToken = (value) => {
    const parts = value.split(',');
    return {
      parts,
      current: parts[parts.length - 1].trim(),
    };
  };

  const renderSuggestions = (matches) => {
    suggestionsEl.innerHTML = '';
    if (!matches.length) {
      suggestionsEl.classList.remove('is-open');
      return;
    }

    matches.forEach((tag) => {
      const button = document.createElement('button');
      button.type = 'button';
      button.className = 'tag-suggestion-item';
      button.textContent = tag;
      button.addEventListener('click', () => addTagToInput(tag));
      suggestionsEl.appendChild(button);
    });

    suggestionsEl.classList.add('is-open');
  };

  const addTagToInput = (tag) => {
    const token = getCurrentToken(input.value);
    const updatedParts = token.parts.slice(0, -1).map((part) => part.trim()).filter(Boolean);

    if (!updatedParts.some((part) => normalize(part) === normalize(tag))) {
      updatedParts.push(tag);
    }

    input.value = updatedParts.join(', ') + ', ';
    input.focus();
    renderSuggestions([]);
  };

  input.addEventListener('input', (event) => {
    const token = getCurrentToken(event.target.value).current;
    const query = normalize(token);

    if (!query) {
      renderSuggestions([]);
      return;
    }

    const matches = allTags
      .filter((tag) => normalize(tag).includes(query))
      .slice(0, 12);

    renderSuggestions(matches);
  });

  input.addEventListener('blur', () => {
    setTimeout(() => renderSuggestions([]), 150);
  });

  popularTags.forEach((chip) => {
    chip.addEventListener('click', () => addTagToInput(chip.dataset.tag || chip.textContent));
  });
})();
