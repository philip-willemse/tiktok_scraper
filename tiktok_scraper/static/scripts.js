// scripts.js

// Function to fetch data when the "Collect New Data" form is submitted
function collectNewData() {
    // Show the loading message
    document.getElementById('loading-message').style.display = 'block';

    // Get data from the form in the "Collect New Data" tab
    const country = document.getElementById('country').value;
    const minFollowers = document.getElementById('min-followers').value;
    const maxFollowers = document.getElementById('max-followers').value;
    const tags = document.getElementById('tags').value;

    // Create an object with the form data
    const data = {
        country: country,
        min_followers: parseInt(minFollowers),
        max_followers: parseInt(maxFollowers),
        tags: tags
    };

     const csrfToken = document.querySelector('input[name="csrf_token"]').value;
     console.log("CSRF Token:", csrfToken);
    // Perform the data collection
    fetch('/scrape_data', {
    method: 'POST',
    body: JSON.stringify(data),
    headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': document.querySelector('input[name="csrf_token"]').value
    }
})
    .then(response => response.json())
    .then(data => {
        // Hide the loading message
        document.getElementById('loading-message').style.display = 'none';

        if (data.message && data.message.includes("successfully")) {
            // You can handle the success message here
            alert("Data collection successful!");

            // Reload the "Collected Data" tab to display the updated data
            openCollectedData();
        } else {
            // Handle errors here
            alert(data.error);
        }
    });
}

// Function to open a new window/tab to display collected data
function openCollectedData() {
    window.open('/display_data', '_blank');
}

// Function to handle user login
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
            // Redirect to the dashboard after successful login
            window.location.href = '/';
        } else {
            alert(data.error);
        }
    });
}

// Function to handle user registration
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
            // Display the registration success message
            const registrationSuccessElement = document.getElementById("registration-success");
            registrationSuccessElement.textContent = "Registration successful! Please check your email for a verification link.";

            // Redirect to the login page after a short delay
            setTimeout(() => {
                window.location.href = 'login.html';
            }, 3000); // Redirect after 3 seconds
        } else {
            alert(data.error);
        }
    });
}

// Function to update the table with collected data
function updateCollectedData(data) {
    const tableBody = document.querySelector('#collected-data-table-body');
    tableBody.innerHTML = ''; // Clear existing data

    data.forEach(user => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${user.follower_count}</td>
            <td>${user.nickname}</td>
            <td>${user.signature}</td>
            <td>${user.uid}</td>
            <td>${user.unique_id}</td>
        `;
        tableBody.appendChild(row);
    });
}

// Fetch and update collected data when the page loads
fetch("/get_collected_data")
    .then(response => response.json())
    .then(data => {
        updateCollectedData(data);
    })
    .catch(error => {
        console.error("Error fetching data:", error);
    });

// Function to open the tab content
function openTab(tabName) {
    // Hide all tab content
    const tabContents = document.querySelectorAll('.tab-content');
    tabContents.forEach(tab => {
        tab.style.display = 'none';
    });

    // Show the clicked tab content
    document.getElementById(tabName).style.display = 'block';

    // If the clicked tab is 'collect-new-data', show the form
    if (tabName === 'collect-new-data') {
        document.getElementById('collect-data-form').style.display = 'block';
    }
}





