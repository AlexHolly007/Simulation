var count = 0;
var chat_history = [];
var story_state = {}
var picture_style;
var last_image_base64 = null;


//Setting up some global variables that will be changed throughout the course of a playthrough

document.addEventListener('DOMContentLoaded', function () {
    const user_prompt = document.getElementById('user-prompt');
    const responseContainer = document.getElementById('response-container');
    const errorspot = document.getElementById('error-spot');

    //
    // getPictureStyle utilized the microservice by making an api http request
    // A single string is returned that contains the picture style to be used in the image generation.
    async function getPictureStyle() {
        const payload = {
            probs: {
                'japanese anime': 0.6,
                'realistic': 0.1,
                'cartoon': 0.1,
                'comic': 0.2
            }
        };
        // fetch microservice
        try {
            const response = await fetch('http://localhost:12121/random_num', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            if (!response.ok) {
                const text = await response.text(); //get server error message
                throw new Error(`HTTP ${response.status}: ${text}`);
            }

            const data = await response.json();
            picture_style = data.result;
        } catch (error) {
            console.error("Error fetching picture style:", error)
            errorspot.innerHTML = `<p style="color:red;">Error: ${error.message}</p>`;
        }
    }
    getPictureStyle();//This is called during startup to get the first picture style


    //
    // This is the main function that will take the user input and route it to the api, so a generative response
    // can be made and returned into the html.
    const chatgpt_button = document.getElementById('chatgpt-button');
    chatgpt_button.addEventListener('click', async function (event) 
    {
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

        try {
            const response = await fetch('/generate_response', {
                method: 'POST',
                body: JSON.stringify({
                    'user_input': userPrompt.value, 
                    'chat_history': chat_history,
                    'story_state': story_state,
                    // The Chat_history is saved so open ai can create a response based on the history of the story
                    // Insted of only being able to look at the last response. 'chat_history' is a global variable. 
                }),
                headers: {'Content-Type': 'application/json',},
            })

            if (!response.ok) {
                const text = await response.text(); //get server error message
                throw new Error(`HTTP ${response.status}: ${text}`);
            }

            const data = await response.json()

            //save the response to the textbox object
            responseContainer.innerHTML = `<p>${data.response}</p><div id="load" class=""></div>`;

            //save the chat history (just like of responses). And the story state, which is small json of context
            chat_history = data.chat_history;
            story_state = data.story_state

    
            // Send the LAST IMAGE TO BUILD OFF, the history (we will use last 2 events), AND the story state to make image
            // await get_picture(chat_history, story_state, picture_style, last_image_base64);

            //reset user prompt
            userPrompt.value = '';
            userPrompt.placeholder = 'Enter a continuation of the story...';

        } catch (error){
            console.error("Error generating response:", error)
            errorspot.innerHTML = `<p style="color:red;">Error: ${error.message}</p>`;
        }
    })


    async function get_picture(chat_hist, story, picture_style, last_image_base64) {
        try{
            const response = await fetch('/get_picture', {
                method: 'POST',
                body: JSON.stringify({
                    'chat_history': chat_hist,
                    'story_state': story,
                    'style': picture_style,
                    'last_image': last_image_base64,
                }),
                headers: {
                    'Content-Type': 'application/json',
                },
            });

            if (!response.ok) {
                const text = await response.text(); //get server error message
                throw new Error(`HTTP ${response.status}: ${text}`);
            }

            //save image for next time
            last_image_base64 = data.image;

            // Display image
            const img = new Image();
            img.src = 'data:image/png;base64,' + data.image;
            const container = document.getElementById('imageContainer');
            container.innerHTML = '';
            container.appendChild(img);

            return data;
        } catch (error) {
            console.error("Error fetching image:", error)
            errorspot.innerHTML = `<p style="color:red;">Error: ${error.message}</p>`;
        }
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

        chat_history = [];
        count = 0;
        last_image_base64 = null;
        story_state = {};
        getPictureStyle();
    })


});
