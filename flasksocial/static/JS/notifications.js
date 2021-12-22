$(function() {
    window.setInterval(function(){
        loadNotifications()
    }, 1000)

    function loadNotifications() {
        $.ajax({
            url: "/notifications",
            type: "POST",
            dataType: "json",
            success:function(data) {
                $('#notification').html(data);
                $("#notification").append(data.htmlresponse);
            }
        });
    }
});

