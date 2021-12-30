const page_title = document.title;

function loadNotifications() {
    fetch('/notifications')
        .then((response) => {
            return response.json();
        })
        .then((data) => {
            let bell_activeContainer = document.getElementById('bell_active');
            let notificationContainer = document.getElementById('notification');
            //let notifications_listContainer = document.getElementById('notifications_list')
            if (parseInt(data) === 0) {
                document.title = page_title;
                $('#notification').remove();
                bell_activeContainer.innerHTML = "<button class=\"bell_no_active_appearance\" onclick=\"showDiv()\"></button>";
            }

            else {
                $('.frame').append($('<div id="notification"></div>'));
                notificationContainer.innerHTML = data;
                bell_activeContainer.innerHTML = "<button class=\"bell_active_appearance\" onclick=\"showDiv()\"></button>";
                document.title = page_title + ' (' + data + ')';
            }
        });
}

loadNotifications();
setInterval(loadNotifications, 5000);























