function fetchData() {
    // Show the loading message
    document.getElementById('loading-message').style.display = 'block';

    const country = document.getElementById('country').value;
    const minFollowers = document.getElementById('min-followers').value;
    const maxFollowers = document.getElementById('max-followers').value;
    const tags = document.getElementById('tags').value;

    const data = {
        country: country,
        min_followers: parseInt(minFollowers),
        max_followers: parseInt(maxFollowers),
        tags: tags
    };

    fetch('/fetch_data', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        // Hide the loading message
        document.getElementById('loading-message').style.display = 'none';

        if (data.message && data.message.includes("successfully")) {
            openDataWindow();  // Open the new window/tab to display the data
        }
    });
}

// This function will open a new window/tab to display the retrieved data
function openDataWindow() {
    window.open('/display_data', '_blank');
}

function login() {
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;

    const data = {
        username: username,
        password: password
    };

    fetch('/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        if (data.message && data.message.includes("successful")) {
            window.location.href = '/';  // Redirect to the main page
        } else {
            alert(data.error);
        }
    });
}

function register() {
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    const email = document.getElementById('email').value;

    const data = {
        username: username,
        password: password,
        email: email
    };

    fetch('/register', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        if (data.message && data.message.includes("successful")) {
            window.location.href = 'login.html';  // Redirect to the login page
        } else {
            alert(data.error);
        }
    });
}
