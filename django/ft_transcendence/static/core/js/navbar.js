function openNav() {
	document.getElementById("SidenavID").style.width = "250px";
}

function closeNav() {
	document.getElementById("SidenavID").style.width = "0";
}

function hideMenu() {
    var burgerMenu = document.getElementById('burger-menu');
    burgerMenu.classList.add('hidden');
}

function openMenu() {
    setTimeout(function() {
        var burgerMenu = document.getElementById('burger-menu');
        burgerMenu.classList.remove('hidden');
    }, 300); // Delay in milliseconds (2000ms = 2 seconds)
}
