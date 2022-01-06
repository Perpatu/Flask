document.addEventListener('mouseup', function(e) {
    let container_list = document.getElementById('notifications_list');   
    if (!container_list.contains(e.target)) {
        container_list.style.display = 'none';
    }
});

function showDiv() {
   document.getElementById('notifications_list').style.display = "block";
   
}