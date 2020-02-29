var autohide_mouse = false;
if (!autohide_mouse_duration) {
    var autohide_mouse_duration = 1500;
}
document.body.style.cursor = "none";
window.onmousemove = function(e){
    document.body.style.cursor = "auto";
    if(autohide_mouse === false){
        autohide_mouse = true;
        setTimeout(function(){
            document.body.style.cursor = "none";
            autohide_mouse = false;
        }, autohide_mouse_duration);
    }
}