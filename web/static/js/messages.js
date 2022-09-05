function showPopupMessage(content) {
    var elMessagesDiv = $('#popup-messages-content');
    var elMessagesUl = $('#popup-messages-content-ul');
    if (elMessagesUl.length && content) {
        elMessagesUl.html(content);
        elMessagesDiv.hide().fadeIn(500).delay(2000).fadeOut(1000);
    }
}