const CATEGORY_DETAILS = {
    werking: {
        title: "Hoe werkt AI?",
        paragraphs: [
            "De categorie \"Hoe werkt AI?\" helpt spelers begrijpen wat artifici\u00eble intelligentie precies doet en hoe AI-systemen tot antwoorden of beslissingen komen. De vragen gaan over begrippen zoals data, algoritmes, trainen, patronen herkennen, prompts en betrouwbaarheid.",
            "Zo leren spelers op een eenvoudige manier dat AI niet \"denkt\" zoals een mens, maar voorspellingen maakt op basis van voorbeelden en informatie.",
        ],
    },
    leefwereld: {
        title: "AI in je leefwereld",
        paragraphs: [
            "De categorie \"AI in jouw leefwereld\" laat spelers ontdekken waar artifici\u00eble intelligentie overal opduikt in het dagelijkse leven. De vragen gaan over herkenbare situaties zoals sociale media, zoekmachines, streamingdiensten, slimme apps, games en online shoppen.",
            "Zo leren spelers bewuster kijken naar technologie die ze vaak al gebruiken, zonder altijd te merken dat er AI achter zit.",
        ],
    },
    kritisch: {
        title: "Kritisch, veilig en verantwoord",
        paragraphs: [
            "De categorie \"Kritisch, veilig en verantwoord\" leert spelers nadenken over hoe ze AI op een slimme en bewuste manier kunnen gebruiken. De vragen gaan over privacy, betrouwbare informatie, vooroordelen, auteursrecht, nepbeelden, online veiligheid en het controleren van AI-antwoorden.",
            "Zo ontdekken spelers dat AI handig kan zijn, maar dat je altijd kritisch moet blijven en zelf verantwoordelijk blijft voor wat je ermee doet.",
        ],
    },
    kansen: {
        title: "Voordelen en kansen",
        paragraphs: [
            "De categorie \"Voordelen en kansen\" laat spelers ontdekken hoe artifici\u00eble intelligentie mensen kan helpen en nieuwe mogelijkheden kan cre\u00ebren. De vragen gaan over AI als hulpmiddel bij leren, creativiteit, zorg, werk, communicatie en probleemoplossend denken.",
            "Zo zien spelers dat AI niet alleen risico's heeft, maar ook kansen biedt om slimmer, sneller en inclusiever te werken.",
        ],
    },
    beelden: {
        title: "AI-beelden",
        paragraphs: [
            "De categorie \"AI-beelden\" bestaat uit foto's waarbij spelers moeten inschatten of ze echt zijn of door AI gegenereerd. De spelers leren aandachtig kijken naar details zoals handen, gezichten, licht, tekst, schaduwen en vreemde foutjes in de afbeelding.",
            "Zo oefenen ze om beelden kritischer te beoordelen en ontdekken ze dat AI-beelden soms heel overtuigend kunnen lijken.",
        ],
    },
};

function revealVisibleSections() {
    const revealNodes = document.querySelectorAll("[data-reveal]");

    if (!("IntersectionObserver" in window)) {
        revealNodes.forEach((node) => node.classList.add("is-visible"));
        return;
    }

    const observer = new IntersectionObserver(
        (entries) => {
            entries.forEach((entry) => {
                if (!entry.isIntersecting) {
                    return;
                }

                entry.target.classList.add("is-visible");
                observer.unobserve(entry.target);
            });
        },
        {
            threshold: 0.16,
            rootMargin: "0px 0px -36px 0px",
        }
    );

    revealNodes.forEach((node) => observer.observe(node));
}

function updateBodyModalState() {
    const hasOpenModal = Array.from(document.querySelectorAll(".site-modal")).some((modal) => !modal.hidden);
    document.body.classList.toggle("is-modal-open", hasOpenModal);
}

function closeCategoryModal() {
    const modal = document.getElementById("categoryModal");
    if (!modal) {
        return;
    }

    modal.hidden = true;
    updateBodyModalState();
}

function openCategoryModal(categoryKey) {
    const detail = CATEGORY_DETAILS[categoryKey];
    const modal = document.getElementById("categoryModal");
    const title = document.getElementById("categoryModalTitle");
    const body = document.getElementById("categoryModalBody");

    if (!detail || !modal || !title || !body) {
        return;
    }

    title.textContent = detail.title;
    body.innerHTML = "";

    detail.paragraphs.forEach((paragraphText) => {
        const paragraph = document.createElement("p");
        paragraph.textContent = paragraphText;
        body.appendChild(paragraph);
    });

    modal.hidden = false;
    updateBodyModalState();
}

function closeMaterialsModal() {
    const modal = document.getElementById("materialsModal");
    if (!modal) {
        return;
    }

    modal.hidden = true;
    updateBodyModalState();
}

function openMaterialsModal() {
    const modal = document.getElementById("materialsModal");
    const closeButton = modal?.querySelector("[data-close-materials-modal]");

    if (!modal) {
        return;
    }

    modal.hidden = false;
    updateBodyModalState();

    window.setTimeout(() => {
        closeButton?.focus();
    }, 60);
}

function bindCategoryModal() {
    const triggerButtons = document.querySelectorAll("[data-category-key]");
    const closeButtons = document.querySelectorAll("[data-close-category-modal]");

    triggerButtons.forEach((button) => {
        button.addEventListener("click", () => {
            openCategoryModal(button.getAttribute("data-category-key"));
        });
    });

    closeButtons.forEach((button) => {
        button.addEventListener("click", closeCategoryModal);
    });
}

function setContactFeedback(message, type = "") {
    const feedback = document.getElementById("contactFormFeedback");
    if (!feedback) {
        return;
    }

    feedback.textContent = message || "";
    feedback.classList.remove("is-error", "is-success");

    if (type) {
        feedback.classList.add(type === "error" ? "is-error" : "is-success");
    }
}

function closeContactModal() {
    const modal = document.getElementById("contactModal");
    if (!modal) {
        return;
    }

    modal.hidden = true;
    updateBodyModalState();
}

function openContactModal() {
    const modal = document.getElementById("contactModal");
    const nameField = document.getElementById("contactName");

    if (!modal) {
        return;
    }

    modal.hidden = false;
    updateBodyModalState();
    setContactFeedback("");

    window.setTimeout(() => {
        nameField?.focus();
    }, 60);
}

async function handleContactSubmit(event) {
    event.preventDefault();

    const form = event.currentTarget;
    const submitButton = document.getElementById("contactSubmitButton");
    if (!(form instanceof HTMLFormElement) || !(submitButton instanceof HTMLButtonElement)) {
        return;
    }

    const formData = new FormData(form);
    const payload = {
        name: String(formData.get("name") || ""),
        email: String(formData.get("email") || ""),
        message: String(formData.get("message") || ""),
        company: String(formData.get("company") || ""),
    };

    setContactFeedback("");
    submitButton.disabled = true;
    submitButton.textContent = "Verzenden...";

    try {
        const response = await fetch("/api/contact", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                Accept: "application/json",
            },
            body: JSON.stringify(payload),
        });

        const result = await response.json().catch(() => ({}));

        if (!response.ok) {
            throw new Error(result.detail || "Het bericht kon niet verzonden worden.");
        }

        form.reset();
        setContactFeedback(result.message || "Je bericht is verzonden.", "success");
    } catch (error) {
        const message = error instanceof Error ? error.message : "Het bericht kon niet verzonden worden.";
        setContactFeedback(message, "error");
    } finally {
        submitButton.disabled = false;
        submitButton.textContent = "Verstuur bericht";
    }
}

function bindContactModal() {
    const openButton = document.querySelector("[data-open-contact]");
    const closeButtons = document.querySelectorAll("[data-close-contact-modal]");
    const form = document.getElementById("contactForm");

    openButton?.addEventListener("click", openContactModal);

    closeButtons.forEach((button) => {
        button.addEventListener("click", closeContactModal);
    });

    if (form instanceof HTMLFormElement) {
        form.addEventListener("submit", handleContactSubmit);
    }
}

function bindMaterialsModal() {
    const openButton = document.querySelector("[data-open-materials]");
    const closeButtons = document.querySelectorAll("[data-close-materials-modal]");

    openButton?.addEventListener("click", openMaterialsModal);

    closeButtons.forEach((button) => {
        button.addEventListener("click", closeMaterialsModal);
    });
}

document.addEventListener("keydown", (event) => {
    if (event.key !== "Escape") {
        return;
    }

    closeCategoryModal();
    closeMaterialsModal();
    closeContactModal();
});

document.addEventListener("DOMContentLoaded", () => {
    revealVisibleSections();
    bindCategoryModal();
    bindMaterialsModal();
    bindContactModal();
});
