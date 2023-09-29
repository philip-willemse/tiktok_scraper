document.getElementById('loginForm').addEventListener('submit', function(e) {
  e.preventDefault();
  const username = document.getElementById('username').value;
  const password = document.getElementById('password').value;

  fetch('/authenticate', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ username, password })
  })
  .then(response => response.json())
  .then(data => {
    console.log("Debug: Server response", data);  // Debug line
    if (data.status === "success") {
  // Redirect to dashboard or do something else
  console.log("Debug: Login successful");
  window.location.href = "/dashboard";  // Redirect to a new page
} else {
  console.log("Debug: Login failed");
}
  });
});
