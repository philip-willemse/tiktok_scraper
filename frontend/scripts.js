function fetchData() {
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
    }).then(response => response.json())
    .then(data => {
        if (data.file) {
            document.getElementById('download-link').style.display = 'block';
        }
    });
}
