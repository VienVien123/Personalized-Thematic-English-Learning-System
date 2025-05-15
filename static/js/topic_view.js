fetch('/api/topics/listen/')
        .then(response => response.json())
        .then(data => {
            const topicContainer = document.getElementById('topic-container');

            // Sắp xếp các topic theo ID tăng dần
            data.sort((a, b) => a.id - b.id);

            // Duyệt qua các topic và tạo các card
            data.forEach(topic => {
                const topicCard = document.createElement('div');
                topicCard.classList.add('col');  // Bootstrap column class

                // Tạo nội dung cho từng card topic
                topicCard.innerHTML = `
                    <a href="/topics/listen/${topic.slug}" style="text-decoration: none; color: inherit;">
                        <div class="card shadow-sm" style="display: flex; flex-direction: row; align-items: center; height: 160px; transition: transform 0.3s ease;">
                            <!-- Đẩy ảnh sang bên trái -->
                            <img src="/media/${topic.image}" class="card-img-left" alt="${topic.name}" style="object-fit: contain; height: 150px; width: 150px; border-radius: 8px 0 0 8px;">
                            
                            <!-- Nội dung bên cạnh ảnh -->
                            <div class="card-body" style="flex: 1; padding-left: 15px; display: flex; flex-direction: column; justify-content: center;">
                                <h5 class="card-title topic-name" style="font-size: 1rem; font-weight: bold; transition: color 0.3s ease;">${topic.name}</h5>
                                <p style="font-size: 0.875rem; color: #555;"><strong>Levels:</strong> ${topic.levels}</p>
                                <p style="font-size: 0.875rem; color: #555;"><strong>${topic.lessons} lessons</strong></p>
                            </div>
                        </div>
                    </a>
                `;

                // Thêm card vào container
                topicContainer.appendChild(topicCard);
            });
        })
        .catch(error => console.error('Error fetching topics:', error));