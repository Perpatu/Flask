document.addEventListener('mouseup', function(e) {
    let container = document.getElementById('notifications_list');
    if (!container.contains(e.target)) {
        container.style.display = 'none';
    }
});

function showDiv() {
   document.getElementById('notifications_list').style.display = "block";}
