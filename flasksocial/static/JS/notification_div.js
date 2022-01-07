document.addEventListener('mouseup', function(e) {
    let container_list = document.getElementById('notifications_list');   
    if (!container_list.contains(e.target)) {
        container_list.style.display = 'none';
    }
});

document.addEventListener('mouseup', function(a) {
    let container_list_three_dots = document.getElementById('notifications_list_three_dots');
    if (!container_list_three_dots.contains(a.target)) {
        container_list_three_dots.style.display = 'none';
    }
})

function showDivList() {
   document.getElementById('notifications_list').style.display = "block";   
}

function showDivListDots() {
    document.getElementById('notifications_list_three_dots').style.display = "block";
}