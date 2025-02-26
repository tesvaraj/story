document.addEventListener('DOMContentLoaded', () => {
    const promptInput = document.getElementById('prompt-input');
    const generateBtn = document.getElementById('generate-btn');
    const loadingElement = document.getElementById('loading');
    const resultElement = document.getElementById('result');
    const generatedImage = document.getElementById('generated-image');
    const downloadBtn = document.getElementById('download-btn');

    generateBtn.addEventListener('click', async () => {
        const prompt = promptInput.value.trim();
        
        if (!prompt) {
            alert('Please enter a description for your image.');
            return;
        }
        
        // Show loading state
        loadingElement.classList.remove('hidden');
        resultElement.classList.add('hidden');
        
        try {
            // Call the API to generate the image
            const response = await generateImage(prompt);
            
            // Display the generated image
            generatedImage.src = response.imageUrl;
            
            // Hide loading and show result
            loadingElement.classList.add('hidden');
            resultElement.classList.remove('hidden');
        } catch (error) {
            console.error('Error generating image:', error);
            alert('An error occurred while generating your image. Please try again.');
            loadingElement.classList.add('hidden');
        }
    });

    downloadBtn.addEventListener('click', () => {
        if (generatedImage.src) {
            const a = document.createElement('a');
            a.href = generatedImage.src;
            a.download = 'generated-image.png';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
        }
    });

    // Function to call the Ablo image model API
    async function generateImage(prompt) {
        // Replace this with your actual API endpoint
        const apiUrl = '/api/generate-image';
        
        const response = await fetch(apiUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ prompt }),
        });
        
        if (!response.ok) {
            throw new Error('Failed to generate image');
        }
        
        return await response.json();
    }
}); 