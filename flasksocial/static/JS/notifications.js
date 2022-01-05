const page_title = document.title;

function loadNotifications() {
    fetch('/notifications')
        .then((response) => {
            return response.json();
        })
        .then((data) => {
            let bell_activeContainer = document.getElementById('bell_active');
            let notificationContainer = document.getElementById('notification');
            if (parseInt(data) === 0) {
                document.title = page_title;
                $('#notification').remove();
                bell_activeContainer.innerHTML = "<button class=\"bell_no_active_appearance\" onclick=\"showDiv()\"></button>";
            }

            else if (parseInt(data) > 0) {
                $('.frame').append($('<div id="notification"></div>'));
                notificationContainer.innerHTML = data;
                bell_activeContainer.innerHTML = "<button class=\"bell_active_appearance\" onclick=\"showDiv()\"></button>";
                document.title = page_title + ' (' + data + ')';
            }

            else if (parseInt(data) > 9){
                $('.frame').append($('<div id="notification"></div>'));
                notificationContainer.innerHTML = "9+";
                bell_activeContainer.innerHTML = "<button class=\"bell_active_appearance\" onclick=\"showDiv()\"></button>";
                document.title = page_title + ' (' + data + ')';
            }
        });
}

function load_invite_notifications(){
    $.ajax({
        url:"/accept_invite",
        method:"POST",
        success:function(data){
            $('#notifications_list').html(data);
            $("#notifications_list").append(data.htmlresponse);
        }
    });
}

load_invite_notifications();
setInterval(load_invite_notifications,5000);

loadNotifications();
setInterval(loadNotifications, 5000);