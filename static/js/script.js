async function handleTool(action) {
    const loader = document.getElementById('loader');
    let endpoint, body;

    if (action === 'tts') {
        const text = document.getElementById('tts-input').value;
        if (!text) return alert("Text required!");
        endpoint = '/tts';
        body = { text: text };
    } else if (action === 'mp3' || action === 'video') {
        const url = document.getElementById('dl-url').value;
        if (!url) return alert("URL required!");
        endpoint = '/download-video';
        body = { url: url, type: action };
    } else if (action === 'ai') {
        const prompt = document.getElementById('ai-prompt').value;
        if (!prompt) return alert("Prompt required!");
        endpoint = '/create-ai-video';
        body = { prompt: prompt };
    }

    loader.style.display = "block";

    try {
        const res = await fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body)
        });
        const data = await res.json();
        loader.style.display = "none";

        if (data.file_url) {
            openModal(data.file_url, data.type || (action === 'ai' ? 'video' : 'audio'));
        } else {
            alert("Error: " + data.error);
        }
    } catch (e) {
        loader.style.display = "none";
        alert("Server Error!");
    }
}

function openModal(url, type) {
    const modal = document.getElementById('res-modal');
    const preview = document.getElementById('preview-area');
    const downBtn = document.getElementById('down-btn');

    downBtn.href = url;
    if (type === 'video') {
        preview.innerHTML = `<video controls style="width:100%"><source src="${url}" type="video/mp4"></video>`;
    } else {
        preview.innerHTML = `<audio controls style="width:100%; margin-top:20px;"><source src="${url}" type="audio/mpeg"></audio>`;
    }
    modal.style.display = "flex";
}

function closeModal() {
    document.getElementById('res-modal').style.display = "none";
}
