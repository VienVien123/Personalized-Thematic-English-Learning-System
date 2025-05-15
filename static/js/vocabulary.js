import { getAuthHeaders } from './auth.js';

// API endpoints
const API_URL = '/api';

// Get all topics
async function getTopics() {
    try {
        const response = await fetch(`${API_URL}/topics/`);
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error fetching topics:', error);
        throw error;
    }
}

// Get all words
async function getWords() {
    try {
        const response = await fetch(`${API_URL}/words/`, {
            headers: getAuthHeaders()
        });
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error fetching words:', error);
        throw error;
    }
}

// Add new word
async function addWord(wordData) {
    try {
        const response = await fetch(`${API_URL}/words/`, {
            method: 'POST',
            headers: getAuthHeaders(),
            body: JSON.stringify(wordData)
        });
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error adding word:', error);
        throw error;
    }
}

// Update word
async function updateWord(wordId, wordData) {
    try {
        const response = await fetch(`${API_URL}/words/${wordId}/`, {
            method: 'PUT',
            headers: getAuthHeaders(),
            body: JSON.stringify(wordData)
        });
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error updating word:', error);
        throw error;
    }
}

// Delete word
async function deleteWord(wordId) {
    try {
        const response = await fetch(`${API_URL}/words/${wordId}/`, {
            method: 'DELETE',
            headers: getAuthHeaders()
        });
        return response.ok;
    } catch (error) {
        console.error('Error deleting word:', error);
        throw error;
    }
}

// Mark word as learned
async function markWordLearned(wordId) {
    try {
        const response = await fetch(`${API_URL}/words/${wordId}/`, {
            method: 'PATCH',
            headers: getAuthHeaders(),
            body: JSON.stringify({ is_learned: true })
        });
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error marking word as learned:', error);
        throw error;
    }
}

// Create word card HTML
function createWordCard(word) {
    return `
        <div class="col-md-4 mb-4">
            <div class="card h-100 ${word.is_learned ? 'bg-light' : ''}">
                <div class="card-body">
                    <h5 class="card-title">${word.word}</h5>
                    <p class="card-text">${word.definition}</p>
                    <p class="card-text"><small class="text-muted">Example: ${word.example}</small></p>
                    <p class="card-text"><small class="text-muted">Topic: ${word.topic}</small></p>
                    <div class="btn-group">
                        <button type="button" class="btn btn-sm btn-outline-primary edit-word" data-word-id="${word.id}">
                            Edit
                        </button>
                        <button type="button" class="btn btn-sm btn-outline-danger delete-word" data-word-id="${word.id}">
                            Delete
                        </button>
                        <button type="button" class="btn btn-sm btn-outline-success mark-learned ${word.is_learned ? 'active' : ''}" data-word-id="${word.id}">
                            ${word.is_learned ? 'Learned' : 'Mark as Learned'}
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `;
}

// Initialize the vocabulary page
export async function initVocabularyPage() {
    try {
        // Load topics
        const topics = await getTopics();
        const topicsList = document.getElementById('topicsList');
        const topicSelect = document.getElementById('topic');
        const editTopicSelect = document.getElementById('editTopic');
        
        // Populate topics list
        topics.forEach(topic => {
            // Add to sidebar
            const li = document.createElement('li');
            li.className = 'nav-item';
            li.innerHTML = `
                <a class="nav-link" href="#" data-topic-id="${topic.id}">
                    ${topic.name}
                </a>
            `;
            topicsList.appendChild(li);
            
            // Add to select options
            const option = document.createElement('option');
            option.value = topic.id;
            option.textContent = topic.name;
            topicSelect.appendChild(option);
            editTopicSelect.appendChild(option.cloneNode(true));
        });
        
        // Load words
        const words = await getWords();
        const wordGrid = document.getElementById('wordGrid');
        wordGrid.innerHTML = '';
        words.forEach(word => {
            wordGrid.appendChild(createWordCard(word));
        });
        
        // Add event listeners
        addEventListeners();
    } catch (error) {
        console.error('Error initializing vocabulary page:', error);
        alert('Error loading vocabulary data');
    }
}

// Add event listeners
function addEventListeners() {
    // Add word form
    const addWordForm = document.getElementById('addWordForm');
    if (addWordForm) {
        addWordForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(addWordForm);
            const wordData = {
                word: formData.get('word'),
                definition: formData.get('definition'),
                example: formData.get('example') || '',
                topic: formData.get('topic') || null
            };

            try {
                console.log('Sending word data:', wordData); // Debug log
                const response = await fetch('/vocabulary/add-word/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCookie('csrftoken')
                    },
                    body: JSON.stringify(wordData)
                });

                console.log('Response status:', response.status); // Debug log
                const responseText = await response.text(); // Get raw response text
                console.log('Response text:', responseText); // Debug log

                if (!response.ok) {
                    throw new Error(`Failed to add word: ${responseText}`);
                }

                let newWord;
                try {
                    newWord = JSON.parse(responseText); // Try to parse as JSON
                } catch (e) {
                    console.error('Error parsing response:', e);
                    throw new Error('Invalid response format');
                }

                const wordGrid = document.getElementById('wordGrid');
                wordGrid.insertAdjacentHTML('afterbegin', createWordCard(newWord));
                
                // Close modal and reset form
                const modal = bootstrap.Modal.getInstance(document.getElementById('addWordModal'));
                if (modal) {
                    modal.hide();
                }
                addWordForm.reset();
            } catch (error) {
                console.error('Error adding word:', error);
                alert(`Error adding word: ${error.message}`);
            }
        });
    }

    // Edit word form
    const editWordForm = document.getElementById('editWordForm');
    if (editWordForm) {
        editWordForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(editWordForm);
            const wordId = formData.get('word_id');
            const wordData = {
                word: formData.get('word'),
                definition: formData.get('definition'),
                example: formData.get('example') || '',
                topic: formData.get('topic') || null
            };

            try {
                console.log('Sending update data:', wordData); // Debug log
                const response = await fetch(`/vocabulary/edit-word/${wordId}/`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCookie('csrftoken')
                    },
                    body: JSON.stringify(wordData)
                });

                console.log('Response status:', response.status); // Debug log
                const responseText = await response.text(); // Get raw response text
                console.log('Response text:', responseText); // Debug log

                if (!response.ok) {
                    throw new Error(`Failed to update word: ${responseText}`);
                }

                let updatedWord;
                try {
                    updatedWord = JSON.parse(responseText); // Try to parse as JSON
                } catch (e) {
                    console.error('Error parsing response:', e);
                    throw new Error('Invalid response format');
                }

                const wordCard = document.querySelector(`[data-word-id="${wordId}"]`).closest('.col-md-4');
                wordCard.outerHTML = createWordCard(updatedWord);
                
                // Close modal
                const modal = bootstrap.Modal.getInstance(document.getElementById('editWordModal'));
                if (modal) {
                    modal.hide();
                }
            } catch (error) {
                console.error('Error updating word:', error);
                alert(`Error updating word: ${error.message}`);
            }
        });
    }

    // Delete word buttons
    document.querySelectorAll('.delete-word').forEach(button => {
        button.addEventListener('click', async () => {
            if (confirm('Are you sure you want to delete this word?')) {
                const wordId = button.dataset.wordId;
                try {
                    console.log('Deleting word:', wordId); // Debug log
                    const response = await fetch(`/vocabulary/delete-word/${wordId}/`, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': getCookie('csrftoken')
                        }
                    });

                    console.log('Response status:', response.status); // Debug log
                    const responseText = await response.text(); // Get raw response text
                    console.log('Response text:', responseText); // Debug log

                    if (!response.ok) {
                        throw new Error(`Failed to delete word: ${responseText}`);
                    }

                    button.closest('.col-md-4').remove();
                } catch (error) {
                    console.error('Error deleting word:', error);
                    alert(`Error deleting word: ${error.message}`);
                }
            }
        });
    });

    // Mark word as learned buttons
    document.querySelectorAll('.mark-learned').forEach(button => {
        button.addEventListener('click', async () => {
            const wordId = button.dataset.wordId;
            try {
                console.log('Marking word as learned:', wordId); // Debug log
                const response = await fetch(`/vocabulary/mark-word-learned/${wordId}/`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCookie('csrftoken')
                    }
                });

                console.log('Response status:', response.status); // Debug log
                const responseText = await response.text(); // Get raw response text
                console.log('Response text:', responseText); // Debug log

                if (!response.ok) {
                    throw new Error(`Failed to update word status: ${responseText}`);
                }

                let data;
                try {
                    data = JSON.parse(responseText); // Try to parse as JSON
                } catch (e) {
                    console.error('Error parsing response:', e);
                    throw new Error('Invalid response format');
                }

                const wordCard = button.closest('.col-md-4');
                if (data.is_learned) {
                    wordCard.classList.add('learned');
                    button.textContent = 'Learned';
                } else {
                    wordCard.classList.remove('learned');
                    button.textContent = 'Mark as Learned';
                }
            } catch (error) {
                console.error('Error updating word status:', error);
                alert(`Error marking word as learned: ${error.message}`);
            }
        });
    });
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', initVocabularyPage); 