const page_title = document.title;

function loadNotifications() {
    fetch('/notifications')
        .then((response) => {
            return response.json();
        })
        .then((data) => {
            let imageContainer = document.getElementById("bell_active");
            let resultContainer = document.getElementById('notification');
            if (parseInt(data[0]) === 0) {
                document.title = page_title;
                $('#notification').remove();
                imageContainer.innerHTML = "<button class=\"bell_no_active_appearance\"></button>";
            }

            else {
                $('.frame').append($('<div id="notification"></div>'));
                resultContainer.innerHTML = data[0];
                imageContainer.innerHTML = "<button class=\"bell_active_appearance\"></button>";
                document.title = page_title + ' (' + data[0] + ')';
            }
        });
}

loadNotifications();
setInterval(loadNotifications, 5000);























