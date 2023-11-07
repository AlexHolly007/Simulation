document.addEventListener('DOMContentLoaded', function () {
    const promptForm = document.getElementById('prompt-form');
    const responseContainer = document.getElementById('response-container');
    const chatgpt_button = document.getElementById('chatgpt-button');
    const close_startup = document.getElementById('close-start');
    const info_UI = document.getElementById('UI-info');
    const info_UI_close = document.getElementById('close-UI');
    const restart_btn = document.getElementById('restart');

    promptForm.addEventListener('submit', function (event) {
        event.preventDefault();
        const userPrompt = document.getElementById('user-prompt').value;

        fetch('/process-prompt', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ 'userPrompt': userPrompt }),
        })
            .then(response => response.text())
            .then(data => {
                // Update the response container with the data received from the server
                responseContainer.innerHTML = data;
            })
            .catch(error => {
                console.error('Error:', error);
            });
    })

    chatgpt_button.addEventListener('click', function (event) {
        event.preventDefault();
        const userPrompt = document.getElementById('user-prompt').value;

        fetch('/generate_response', {
            method: 'POST',
            body: new URLSearchParams({'user_input': userPrompt }),
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
        })
        .then(response => response.json())
        .then(data => {
            responseContainer.innerHTML = `<p>${data.response}</p>`;
        });
    })

    close_startup.addEventListener('click', function (event) {
        event.preventDefault();
        const alert_startup = document.getElementById('alert_start');
        alert_startup.className = 'alert hide';
    })

    info_UI.addEventListener('click', function (event) {
        event.preventDefault();
        const UI_info_alert = document.getElementById('UI-info-alert');
        UI_info_alert.className = 'alert';
    })

    info_UI_close.addEventListener('click', function (event) {
        event.preventDefault();
        const UI_info_alert = document.getElementById('UI-info-alert');
        UI_info_alert.className = 'alert hide';
    })

    restart_btn.addEventListener('click', function(event) {
        const userPrompt = document.getElementById('user-prompt');
        userPrompt.value = '';
        responseContainer.innerHTML = '';
    })


});
