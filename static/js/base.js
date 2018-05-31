$(document).ready(function () {

$("#btn-browse-sheet").click(function (e) {
    e.preventDefault();
    $("#id_file_campaign").click();
});

$(".clickable-rows > tr").click(function(){
    window.location.replace($(this).data("href"));
});
});
