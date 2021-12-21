$(function() {
    window.setInterval(function(){
        loadNotifications()
    }, 10000)

    function loadNotifications() {
        $.ajax({
            url: "/notifications",
            type: "POST",
            dataType: "json",
            success:function(data) {
                $(notification).replaceWith(data)
            }
        });
    }
});