var count = 0;
var backstory = [{"role": "system", "content": "You are creating a story\
with the user. You should add something to the story and read it back as \
a continuation of the story, keep responses short, under 60 words"}];
var picture_style;
//Setting up some global variables that will be changed throughout the course of a playthrough

document.addEventListener('DOMContentLoaded', function () {
    const user_prompt = document.getElementById('user-prompt');
    const responseContainer = document.getElementById('response-container');

    //
    // getPictureStyle utilized the microservice by making an api http request
    // A single string is returned that contains the picture style to be used in the image generation.
    function getPictureStyle() {
        fetch('/make_request', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(''),
        })
        .then(response => response.json())
        .then(data => {
            picture_style = data['result'];// Saving the picture style for further use. It is a global variable.
        })
        .catch(error => { //error checking
            responseContainer.innerHTML = error;
            console.error('Error:', error);
        });
    }
    getPictureStyle();//This is called during startup to get the first picture style


    //
    // This is the main function that will take the user input and route it to the api, so a generative response
    // can be made and returned into the html. 
    const chatgpt_button = document.getElementById('chatgpt-button');
    chatgpt_button.addEventListener('click', function (event) {
        event.preventDefault();
        responseContainer.innerHTML = '<div id="load" class="loader"></div>'
        count += 1; //This count and loop is set to remind users they can restart the playthrough. It goes off after three responses
        if (count == 4) {
            const tnkr_msg = document.getElementById('tnkr-timeout');
            tnkr_msg.className = "alert";
        };
        if (count == 7) {
            const end_msg = document.getElementById('end-play');
            end_msg.className = "alert";
            document.getElementById('restart').click();
            return;
        };
        const userPrompt = document.getElementById('user-prompt');

        fetch('/generate_response', {
            method: 'POST',
            body: JSON.stringify({
                'user_input': userPrompt.value, 
                'backstory': backstory,
                // The backstory is saved so open ai can create a response based on the history of the story
                // Insted of only being able to look at the last response. 'backstory' is a global variable. 
            }),
            headers: {
                'Content-Type': 'application/json',
            },
        })
        .then(response => response.json())
        .then(async data => { //The response data is sent to the html responce container.
            await get_picture(data.response, picture_style);
            responseContainer.innerHTML = `<p>${data.response}</p><div id="load" class=""></div>`;
            backstory = data.backstory;
            userPrompt.value = '';
            userPrompt.placeholder = 'Enter a continuation of the story...';
        });
    })


    function get_picture(gpt_response, picture_style) {
        return new Promise((resolve, reject) => {
            fetch('/get_picture', {
                method: 'POST',
                body: JSON.stringify({
                    'image_text': gpt_response,
                    'style': picture_style,
                }),
                headers: {
                    'Content-Type': 'application/json',
                },
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Non-200 response');
                }
                return response.json();
            })
            .then(data => {
                var img = new Image();
                img.src = 'data:image/png;base64,' + data.image;
    
                var container = document.getElementById('imageContainer');
                container.innerHTML = '';
                container.appendChild(img);
                resolve(data);
            })
            .catch(error => {
                reject(error);
            });
        });
    }

    //
    //This is the close button for the alert that pops up after the user has had a playthrough last more than 3 responses.
    const tnkr_close = document.getElementById('tnkr-close-btn');
    tnkr_close.addEventListener('click', function (event) {
        event.preventDefault();
        const tnkr_msg = document.getElementById('tnkr-timeout');
        tnkr_msg.className = 'alert hide';
    })

    //
    //Close button for the alert that pops up when you have had a playthrough go too long
    const endPlay_alert_close = document.getElementById('end-close-btn');
    endPlay_alert_close.addEventListener('click', function (event) {
        event.preventDefault();
        const end_msg = document.getElementById('end-play');
        end_msg.className = 'alert hide';
    })
    //
    //enables 'enter' as a submission as well as the 'generate' button
    user_prompt.addEventListener('keyup', function(event) {
        event.preventDefault();
        if (event.key === 'Enter') {
            document.getElementById('chatgpt-button').click();
    	}
    });

    //
    //Close button for the startup guide alert
    const close_startup = document.getElementById('close-start');
    close_startup.addEventListener('click', function (event) {
        event.preventDefault();
        const alert_startup = document.getElementById('alert_start');
        alert_startup.className = 'alert hide';
    })

    //
    //Functions for the user-input 'info' button, as well as the close botton for the alert that pops up.
    const info_UI = document.getElementById('UI-info');
    const info_UI_close = document.getElementById('close-UI');
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
    
    //
    //Functions for the restart button information symbol to start the alert, and the close btn for the alert
    const info_restart = document.getElementById('restart-info-btn');
    const info_restart_close = document.getElementById('close-restart');
    info_restart.addEventListener('click', function(event) {
        event.preventDefault();
        const restart_info_alert = document.getElementById('restart-info');
        restart_info_alert.className = 'alert';
    })
    info_restart_close.addEventListener('click', function(event) {
        event.preventDefault();
        const restart_info_alert = document.getElementById('restart-info');
        restart_info_alert.className = 'alert hide';
    })

    //
    //Restart button, will reset response history and screen. Enabling new responses
    const restart_btn = document.getElementById('restart');
    restart_btn.addEventListener('click', function(event) {
        const userPrompt = document.getElementById('user-prompt');
        userPrompt.value = '';
        responseContainer.innerHTML = '';
        var container = document.getElementById('imageContainer');
        container.innerHTML = '';
        backstory = [{"role": "system", "content": "You are creating a story\
        with the user. You should add something to the story and read it back as \
        a continuation of the story, keep responses short, under 60 words"}];
        getPictureStyle();
    })


});
