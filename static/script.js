// document.addEventListener('DOMContentLoaded', () => {
//     const fileInput = document.getElementById('file-input');
//     const uploadedImage = document.getElementById('uploaded-image');
//     const predictButton = document.getElementById('predict-button');
//     const resultsContainer = document.getElementById('results-container');

//     fileInput.addEventListener('change', () => {
//         const file = fileInput.files[0];
//         if (file) {
//             const reader = new FileReader();
//             reader.onload = (e) => {
//                 uploadedImage.src = e.target.result;
//                 uploadedImage.style.display = 'block';
//             };
//             reader.readAsDataURL(file);
//         }
//     });

//     predictButton.addEventListener('click', async () => {
//         const file = fileInput.files[0];
//         if (!file) {
//             alert('Please upload an image first.');
//             return;
//         }

//         resultsContainer.innerHTML = '<div class="spinner"></div>';

//         const formData = new FormData();
//         formData.append('file', file);

//         try {
//             const response = await fetch('/predict', {
//                 method: 'POST',
//                 body: formData
//             });

//             const data = await response.json();

//             if (data.error) {
//                 resultsContainer.innerHTML = `<p style="color: red;">Error: ${data.error}</p>`;
//             } else {
//                 resultsContainer.innerHTML = `
//                     <div class="result">
//                         <h2>Prediction</h2>
//                         <p><strong>Animal:</strong> ${data.prediction} (${data.confidence.toFixed(2)}% confidence)</p>
//                     </div>
//                     <div class="result">
//                         <h2>Did You Know?</h2>
//                         ${data.facts.map(fact => `<p>✅ ${fact}</p>`).join('')}
//                         <a href="${data.wiki_link}" target="_blank">🌐 Read more on Wikipedia</a>
//                     </div>
//                 `;
//             }
//         } catch (error) {
//             resultsContainer.innerHTML = `<p style="color: red;">An error occurred: ${error.message}</p>`;
//         }
//     });
// });
document.addEventListener('DOMContentLoaded', () => {
    const fileInput = document.getElementById('file-input');
    const uploadedImage = document.getElementById('uploaded-image');
    const predictButton = document.getElementById('predict-button');
    const resultsContainer = document.getElementById('results-container');

    fileInput.addEventListener('change', () => {
        const file = fileInput.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = (e) => {
                uploadedImage.src = e.target.result;
                uploadedImage.style.display = 'block';
            };
            reader.readAsDataURL(file);
        }
    });

    predictButton.addEventListener('click', async (e) => {
        e.preventDefault(); // ✅ Stop page reload

        const file = fileInput.files[0];
        if (!file) {
            alert('Please upload an image first.');
            return;
        }

        resultsContainer.innerHTML = '<p>Analyzing image...</p>';

        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch('/predict', {
                method: 'POST',
                body: formData
            });

            console.log("Raw response:", response);

            const data = await response.json();
            console.log("Parsed JSON:", data);

            if (data.error) {
                resultsContainer.innerHTML = `<p style="color: red;">Error: ${data.error}</p>`;
            } else {
                resultsContainer.innerHTML = `
                    <div class="result">
                        <h2>Prediction</h2>
                        <p><strong>Animal:</strong> ${data.prediction} (${data.confidence.toFixed(2)}% confidence)</p>
                    </div>
                    <div class="result">
                        <h2>Did You Know?</h2>
                        ${data.facts && data.facts.length > 0 ? data.facts.map(f => `<p>✅ ${f}</p>`).join('') : "<p>No facts available.</p>"}
                        ${data.wiki_link ? `<a href="${data.wiki_link}" target="_blank">🌐 Read more on Wikipedia</a>` : ""}
                    </div>
                `;
            }
        } catch (error) {
            resultsContainer.innerHTML = `<p style="color: red;">An error occurred: ${error.message}</p>`;
        }
    });
});
