document.addEventListener('DOMContentLoaded', function() {
    const uploadForm = document.getElementById('uploadForm');
    const fileInput = document.getElementById('fileInput');
    const dropArea = document.getElementById('dropArea');
    const resultDiv = document.getElementById('result');
    const progressBar = document.querySelector('.progress-bar');
    const progress = document.querySelector('.progress');
    const uploadIcon = document.getElementById('uploadIcon');
    const uploadText = document.getElementById('uploadText');
    const fileName = document.getElementById('fileName');
    const uploadSuccess = document.getElementById('uploadSuccess');

    // Drag and drop functionality
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropArea.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    ['dragenter', 'dragover'].forEach(eventName => {
        dropArea.addEventListener(eventName, highlight, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropArea.addEventListener(eventName, unhighlight, false);
    });

    function highlight() {
        dropArea.classList.add('bg-light');
    }

    function unhighlight() {
        dropArea.classList.remove('bg-light');
    }

    dropArea.addEventListener('drop', handleDrop, false);

    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        fileInput.files = files;
    }

    dropArea.addEventListener('click', () => fileInput.click());

    function resetUploadArea() {
        dropArea.style.opacity = '0';
        setTimeout(() => {
            uploadIcon.style.display = 'inline-block';
            uploadText.style.display = 'block';
            fileName.textContent = '';
            uploadSuccess.style.display = 'none';
            dropArea.style.opacity = '1';
        }, 500);
    }

    function handleFileSelect(file) {
        if (file) {
            fileName.textContent = file.name;
            uploadIcon.classList.add('upload-animation');
            uploadText.style.display = 'none';
            
            setTimeout(() => {
                uploadIcon.classList.remove('upload-animation');
                uploadIcon.style.display = 'none';
                uploadSuccess.style.display = 'inline-block';
            }, 1000);
        }
    }

    fileInput.addEventListener('change', (e) => {
        handleFileSelect(e.target.files[0]);
    });

    dropArea.addEventListener('drop', (e) => {
        handleDrop(e);
        handleFileSelect(fileInput.files[0]);
    });

    uploadForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const file = fileInput.files[0];
        
        if (!file) {
            alert('Por favor, selecione um arquivo.');
            return;
        }
        
        const formData = new FormData();
        formData.append('file', file);
        
        try {
            resultDiv.style.display = 'none';
            progress.style.display = 'flex';
            progressBar.style.width = '0%';
            
            const response = await fetch('/upload', {
                method: 'POST',
                body: formData
            });

            const reader = response.body.getReader();
            const decoder = new TextDecoder();

            let buffer = '';
            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                buffer += decoder.decode(value, { stream: true });
                const messages = buffer.split('\n---\n');
                buffer = messages.pop();

                for (const message of messages) {
                    if (message.trim() !== '') {
                        try {
                            const data = JSON.parse(message);
                            progressBar.style.width = `${data.progress}%`;
                            progressBar.textContent = `${data.status} - ${data.progress}%`;

                            if (data.progress === 100) {
                                progress.style.display = 'none';
                                resultDiv.style.display = 'block';
                                resultDiv.innerHTML = `
                                    <h2 class="mb-3">Resultado:</h2>
                                    <p class="alert alert-success">${data.message}</p>
                                    <a href="/download/${data.translated_file}" class="btn btn-primary mb-3">Baixar arquivo traduzido</a>
                                    <h3 class="mt-4">Resumo:</h3>
                                    <p class="bg-light p-3 rounded">${data.summary}</p>
                                `;

                                // Dispara os confetes
                                fireConfetti();

                                // Reset the upload area
                                resetUploadArea();
                            }
                        } catch (error) {
                            console.error('Erro ao analisar JSON:', error, 'Mensagem:', message);
                        }
                    }
                }
            }
        } catch (error) {
            console.error('Erro:', error);
            progress.style.display = 'none';
            resultDiv.style.display = 'block';
            resultDiv.innerHTML = `
                <div class="alert alert-danger">
                    Ocorreu um erro ao processar o arquivo. Por favor, tente novamente.
                </div>
            `;
            resetUploadArea();
        }
    });

    // Função para disparar confetes
    function fireConfetti() {
        const duration = 5 * 1000;
        const animationEnd = Date.now() + duration;
        const defaults = { startVelocity: 30, spread: 360, ticks: 60, zIndex: 0 };

        function randomInRange(min, max) {
            return Math.random() * (max - min) + min;
        }

        const interval = setInterval(function() {
            const timeLeft = animationEnd - Date.now();

            if (timeLeft <= 0) {
                return clearInterval(interval);
            }

            const particleCount = 50 * (timeLeft / duration);
            confetti(Object.assign({}, defaults, { particleCount, origin: { x: randomInRange(0.1, 0.3), y: Math.random() - 0.2 } }));
            confetti(Object.assign({}, defaults, { particleCount, origin: { x: randomInRange(0.7, 0.9), y: Math.random() - 0.2 } }));
        }, 250);
    }
});
