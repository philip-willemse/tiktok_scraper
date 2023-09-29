async function fetchTagData() {
    const tag = document.getElementById('tagInput').value;
    const response = await fetch(`/fetch_tag?tag=${tag}`);
    const data = await response.json();

    const tableBody = document.getElementById('tagDataTableBody');
    tableBody.innerHTML = "";  // Clear existing data

    const tagDataArray = data["Tag Data from TikAPI"];
    for (const item of tagDataArray) {
        const row = document.createElement('tr');
        const nicknameCell = document.createElement('td');
        const followerCountCell = document.createElement('td');
        const signatureCell = document.createElement('td');

        nicknameCell.textContent = item.nickname;
        followerCountCell.textContent = item.follower_count;
        signatureCell.textContent = item.signature;

        row.appendChild(nicknameCell);
        row.appendChild(followerCountCell);
        row.appendChild(signatureCell);
        tableBody.appendChild(row);
    }
}
