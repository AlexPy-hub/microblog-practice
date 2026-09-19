document.addEventListener("DOMContentLoaded", () => {

    document.querySelectorAll(".like-form").forEach((form) => {

        form.addEventListener("submit", async (event) => {

            event.preventDefault();

            const button = form.querySelector(".like-button");

            if (!button) {
                return;
            }

            try {

                const response = await fetch(
                    form.action,
                    {
                        method: "POST",
                        headers: {
                            "X-Requested-With": "XMLHttpRequest"
                        }
                    }
                );

                if (!response.ok) {
                    return;
                }

                const data = await response.json();

                const count = button.querySelector("span");

                if (count) {
                    count.textContent = data.likes_count;
                }

                if (data.liked) {
                    button.classList.add("liked");
                    button.firstChild.textContent = "❤️";
                } else {
                    button.classList.remove("liked");
                    button.firstChild.textContent = "♡";
                }

            } catch (error) {
                console.error(
                    "Ошибка при установке лайка:",
                    error
                );
            }

        });

    });

});