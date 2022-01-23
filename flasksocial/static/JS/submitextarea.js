/*function showComments() {
    var comment = document.getElementById("comment");
    if (comment.style.display === "none") {
        comment.style.display = "block";
    }
    else {
        comment.style.display = "none";
    }
}*/

$(document).ready(function() {
    $('.commentarea').keydown(function(event) {
        if (event.which == 13) {
            this.form.submit();
            event.preventDefault();
         }
    });
});