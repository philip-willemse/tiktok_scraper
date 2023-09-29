document.getElementById('tagForm').addEventListener('submit', function(e) {
  e.preventDefault();
  const tag = document.getElementById('tag').value;

  fetch(`/fetch_tag?tag=${tag}`, {
    method: 'GET'
  })
  .then(response => response.json())
  .then(data => {
    document.getElementById('tagData').innerHTML = JSON.stringify(data, null, 2);
  });
});
