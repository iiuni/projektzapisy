// Implements folding sidebar contents on small devices.

function toggleSidebarFolded(event) {
    const sidebarInner = document.getElementById("sidebar-inner");
    sidebarInner.classList.toggle("folded");
    event.preventDefault();
}

document.addEventListener("DOMContentLoaded", function() {
    const sidebarFoldButton = document.getElementById("fold-toggler");
    if (!sidebarFoldButton) {
        return;
    }
    sidebarFoldButton.addEventListener("click", toggleSidebarFolded);
});
