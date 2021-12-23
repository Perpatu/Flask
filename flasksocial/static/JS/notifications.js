const page_title = document.title;

function loadNotifications() {
    fetch('/notifications')
        .then((response) => {
            return response.json();
        })
        .then((result) => {
            let resultContainer = document.getElementById("notification");
            if (result === 0) {
                document.title = page_title;
            }
            else {
                document.title = page_title + ' (' + result + ')';
            }
            resultContainer.innerHTML = JSON.stringify(result);
        });
}
loadNotifications();
setInterval(loadNotifications, 1000);

























