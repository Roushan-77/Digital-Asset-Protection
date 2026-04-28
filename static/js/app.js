document.addEventListener("DOMContentLoaded", () => {
    const pageLoader = document.querySelector(".page-loader");

    document.querySelectorAll("[data-flash]").forEach((alert) => {
        window.setTimeout(() => {
            alert.classList.add("is-hiding");
            window.setTimeout(() => alert.remove(), 260);
        }, 4500);
    });

    document.querySelectorAll("[data-loading-form]").forEach((form) => {
        const submitButton = form.querySelector("[data-submit-button]");
        const buttonLabel = form.querySelector("[data-button-label]");
        const loadingText = form.dataset.loadingText || "Loading...";
        const originalText = buttonLabel ? buttonLabel.textContent : submitButton?.textContent;
        let submitted = false;

        form.addEventListener("submit", (event) => {
            if (submitted) {
                event.preventDefault();
                return;
            }

            submitted = true;
            pageLoader?.classList.add("is-active");

            if (submitButton) {
                submitButton.disabled = true;
                submitButton.classList.add("btn-loading");
                submitButton.setAttribute("aria-busy", "true");
            }

            if (buttonLabel) {
                buttonLabel.textContent = loadingText;
            } else if (submitButton) {
                submitButton.textContent = loadingText;
            }

            window.setTimeout(() => {
                if (!form.checkValidity()) {
                    submitted = false;
                    pageLoader?.classList.remove("is-active");
                    if (submitButton) {
                        submitButton.disabled = false;
                        submitButton.classList.remove("btn-loading");
                        submitButton.removeAttribute("aria-busy");
                    }
                    if (buttonLabel) {
                        buttonLabel.textContent = originalText;
                    } else if (submitButton) {
                        submitButton.textContent = originalText;
                    }
                }
            }, 0);
        });
    });

    document.querySelectorAll(".image-input").forEach((input) => {
        const form = input.closest("form");
        const preview = form?.querySelector("[data-image-preview]");
        const previewImage = preview?.querySelector("img");
        const fileName = form?.querySelector("[data-file-name]");

        input.addEventListener("change", () => {
            const file = input.files && input.files[0];
            if (!file || !preview || !previewImage || !fileName) {
                return;
            }

            fileName.textContent = file.name;
            previewImage.src = URL.createObjectURL(file);
            preview.hidden = false;
        });
    });
});
