const page_title = document.title;

function loadNoumberNotifications() {
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
                bell_activeContainer.innerHTML = "<button class=\"bell_no_active_appearance\" onclick=\"showDivList()\"></button>";
            }

            else if (parseInt(data) > 0) {
                $('.frame').append($('<div id="notification"></div>'));
                notificationContainer.innerHTML = data;
                bell_activeContainer.innerHTML = "<button class=\"bell_active_appearance\" onclick=\"showDivList()\"></button>";
                document.title = page_title + ' (' + data + ')';
            }

            else if (parseInt(data) > 9){
                $('.frame').append($('<div id="notification"></div>'));
                notificationContainer.innerHTML = "9+";
                bell_activeContainer.innerHTML = "<button class=\"bell_active_appearance\" onclick=\"showDivList()\"></button>";
                document.title = page_title + ' (' + data + ')';
            }
        });
}

function loadInviteNotifications(){
    $.ajax({
        url:"/accept_invite",
        method:"POST",
        success:function(data){
            $('#notifications_list').html(data);
            $("#notifications_list").append(data.htmlresponse);
        }
    });
}

loadInviteNotifications();
setInterval(loadInviteNotifications,5000);

loadNoumberNotifications();
setInterval(loadNoumberNotifications, 5000);