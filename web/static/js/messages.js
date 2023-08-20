function showPopupMessageAtPageLoad() {
    var elMessagesDiv = $('#popup-messages-content');
    var elMessagesUl = $('#popup-messages-content-ul li');
    if (elMessagesUl.length) {
        elMessagesDiv.hide().fadeIn(500).delay(2000).fadeOut(1000);
    }
}
function showPopupMessage(content) {
    var elMessagesDiv = $('#popup-messages-content');
    var elMessagesUl = $('#popup-messages-content-ul');
    if (content) {
        elMessagesUl.html(content);
        elMessagesDiv.hide().fadeIn(500).delay(2000).fadeOut(1000);
    }
}

$( document ).ready(function() {
    showPopupMessageAtPageLoad();
});