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
