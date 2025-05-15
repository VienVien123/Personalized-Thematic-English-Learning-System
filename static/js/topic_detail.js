document.addEventListener('DOMContentLoaded', function() {
    const topicSlug = document.getElementById('topic-data').dataset.slug;
    const sectionsContainer = document.getElementById('sections-container');
    const topicName = document.getElementById('topic-name');

    fetch(`/api/topics/listen/${topicSlug}/`)
        .then(response => response.json())
        .then(data => {
            topicName.textContent = data.topic.name;  // Hiển thị tên topic

            data.sections.forEach(section => {
                const sectionElement = document.createElement('div');
                sectionElement.classList.add('card', 'mb-3', 'shadow-sm');
                sectionElement.setAttribute('data-toggle', 'collapse');
                sectionElement.setAttribute('aria-expanded', 'false');
                sectionElement.setAttribute('aria-controls', `collapse${section.id}`);

                // Section Header
                const sectionHeader = document.createElement('div');
                sectionHeader.classList.add('card-header');
                sectionHeader.setAttribute('id', `heading${section.id}`);

                const sectionTitle = document.createElement('h5');
                sectionTitle.classList.add('mb-0');
                const sectionButton = document.createElement('button');
                sectionButton.classList.add('btn', 'btn-link');
                sectionButton.setAttribute('aria-expanded', 'false');
                sectionButton.setAttribute('aria-controls', `collapse${section.id}`);
                sectionButton.textContent = `${section.title} (${section.subtopics.length} lessons)`;
                sectionTitle.appendChild(sectionButton);
                sectionHeader.appendChild(sectionTitle);

                // Tạo phần nội dung (subtopics) bị ẩn
                const sectionCollapse = document.createElement('div');
                sectionCollapse.id = `collapse${section.id}`;
                sectionCollapse.classList.add('collapse');
                sectionCollapse.setAttribute('aria-labelledby', `heading${section.id}`);

                const sectionBody = document.createElement('div');
                sectionBody.classList.add('card-body');

                // Subtopics List - Sử dụng Grid system của Bootstrap để chia 3 cột
                const subtopicsRow = document.createElement('div');
                subtopicsRow.classList.add('row');
                section.subtopics.forEach((subtopic, index) => {
                    const subtopicCol = document.createElement('div');
                    subtopicCol.classList.add('col-md-4', 'mb-3');

                    const subtopicCard = document.createElement('div');
                    subtopicCard.classList.add('card', 'h-100');
                    subtopicCard.innerHTML = `
                        <div class="card-body">
                            <h5 class="card-title">
                                <a href="/topics/listen/${topicSlug}/subtopics/${subtopic.slug}/listen-and-type/" class="text-decoration-none text-blue">
                                    ${subtopic.title}
                                </a>
                            </h5>
                            <p class="card-text">${subtopic.num_part} parts · Vocab level: ${subtopic.level}</p>
                        </div>
                    `;

                    subtopicCol.appendChild(subtopicCard);
                    subtopicsRow.appendChild(subtopicCol);
                });

                sectionBody.appendChild(subtopicsRow);
                sectionCollapse.appendChild(sectionBody);
                sectionElement.appendChild(sectionHeader);
                sectionElement.appendChild(sectionCollapse);

                // Thêm section vào container
                sectionsContainer.appendChild(sectionElement);

                // Thêm sự kiện để mở/đóng phần subtopics khi click vào card
                sectionElement.addEventListener('click', function() {
                    const collapseContent = sectionElement.querySelector(`#collapse${section.id}`);
                    if (collapseContent.classList.contains('collapse')) {
                        collapseContent.classList.remove('collapse');
                    } else {
                        collapseContent.classList.add('collapse');
                    }
                });
            });
        })
    .catch(error => console.error('Error fetching topic data:', error));
});