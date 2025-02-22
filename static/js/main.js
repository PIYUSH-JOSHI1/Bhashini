// static/js/main.js
document.addEventListener('DOMContentLoaded', function() {
    const translateForm = document.querySelector('textarea');
    const translateButton = document.querySelector('button');
    const targetLangSelect = document.querySelector('select');

    if (translateForm && translateButton && targetLangSelect) {
        translateButton.addEventListener('click', async () => {
            const text = translateForm.value;
            const targetLang = targetLangSelect.value;

            if (!text) {
                alert('Please enter text to translate');
                return;
            }

            try {
                const response = await fetch('/translate', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                    },
                    body: `text=${encodeURIComponent(text)}&target_lang=${targetLang}`
                });

                const data = await response.json();

                if (data.status === 'success') {
                    // Create or update translation result
                    let resultDiv = document.getElementById('translation-result');
                    if (!resultDiv) {
                        resultDiv = document.createElement('div');
                        resultDiv.id = 'translation-result';
                        resultDiv.className = 'mt-4 p-4 bg-gray-100 rounded-lg';
                        translateForm.parentNode.appendChild(resultDiv);
                    }
                    resultDiv.textContent = data.translation;
                } else {
                    alert('Translation failed: ' + data.message);
                }
            } catch (error) {
                alert('Error during translation: ' + error.message);
            }
        });
    }
});