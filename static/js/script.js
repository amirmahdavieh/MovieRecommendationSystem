document.addEventListener("DOMContentLoaded", function () {
    const buttons = document.querySelectorAll(".toggle-watch");

    buttons.forEach(button => {
        button.addEventListener("click", function () {
            const movieTitle = this.getAttribute("data-title");

            fetch("/toggle_watch", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ title: movieTitle })
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === "success") {
                    this.textContent = this.textContent === "Watched" ? "Not Watched Yet" : "Watched";
                }
            })
            .catch(error => console.error("Error toggling watch status:", error));
        });
    });
});
