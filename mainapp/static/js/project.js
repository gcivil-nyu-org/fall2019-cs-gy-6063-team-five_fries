
/* auto-hide the alert messages after 5 seconds */
$(function() {
    // setTimeout() function will be fired after the page
    // is loaded it will wait for 5 seconds and then
    // will fire
    setTimeout(function() {
        $(".alert").alert('close');
    }, 5000)
})