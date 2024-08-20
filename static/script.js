function toggleDarkMode(){
    var redirectUrl = new URL(window.location.href.replace('?toggleDarkMode', ''));
    redirectUrl.searchParams.append('toggleDarkMode', true);
    window.location = redirectUrl;
}
