// Show a confirmation prompt before deleting a client
document.addEventListener("DOMContentLoaded", () => {
    const deleteLinks = document.querySelectorAll("a[href*='/delete/']");

    deleteLinks.forEach(link => {
        link.addEventListener("click", event => {
            const confirmDelete = confirm("Are you sure you want to delete this item?");
            if (!confirmDelete) {
                event.preventDefault();
            }
        });
    });
});
