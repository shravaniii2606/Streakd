document.addEventListener("DOMContentLoaded", () => {
    const modal = document.getElementById("taskModal");
    const addBtn = document.querySelector(".add-task-btn");

    if (!addBtn) {
        console.error("Add Task button not found");
        return;
    }

    // Open modal
    addBtn.addEventListener("click", () => {
        modal.classList.add("active");
    });

    // Close modal
    window.closeModal = function () {
        modal.classList.remove("active");
    };

    // Close modal when clicking outside
    window.addEventListener("click", (e) => {
        if (e.target === modal) {
            modal.classList.remove("active");
        }
    });
});
document.addEventListener("DOMContentLoaded", () => {
    const fills = document.querySelectorAll(".progress-fill");
    fills.forEach(fill => {
        const width = fill.dataset.width; // get value from data-width
        fill.style.width = width + "%";
    });
});
document.addEventListener("DOMContentLoaded", () => {
    const xpFill = document.getElementById("xpFill");
    if (!xpFill) return;

    const currentXP = parseInt(xpFill.dataset.current);
    const nextXP = parseInt(xpFill.dataset.next);

    const percentage = Math.min((currentXP / nextXP) * 100, 100);

    setTimeout(() => {
        xpFill.style.width = percentage + "%";
    }, 300);
});

